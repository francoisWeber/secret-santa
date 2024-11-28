import random
from .utils import sha256
import json
import re


class Group:
    def __init__(self, people_list=None, impossible_pairs=None, forced_gift=None):
        self.people = [] if people_list is None else people_list
        self.impossible_pairs = {} if impossible_pairs is None else impossible_pairs
        self.forced_gift = forced_gift
        
    @staticmethod
    def sanitize_name(name: str) -> str:
        name = name.replace("\t", " ")
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)
        name = " ".join([part.capitalize() for part in name.split(" ")])
        return name

    def set_forced_gifts_from_str(self, forced_gift_chains):
        forced_gift = []
        for sender_and_receiver in forced_gift_chains:
            sender, receiver = sender_and_receiver.split(":")
            sender = self.sanitize_name(sender)
            receiver = self.sanitize_name(receiver)
            if f"{sender}-{receiver}" in self.impossible_pairs:
                raise ValueError(
                    f"Impossible ! {sender} et {receiver} ne peuvent pas être forcés et exclus !"
                )
            print("Forced gift from", sender, "to", receiver)
            forced_gift += [(sender, receiver)]
        self.forced_gift = forced_gift

    def sample_chain(self):
        people_chain = None
        if self.forced_gift:
            meta_chain = []
            people = self.people.copy()
            for (sender, receiver) in self.forced_gift:
                people.pop(people.index(sender))
                people.pop(people.index(receiver))
                meta_chain.append([sender, receiver])
            meta_chain += [[single_guy] for single_guy in people]
            while not self.is_chain_valid(people_chain):
                random.shuffle(meta_chain)
                people_chain = [people for meta_el in meta_chain for people in meta_el]
        else:
            while not self.is_chain_valid(people_chain):
                people_chain = self.people.copy()
                random.shuffle(people_chain)
        return people_chain

    @classmethod
    def load(cls, path):
        people = set()
        impossible_pairs = set()
        with open(path) as f:
            people_or_groups = [a.strip() for a in f.readlines()]

        for p_or_c in people_or_groups:
            one_line_of_people = p_or_c.split(",")
            one_line_of_people = [Group.sanitize_name(pp) for pp in one_line_of_people]
            people.update(one_line_of_people)  # update the set
            if len(one_line_of_people) > 1:
                for p1 in one_line_of_people:
                    for p2 in one_line_of_people:
                        impossible_pairs.update([f"{p1}-{p2}"])
        people = sorted(list(people))
        return cls(people_list=people, impossible_pairs=impossible_pairs)

    def _pair_is_impossible(self, p1, p2):
        return f"{p1}-{p2}" in self.impossible_pairs

    def is_chain_valid(self, people_chain):
        if people_chain is None:
            return False
        n_people = len(people_chain)
        for i in range(n_people):
            sender = people_chain[i]
            receiver = people_chain[(i + 1) % n_people]
            if self._pair_is_impossible(sender, receiver):
                return False
        return True

    def __str__(self) -> str:
        return json.dumps({"people": self.people, "couples": self.impossible_pairs})

    def name(self):
        return f"group-{sha256(self.people, sorted(list(self.impossible_pairs)))[:8]}"
