from army.division import Division


class MicroABS:
    def __init__(self, name, ai, use_division_backout_position=None):
        self.ai = ai
        self.name = name
        self.use_division_backout_position = use_division_backout_position

    def in_grid(self, pos):
        try:
            return self.ai.in_pathing_grid(pos)
        except:
            return False

    async def do_micro(self, division: Division):
        raise NotImplementedError

    def __str__(self):
        return self.name