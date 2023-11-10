from army.attack.target_selector_attack import TargetSelectorAttack
from army.movements import Movements
from army.status.army_status import ArmyStatus
from army.training.training import Training
from .division import Division
from typing import Dict, List

# from .scouting.probe_scouting import ProbeScouting


class Army:
    def __init__(self, ai_object, scouting, enemy_economy, own_economy, trainer, defense):
        self.divisions: Dict[str, Division] = {}
        self.ai = ai_object
        self.scouting = scouting
        self.defense = defense
        self.army_status = ArmyStatus(ai_object)
        self.training = Training(ai_object, trainer, self.divisions)
        self.enemy_economy = enemy_economy
        self.own_economy = own_economy
        self.defense.assign_defend_position()
        # self.probe_scouting = ProbeScouting(ai_object)
        self.last_print_time = 0

    async def execute(self):
        try:
            time = int(self.ai.time)
            if time % 10 == 0 and self.last_print_time != time:
                self.own_economy.print_own_economy_info()
                self.enemy_economy.print_enemy_info()
                self.last_print_time = time

            self.army_status.establish_army_status()
            self.training.refresh_all_soldiers()
            training_order = self.training.create_training_order()
            self.training.order_units_training(training_order)
            await self.training.train()

            self.defense.assign_defend_position()
            if self.army_status.status == ArmyStatus.ATTACKING:
                await self.execute_micro()
            else:
                await self.execute_micro()
                self.defense.defend(self.army_status)

            self.defense.avoid_aoe()
            if self.scouting.enemy_main_base_down:
                self.scouting.scan_on_end()
            else:
                # self.probe_scouting.scout()
                await self.scouting.scan_middle_game()
            # self.debug()
        except Exception as ex:
            self.training.debug()
            raise ex

    async def execute_micro(self):
        for division in self.divisions:
            await self.divisions[division].do_micro()

    def create_division(self, division_name, units_ids_dict, micros: List, movements: Movements,
                        target_selector=None, lifetime=None):
        if division_name in self.divisions:
            print('Division "{}" already exists.'.format(division_name))
        else:
            new_division = Division(self.ai, division_name, units_ids_dict, micros, movements,
                                    target_selector=target_selector, lifetime=lifetime)
            self.divisions[division_name] = new_division
            print("division created: {}".format(new_division))
            return new_division

    def print_divisions_info(self):
        for division_name in self.divisions:
            print(self.divisions[division_name])
