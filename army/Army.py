from army.attack.attack import Attack
from army.defense.defense import Defense
from army.movements import Movements
from army.status.army_status import ArmyStatus
from army.training.training import Training
from economy.info.own_economy import OwnEconomy
from .division import Division
from typing import Dict, List


class Army:
    def __init__(self, ai_object, scouting, enemy_economy, own_economy, trainer):
        self.divisions: Dict[str, Division] = {}
        self.ai = ai_object
        self.scouting = scouting
        self.defense = Defense(ai_object)
        self.attack = Attack(ai_object)
        self.army_status = ArmyStatus(ai_object)
        self.training = Training(ai_object, trainer, self.divisions)
        self.defense.assign_defend_position()
        self.enemy_economy = enemy_economy
        self.own_economy: OwnEconomy = own_economy
        self.last_print_time = 0

    async def execute(self):
        try:
            # time = int(self.ai.time)
            # if time % 5 == 0 and self.last_print_time != time:
            #     self.own_economy.print_own_economy_info()
            #     self.last_print_time = time


            self.army_status.establish_army_status()
            self.training.refresh_all_soldiers()
            training_order = self.training.create_training_order()
            self.training.order_units_training(training_order)
            await self.training.train()

            destination = None
            if self.army_status.status == ArmyStatus.ATTACKING:
                destination = self.attack.select_targets_to_attack()
                # await self.move_army(target)
            else:
                self.defense.assign_defend_position()
                self.defense.defend(self.army_status)

            await self.execute_micro(destination)
            self.defense.avoid_aoe()
            if self.attack.enemy_main_base_down:
                self.scouting.scan_on_end()
            else:
                self.scouting.scan_middle_game()
            # self.debug()
        except Exception as ex:
            self.training.debug()
            raise ex

    async def execute_micro(self, destination):
        for division in self.divisions:
            await self.divisions[division].do_micro(destination)

    def create_division(self, division_name, units_ids_dict, micros: List, movements: Movements, lifetime=None):
        if division_name in self.divisions:
            print('Division "{}" already exists.'.format(division_name))
        else:
            new_division = Division(self.ai, division_name, units_ids_dict, micros, movements, lifetime=lifetime)
            self.divisions[division_name] = new_division
            print("division created: {}".format(new_division))
            return new_division

    def print_divisions_info(self):
        for division_name in self.divisions:
            print(self.divisions[division_name])
