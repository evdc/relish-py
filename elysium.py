from collections import defaultdict


class Entities:
    # super primitive entity allocator that isn't even generational
    def __init__(self):
        self.next_id = 0

    def new(self):
        i = self.next_id
        self.next_id += 1
        return i


class RuleCase:
    def __init__(self, name, action, pattern):
        self.name = name
        self.action = action
        self.pattern = pattern
        self.deps = []

    def __repr__(self):
        return "<Rule {} as {} if {}>".format(self.name, self.action, self.pattern)


class Wildcard:
    def __eq__(self, other):
        return True

    def __repr__(self):
        return "_"


_ = Wildcard()


class Pattern:
    def __init__(self, engine, target):
        self.eng = engine
        self.target = target

    def match(self, arg):
        if isinstance(self.target, RuleCase):
            return self.eng.apply_rule(self.target.name, arg)
        else:
            return self.target == arg

    def __repr__(self):
        return str(self.target)


class Engine:
    def __init__(self):
        self.rule_cases = defaultdict(list)
        self.vars = {}

    def add_rule(self, name, pattern, action):
        rc = RuleCase(name, action, Pattern(self, pattern))
        if isinstance(pattern, RuleCase):   # duplicated check
            rc.deps.append(pattern)
        self.rule_cases[name].append(rc)
        print(rc)
        return rc

    def apply_rule(self, name, *args):
        cases = self.rule_cases[name]
        # we are very dumb and just do last-defined-rule-wins
        for case in reversed(cases):
            if case.pattern.match(*args):
                return case.action(*args)
        raise Exception("No cases matched rule {} for args {}".format(name, args))

    def all_rule_cases(self):
        for rcs in self.rule_cases.values():
            for rc in rcs:
                yield rc


def main():
    entities = Entities()
    eng = Engine()

    player = entities.new()
    monster = entities.new()
    rock = entities.new()
    treasure = entities.new()

    # do Living(_) as False
    eng.add_rule("Living", lambda _: False, lambda _: True)
    # do Living(player) as True
    eng.add_rule("Living", lambda _: True, lambda x: x == player)
    eng.add_rule("Living", lambda _: True, lambda x: x == monster)

    eng.add_rule("Treasure", lambda _: False, lambda _: True)
    eng.add_rule("Treasure", lambda _: True, lambda x: x == treasure)

    # do Price(_) as 0
    eng.add_rule("Price", lambda _: 0, lambda _: True)
    # do Price(x) as 10 if Treasure(x)
    eng.add_rule("Price", lambda _: 10, lambda x: eng.apply_rule("Treasure", x))

    # we'd prefer this syntax:
    # Price[lambda _: True] = 0
    # Price[lambda x: Treasure[x]] = 10
    # or without lambdas, and _ defined as an implicit var:
    # Price[True] = 0
    # Price[Treasure[_]] = 10
    # or even:
    # Price[_] = 0
    # Price[Treasure] = 10

    print(eng.apply_rule("Living", player))
    print(eng.apply_rule("Living", rock))
    print(eng.apply_rule("Price", monster))
    print(eng.apply_rule("Price", treasure))

def test2():
    entities = Entities()
    eng = Engine()

    player = entities.new()
    monster = entities.new()
    rock = entities.new()
    treasure = entities.new()

    eng.add_rule("Living", _, lambda _: False)
    eng.add_rule("Living", player, lambda _: True)
    eng.add_rule("Living", monster, lambda _: True)

    Treasure = eng.add_rule("Treasure", _, lambda _: False)
    eng.add_rule("Treasure", treasure, lambda _: True)

    # do Price(_) as 0
    eng.add_rule("Price", _, lambda _: 0)
    # do Price(x) as 10 if Treasure(x)
    eng.add_rule("Price", Treasure, lambda _: 10)


    print(eng.apply_rule("Living", player))
    print(eng.apply_rule("Living", rock))
    print(eng.apply_rule("Price", monster))
    print(eng.apply_rule("Price", treasure))

    for rc in eng.all_rule_cases():
        print(rc.name, rc.deps)

if __name__ == "__main__":
    test2()
