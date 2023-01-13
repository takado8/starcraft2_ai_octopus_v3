from sc2.unit import Unit


class Soldier:
    def __init__(self, unit: Unit, division_name=None):
        self.unit: Unit = unit
        self.division_name = division_name

    @property
    def tag(self):
        return self.unit.tag

    @property
    def type_id(self):
        return self.unit.type_id

    def __eq__(self, other):
        if not isinstance(other, Soldier):
            print('(other) object of type \'{}\' is not comparable with object of type \'{}\''.format(type(other),
                                                                                                      type(self)))
            raise TypeError
        return self.tag == other.tag

    def __str__(self):
        return "Soldier(tag={}, type_id={})".format(self.tag, self.type_id)

    def __repr__(self):
        return str(self)