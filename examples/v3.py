import itertools
from functools import reduce

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


class Event:
    def __init__(self, name, *params):
        self.name = name
        self.params = params

    def __hash__(self):
        return hash(self.name)


class BinaryRel:
    # screw efficiency!
    def __init__(self, *tuples):
        self.map = {t[0]: t[1] for t in tuples}
        self.onchange_fn = None

    def __getitem__(self, key):
        return self.map[key]

    def __setitem__(self, key, val):
        self.map[key] = val
        self._changed()

    def __iter__(self):
        yield from self.map.items()

    def onchange(self, fn):
        self.onchange_fn = fn

    def _changed(self):
        if callable(self.onchange_fn):
            self.onchange_fn()

    def __repr__(self):
        return str(self.map)


class Var:
    # Just a variable that ranges over a set/relation
    def __init__(self, target):
        self.target = target

    def __iter__(self):
        for i in self.target:
            yield i


class TupleRange:
    # Extended range that supports tuples
    def __init__(self, start, stop):
        assert len(start) == len(stop)
        self.start = start
        self.stop = stop
        self.width = len(start)

    def __iter__(self):
        it = itertools.product(
            range(self.start[i], self.end[i]) for i in range(self.width)
        )
        yield from it

    def __contains__(self, item):
        return all(
            item[i] >= self.start[i] and item[i] < self.stop[i]
            for i in range(self.width)
        )

    def __len__(self):
        return functools.reduce(
            lambda x, y: x * y,
            [self.end[i] - self.start[i] for i in range(self.width)]
        )



class Engine:
    def __init__(self):
        self.handlers = {}

    def handle(self, event, handler):
        self.handlers[event] = handler

    def do(self, event, *params):
        handler = self.handlers.get(event)
        if handler:
            handler(*params)
