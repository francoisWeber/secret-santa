from .utils import sha256
import json


class Group:
    def __init__(self, people_list=None, impossible_pairs=None):
        self.people = [] if people_list is None else people_list
        self.impossible_pairs = {} if impossible_pairs is None else impossible_pairs

    @classmethod
    def load(cls, path):
        people = set()
        impossible_pairs = set()
        with open(path) as f:
            people_or_groups = [a.strip() for a in f.readlines()]

        for p_or_c in people_or_groups:
            one_line_of_people = p_or_c.split(",")
            one_line_of_people = [pp.strip().capitalize() for pp in one_line_of_people]
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
