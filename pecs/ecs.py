UPPER_32_BITS = (2 ** 32 - 1) << 32
LOWER_32_BITS = (2 ** 32 - 1)


class EntityType:
    # A "base type" of entities.
    def __init__(self, world, name, typeid):
        self.world = world
        self.name = name
        self.typeid = typeid
        self._next_id = 0

    def new(self) -> int:
        entity = (self.typeid << 32) | self._next_id
        self._next_id += 1
        self.world.new_entity(entity)
        return entity


class Component:
    # A relation from entities of type `entity_type` to `datatype` (which can also be an entity type id)
    # Assuming a dense relation, aka non-nullable, using entity IDs as direct indices
    def __init__(self, world, name, entity_type, datatype):
        self.world = world
        self.name = name
        self.entity_type = entity_type
        self.datatype = datatype
        self.data = []

    def __setitem__(self, key, val):
        entity_id = (key & LOWER_32_BITS)
        #if entity_id > len(self.data):
            # extend self.data to entity_id
        self.data[entity_id] = val

    def __getitem__(self, key):
        entity_id = (key & LOWER_32_BITS)
        return self.data[entity_id]

    def __iter__(self):
        yield from self.data

    def iter_with_ids(self):
        for i, val in enumerate(self.data):
            entity_id = (self.entity_type << 32) | i
            yield (entity_id, val)


class World:
    def __init__(self):
        self._next_type_id = 1
        self.entities = []
        self.entity_types = [None]  # Starts with a dummy entity type for Entity.

    def new_type(self, name):
        typ = EntityType(self, name, self._next_type_id)
        self._next_type_id += 1
        self.entity_types.append(typ)
        return typ

    def new_entity(self, entity):
        self.entities.append(entity)
        self.entities.sort()

    def typeof(self, entity):
        typeid = (entity & UPPER_32_BITS) >> 32
        return self.entity_types[typeid]


def main():
    world = World()
    dog = world.new_type("dog")
    cat = world.new_type("cat")
    person = world.new_type("person")

    fatou = cat.new()
    wizzy = cat.new()
    kitty = cat.new()
    bob = person.new()
    fido = dog.new()
    rex = dog.new()

    print(fatou, wizzy, kitty)
    print(fido, rex)

    print(world.typeof(fatou).name)
    print(world.typeof(rex).name)

    print(world.entities)


if __name__ == "__main__":
    main()
