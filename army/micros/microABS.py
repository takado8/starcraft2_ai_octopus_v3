class MicroABS:
    def __init__(self, name, ai):
        self.ai = ai
        self.name = name

    async def do_micro(self, soldiers):
        raise NotImplementedError

    def __str__(self):
        return self.name