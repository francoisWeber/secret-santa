# coding: utf-8
import random
import json
import os
import hashlib


def load_people(path='./lesGens.txt'):
    with open(path) as f:
        people_list = f.readlines()
    # separate couples and single
    individuals = []
    couples = []
    for line in people_list:
        if ',' not in line:
            people_name = line.strip()
            individuals.append(people_name)
        else:
            indiv_in_couple = line.split(',')
            indiv_in_couple = [people.strip() for people in indiv_in_couple]
            individuals += indiv_in_couple
            couples.append(indiv_in_couple)
    return individuals, couples


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


# Import list of people ...
# with open('lesGens.json') as f:
#     individuals = json.load(f)
# n_individuals = len(individuals)

# with open('lesCouples.json') as f:
#     couples = json.load(f)

individuals, couples = load_people()
n_individuals = len(individuals)

# Save a short hash that characterizes that run :
caracteristic_to_hash = {'individuals': individuals, 'couples': couples}
run_hash = hashlib.md5(json.dumps(caracteristic_to_hash).encode()).hexdigest()
run_hash = run_hash[:5]

# sample trials until no one in a couple has to offer a gift to his/her +1 :
gift_among_couple = exists_gifts_among_couple(individuals, couples)
while gift_among_couple:
    random.shuffle(individuals)
    gift_among_couple = exists_gifts_among_couple(individuals, couples)

# We've found a permutation that avoids auto-couple-gift
# Make a sub directory
# caracteristics of that run :
m = hashlib.md5().hexdigest()
SUBDIR_PATH = os.path.join(os.path.dirname(
    __file__), 'secret_santa_{}'.format(run_hash))
if not os.path.isdir(SUBDIR_PATH):
    os.mkdir(SUBDIR_PATH)

# And write results file down
for i in range(n_individuals):
    sender = individuals[i]
    receiver = individuals[(i+1) % n_individuals]

    with open(os.path.join(SUBDIR_PATH, '{}.txt'.format(sender)), 'w') as f:
        f.write('{}, tu offres un cadeau à {} :)'.format(sender, receiver))
