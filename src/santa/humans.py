# import vobject

from hashlib import sha256
from os import path as osp
import os


class SendersList:
    def __init__(self, people, gift_matrix, vcards) -> None:
        self.senders = []
        self.sha256 = sha256((str(people) + str(gift_matrix)).encode()).hexdigest()
        if vcards is not None:
            pass
        else:
            for i, sender in enumerate(people):
                j = gift_matrix[i].argmax()
                receiver = people[j]
                self.senders.append(Sender(sender, receiver, email=None))

    def stdout(self):
        for sender in self.senders:
            sender.stdout()

    def fire_email(self):
        for sender in self.senders:
            sender.fire_email()

    def dump(self):
        dump_dir = osp.join(".", f"secret_santa_{self.sha256[:8]}")
        try:
            os.mkdir(dump_dir)
        except FileExistsError as e:
            print("Same run already computed")
        for sender in self.senders:
            dump_path = osp.join(dump_dir, f"infos_pour_{sender.name}")
            sender.dump(dump_path)


class Sender:
    def __init__(self, name, target, email):
        self.name = name
        self.target = target
        self.email = email

    def get_message(self):
        return f"""{self.name}, tu offres un cadeau à ... {self.target} ! <3
    Le Père Noël 🎅🏼
            """

    def stdout(self):
        print(self.get_message())

    def fire_email(self):
        pass

    def dump(self, path):
        with open(path, "w") as f:
            f.write(self.get_message())


def load_people(path):
    with open(path) as f:
        people_list = f.readlines()
    # separate couples and single
    individuals = []
    couples = []
    for line in people_list:
        if len(line) > 1:
            if "," not in line:
                people_name = line.strip()
                individuals.append(people_name)
            else:
                indiv_in_couple = line.split(",")
                indiv_in_couple = [people.strip() for people in indiv_in_couple]
                individuals += indiv_in_couple
                couples.append(indiv_in_couple)
    return individuals, couples


def load_vcards(path):
    with open(path) as f:
        card_lines = f.readlines()
    vcards = []
    one_vcard = ""
    for line in card_lines:
        if line.startswith("BEGIN:VCARD"):
            one_vcard = line
        elif line.startswith("END:VCARD"):
            one_vcard += line
            vcards.append(vobject.readOne(one_vcard))
        else:
            one_vcard += line
    return vcards


def get_key_from_vcard(vcard):
    # name
    name = vcard.fn.value.lower()
    # nickname
    try:
        nickname = vcard.nickname.value.lower()
    except AttributeError:
        nickname = ""
    # mail
    try:
        mail = vcard.email.value.lower()
    except AttributeError:
        mail = ""
    return "#".join([name + ":" + nickname, mail])


def get_people_emails(people_list, vcard_keys):
    people2mails = {}
    for p in people_list:
        potential_mails = []
        for card_key in vcard_keys:
            if p.lower() in card_key:
                potential_mail = card_key.split("#")[1]
                if "@" in potential_mail:
                    potential_mails.append(potential_mail)
        people2mails.update({p: potential_mails})
    return people2mails


def email_checker(people_and_mails):
    people_and_mail = {}
    for name, mails in people_and_mails.items():
        if len(mails) == 0:
            user_input = input(f"No mail for {name} : provide it !\n")
            people_and_mail.update({name: user_input})
        elif len(mails) > 1:
            print(f"Ambiguous mails list for {name}. Pick one or type one!")
            for (i, mail) in enumerate(mails):
                print(f"\t{i}\t{mail}")
            user_input = input("Which one ?")
            try:
                ii = int(user_input)
                people_and_mail.update({name: mails[ii]})
            except ValueError:
                people_and_mail.update({name: user_input})
        else:
            user_input = input(
                f"Got {mails[0]} for {name} : is it OK (enter) or wrong (type correct address)?"
            )
            if len(user_input) == 0:
                people_and_mail.update({name: mails[0]})
            else:
                people_and_mail.update({name: user_input})
    return people_and_mail


def gather_emails(people_list, vcards):
    vcard_keys = [get_key_from_vcard(vcard) for vcard in vcards]
    people2emails = get_people_emails(people_list, vcard_keys)
    return email_checker(people2emails)