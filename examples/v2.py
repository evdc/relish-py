from collections import defaultdict

########################################################################################################################
# Inspired by https://eblong.com/zarf/essays/rule-based-if/, among others.
#
# NOTES
# - instead of merging sets on constructing a new RuleCase pattern you could do a recursive call in match()
#   (but that's not very ECS of you)
# - if "entity type rules" like Treasure, Living only ever return True/False they're basically just glorified sets
#   of entity ids aka components / unary relations in other models and so instead of them needing to define a True
#   case and a False case, can just have one set of entity IDs for the whole rule
#   - this is not generally true: a rule like Treasure *may* want different price bands for different sets of entities
#     and it loses you some flexibility: what if you want to say "this is True for entities 1,2,3; False for 4,5,6;
#     and undefined (or 42, or anything) for everyone else" ??? but it makes implementing easier
#     a pure (non-ecs, not-cached) rule engine as in the example above won't stop you from doing this
#
#
########################################################################################################################


class Entities:
    # super primitive entity allocator that isn't even generational
    def __init__(self):
        self.next_id = 0

    def new(self):
        i = self.next_id
        self.next_id += 1
        return Entity(i)


class Entity:
    # wrapper to make things a little clearer, and way less efficient
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Entity) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "<{}>".format(self.id)


class RuleCase:
    def __init__(self, name, action, pattern):
        # `action` may be a callable, or any other object;
        # if it's not a callable, it will be turned into a callable which returns that object
        self.name = name
        self._action = action
        self.pattern = pattern
        self.deps = []

    def action(self, *args):
        if callable(self._action):
            return self._action(*args)
        return self._action

    def __repr__(self):
        return "<RuleCase {} as {} if {}>".format(self.name, self._action, self.pattern)


class Rule:
    def __init__(self, name, cases=None):
        self.name = name
        self.cases = cases or []

    def add_case(self, case):
        # Unify this case with the existing cases
        for c in self.cases:
            if c._action == case._action:
                c.pattern.merge(case.pattern)
                break
        else:
            self.cases.append(case)

    def __repr__(self):
        return "<Rule {}>".format(self.name)


class Wildcard:
    def __repr__(self):
        return "_"


_ = Wildcard()


class Pattern:
    # A Pattern can store a set of all entity IDs matching it
    # the Pattern ctor could return concrete implementations of like,
    # WildcardPattern, EntityPattern, RulePattern, ...

    def __init__(self, engine, target):
        self.eng = engine
        self.target = target
        self.entities = set()
        self.deps = set()

        if isinstance(target, Entity):
            self.entities.add(target)

    def merge(self, other: 'Pattern'):
        self.entities.update(other.entities)

    def match(self, arg):
        if isinstance(self.target, Wildcard):
            return True
        if isinstance(self.target, Rule):
            # this isn't great bc you apply the rule (potentially having side effects)
            # just to test if there's a match
            return self.eng.apply_rule(self.target.name, arg)
        return arg in self.entities

    def __repr__(self):
        return str(self.target)


class Engine:
    def __init__(self):
        self.rules = {}
        self.vars = {}

    def add_rule(self, name, pattern, action):
        rule = None
        rc = RuleCase(name, action, Pattern(self, pattern))
        if name in self.rules:
            rule = self.rules[name]
            rule.add_case(rc)
        else:
            rule = Rule(name, [rc])
            self.rules[name] = rule
        return rule

    def apply_rule(self, name, *args):
        print("Apply {} to {}".format(name, args))
        rule = self.rules[name]
        # we are very dumb and just do last-defined-rule-wins
        for case in reversed(rule.cases):
            if case.pattern.match(*args):
                return case.action(*args)
        raise Exception("No cases matched rule {} for args {}".format(name, args))

    def all_rule_cases(self):
        for rule in self.rules.values():
            for rc in rule.cases:
                yield rc


def main():
    entities = Entities()
    eng = Engine()

    player = entities.new()
    monster = entities.new()
    rock = entities.new()
    treasure = entities.new()
    treasure2 = entities.new()

    eng.add_rule("Living", _, False)
    eng.add_rule("Living", player, True)
    eng.add_rule("Living", monster, True)

    Treasure = eng.add_rule("Treasure", _, False)
    eng.add_rule("Treasure", treasure, True)

    # do Price(_) as 0
    eng.add_rule("Price", _, 0)
    # do Price(x) as 10 if Treasure(x)
    eng.add_rule("Price", Treasure, 10)


    for rc in eng.all_rule_cases():
        print(rc.name, rc.pattern.entities, rc._action)

    print(eng.apply_rule("Living", monster))
    print(eng.apply_rule("Living", rock))
    print(eng.apply_rule("Price", monster))
    print(eng.apply_rule("Treasure", treasure))
    print(eng.apply_rule("Price", treasure))


if __name__ == "__main__":
    main()
