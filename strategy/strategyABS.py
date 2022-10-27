class StrategyABS:
    def __init__(self, type, name):
        self.type = type
        self.name = name


    # =======================================================  Builders
    async def build_from_queue(self):
        raise NotImplementedError

    async def build_pylons(self):
        raise NotImplementedError

    def build_assimilators(self):
        raise NotImplementedError

    # =======================================================  Upgraders
    def forge_upgrade(self):
        raise NotImplementedError

    def cybernetics_upgrade(self):
        raise NotImplementedError

    async def twilight_upgrade(self):
        raise NotImplementedError

    # =======================================================  Trainers
    async def train_units(self):
        raise NotImplementedError

    def train_probes(self):
        raise NotImplementedError

    # =======================================================  Army

    async def army_do_micro(self):
        raise NotImplementedError



    # ======================================================= Conditions
    def attack_condition(self):
        raise NotImplementedError

    def retreat_condition(self):
        raise NotImplementedError

    def counter_attack_condition(self):
        raise NotImplementedError

    # ======================================================== Buffs
    def chronoboost(self):
        raise NotImplementedError
