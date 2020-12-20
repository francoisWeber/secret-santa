import numpy as np


def build_constraints(people, couples, other_constraints=None):
    constraints = np.identity(len(people))
    if other_constraints is not None:
        constraints += other_constraints
    for couple in couples:
        i = people.index(couple[0])
        j = people.index(couple[1])
        constraints[i, j] = 1
        constraints[j, i] = 1
    return constraints


def possibility_for(i, constraints, sender_receiver_mat):
    # people to whom i could possibly send a gift
    giftable_people_for_i = np.where(constraints[i] == 0)[0]
    # people who do not already have a gift
    giftless_people = np.where(sender_receiver_mat.sum(axis=0) == 0)[0]
    # intersection of these :
    possible_receiver_for_i = np.intersect1d(giftable_people_for_i, giftless_people)
    return possible_receiver_for_i


def assign(i, constraints, sender_2_receiver):
    possibilities_for_i = possibility_for(i, constraints, sender_2_receiver)
    # among these : try to continue the assignments
    if possibilities_for_i.size == 0:
        return None
    for j in possibilities_for_i:
        next_sender_2_receiver = np.copy(sender_2_receiver)
        next_sender_2_receiver[i][j] = 1
        if i < constraints[0].size - 1:
            new_sender_receiver_mat = assign(i + 1, constraints, next_sender_2_receiver)
            if new_sender_receiver_mat is None:
                pass
            else:
                return new_sender_receiver_mat
        else:
            return next_sender_2_receiver


def secret_santa_old(constraints):
    sender_receiver_mat = np.zeros_like(constraints)
    return assign(0, constraints, sender_receiver_mat)


def santa_roll_dices(people, couples, other_constraints=None):
    constraints = build_constraints(people, couples, other_constraints)
    return assign(0, constraints, np.zeros_like(constraints))
