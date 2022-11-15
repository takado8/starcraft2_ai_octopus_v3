from army.army import Army
from army.scouting.scouting import Scouting
from bot.conditions import ConditionAttack, ConditionCounterAttack, ConditionRetreat, ConditionLockSpending
from bot.nexus_abilities import Chronobooster
from bot.trainer import Trainer
from bot.trainers import NexusTrainer
from builders import PylonBuilder, AssimilatorBuilder
from economy.info.enemy_economy import EnemyEconomy
from economy.info.own_economy import OwnEconomy
from economy.workers.distribute_workers import DistributeWorkers


class StrategyABS:
    def __init__(self, type, name, ai):
        self.type = type
        self.name = name
        self.ai = ai
        self.own_economy = OwnEconomy(ai)
        self.enemy_economy = EnemyEconomy(ai)
        self.scouting = Scouting(ai, self.enemy_economy)
        self.trainer = Trainer(ai)
        self.army = Army(ai, self.scouting, self.trainer)

        self.pylon_builder = PylonBuilder(ai)
        self.assimilator_builder = AssimilatorBuilder(ai)
        self.nexus_trainer = NexusTrainer(ai)

        self.condition_attack = ConditionAttack(ai)
        self.condition_counter_attack = ConditionCounterAttack(ai)
        self.condition_retreat = ConditionRetreat(ai)
        self.condition_lock_spending = ConditionLockSpending(ai)

        self.chronobooster = Chronobooster(ai)
        self.workers_distribution = DistributeWorkers(ai)


    def distribute_workers(self):
        raise NotImplementedError

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
    def train_probes(self):
        raise NotImplementedError

    # =======================================================  Army
    def army_execute(self):
        raise NotImplementedError

    # ======================================================= Conditions
    def attack_condition(self):
        raise NotImplementedError

    def retreat_condition(self):
        raise NotImplementedError

    def counter_attack_condition(self):
        raise NotImplementedError

    async def lock_spending_condition(self):
        raise NotImplementedError

    # ======================================================== Buffs
    def chronoboost(self):
        raise NotImplementedError

    async def morphing(self):
        raise NotImplementedError