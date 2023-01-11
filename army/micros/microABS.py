class MicroABS:
    def __init__(self, name, ai):
        self.ai = ai
        self.name = name

    def in_grid(self, pos):
        try:
            return self.ai.in_pathing_grid(pos)
        except:
            return False

    def find_placement_for_units(self, position):
        i = 3
        while not self.ai.in_pathing_grid(position) and i < 6:
            position = position.random_on_distance(i)
            i += 1
            j = 1
            while not self.ai.in_pathing_grid(position) and j < 5:
                # print('func j: ' + str(j))
                k = 0
                while not self.ai.in_pathing_grid(position) and k < 12:
                    position = position.random_on_distance(j * 2)
                    k+=1
                j += 1
        return position if self.ai.in_pathing_grid(position) else None

    async def do_micro(self, division, target):
        raise NotImplementedError

    def __str__(self):
        return self.name