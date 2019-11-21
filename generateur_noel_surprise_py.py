# coding: utf-8
import time
import tqdm
import random
import json
import os
import hashlib
import vobject
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# constants
VCARD_PATH = '/Users/fweber/Desktop/contacts-2019-11-20.vcf'
PEOPLE_PATH = './lesGens.txt'

# Data loading


def load_people(path):
    with open(path) as f:
        people_list = f.readlines()
    # separate couples and single
    individuals = []
    couples = []
    for line in people_list:
        if len(line) > 1:
            if ',' not in line:
                people_name = line.strip()
                individuals.append(people_name)
            else:
                indiv_in_couple = line.split(',')
                indiv_in_couple = [people.strip()
                                   for people in indiv_in_couple]
                individuals += indiv_in_couple
                couples.append(indiv_in_couple)
    return individuals, couples


def load_vcards(path):
    with open(path) as f:
        card_lines = f.readlines()
    vcards = []
    for line in card_lines:
        if line.startswith('BEGIN:VCARD'):
            one_vcard = line
        elif line.startswith('END:VCARD'):
            one_vcard += line
            vcards.append(vobject.readOne(one_vcard))
        else:
            one_vcard += line
    return vcards

# filtering emails


def get_key_from_vcard(vcard):
    # name
    name = vcard.fn.value.lower()
    # nickname
    try:
        nickname = vcard.nickname.value.lower()
    except AttributeError:
        nickname = ''
    # mail
    try:
        mail = vcard.email.value.lower()
    except AttributeError:
        mail = ''
    return '#'.join([name + ':' + nickname, mail])


def get_people_emails(people_list, vcard_keys):
    people2mails = {}
    for p in people_list:
        potential_mails = []
        for card_key in vcard_keys:
            if p.lower() in card_key:
                potential_mail = card_key.split('#')[1]
                if '@' in potential_mail:
                    potential_mails.append(potential_mail)
        people2mails.update({p: potential_mails})
    return people2mails


def email_checker(people_and_mails):
    people_and_mail = {}
    for name, mails in people_and_mails.items():
        if len(mails) == 0:
            user_input = input(f'No mail for {name} : provide it !\n')
            people_and_mail.update({name: user_input})
        elif len(mails) > 1:
            print(f'Ambiguous mails list for {name}. Pick one or type one!')
            for (i, mail) in enumerate(mails):
                print(f'\t{i}\t{mail}')
            user_input = input('Which one ?')
            try:
                ii = int(user_input)
                people_and_mail.update({name: mails[ii]})
            except ValueError:
                people_and_mail.update({name: user_input})
        else:
            user_input = input(
                f'Got {mails[0]} for {name} : is it OK (enter) or wrong (type correct address)?')
            if len(user_input) == 0:
                people_and_mail.update({name: mails[0]})
            else:
                people_and_mail.update({name: user_input})
    return people_and_mail


def gather_emails(people_list, vcards):
    vcard_keys = [get_key_from_vcard(vcard) for vcard in vcards]
    people2emails = get_people_emails(people_list, vcard_keys)
    return email_checker(people2emails)


# prepare gifts


def exists_gifts_among_couple(ordered_individuals, couples):
    '''
    Check if people among a couple should offer them a gift
    Given an ordered list of people and a list of couples, determines if 
    people from at least one couple are supposed to offer them a gift. If so
    the function returns True. If no couple are concerned by an 
    "auto-couple-gift", then returns False
    '''
    n_individuals = len(ordered_individuals)
    # for every couple, check the index of protagonists in ordered list
    for couple in couples:
        # who is concerned ?
        name1 = couple[0]
        name2 = couple[1]
        # what position in the proposed order ?
        index1 = ordered_individuals.index(name1)
        index2 = ordered_individuals.index(name2)
        # does they offer them anything ?
        auto_gift = ((index1 + 1) % n_individuals) == index2
        auto_gift = auto_gift or ((index2 + 1) % n_individuals) == index1
        if auto_gift:
            return True
    # if no couples or if no couple are mutually offering something : False
    return False


def pick_random_gifts(individuals, couples):
    '''Find a permutation that avoid gifts among couples
    '''
    gift_among_couple = exists_gifts_among_couple(individuals, couples)
    while gift_among_couple:
        random.shuffle(individuals)
        gift_among_couple = exists_gifts_among_couple(individuals, couples)
    return individuals


def craft_message_between(sender, receiver):
    return f'''
            {sender}, tu offres un cadeau à ... {receiver} ! <3

            Le Père Noël 🎅🏼
            '''

# emails


def get_mail_config():
    with open('./mail_config.json') as f:
        return json.load(f)


def get_connection(host, port, santas_address, santas_password):
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(santas_address, santas_password)
    return server


def fire_emails(server, mails_and_messages):
    for mail_message in tqdm.tqdm(mails_and_messages):
        msg = MIMEMultipart()
        msg['From'] = server.user
        msg['To'] = mail_message['mail']
        msg['Subject'] = "Secret Santa <3"
        msg.attach(MIMEText(mail_message['message'], 'plain'))
        server.send_message(msg)
        time.sleep(1)


def hash_and_get_output_dir(individuals, couples):
    caracteristic_to_hash = {'individuals': individuals, 'couples': couples}
    run_hash = hashlib.md5(json.dumps(
        caracteristic_to_hash).encode()).hexdigest()
    run_hash = run_hash[:5]
    return os.path.join(os.path.dirname(__file__), 'secret_santa_{}'.format(run_hash))


# load people and vcards
individuals, couples = load_people(PEOPLE_PATH)
vcards = load_vcards(VCARD_PATH)

# get their emails
people2email = gather_emails(individuals, vcards)

# compute a hash for that run
SUBDIR_PATH = hash_and_get_output_dir(individuals, couples)

# compute a permutation
ordered_people = pick_random_gifts(individuals, couples)
n_people = len(ordered_people)

# rearrange senders and receivers
mails2messages = []
for i, name in enumerate(ordered_people):
    sender = individuals[i]
    receiver = individuals[(i+1) % n_people]
    message = craft_message_between(sender, receiver)
    senders_mail = people2email.get(sender)
    mails2messages.append({'mail': senders_mail, 'message': message})

# backup
if not os.path.isdir(SUBDIR_PATH):
    os.mkdir(SUBDIR_PATH)

with open(os.path.join(SUBDIR_PATH, 'sources.json'), 'w') as f:
    json.dump(mails2messages, f, indent=2, ensure_ascii=False)

# send mails
mail_config = get_mail_config()
server = get_connection(**mail_config)
fire_emails(server, mails2messages)
