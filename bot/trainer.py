from sc2 import Race
from sc2.unit import UnitTypeId
from sc2.constants import PROTOSS_TECH_REQUIREMENT
from bot.constants import BUILDING_OF_ORIGIN_DICT
from bot.trainers import WarpgateTrainer
from sc2.ids.ability_id import AbilityId as ability


class Trainer:
    def __init__(self, ai):
        self.ai = ai
        self.training_queue = []
        self.warp_gate_trainer = WarpgateTrainer(ai)

    async def train(self):
        if self.training_queue:
            i = 0
            buildings = None
            unit_id = None
            while not buildings and i < len(self.training_queue):
                unit_id = self.training_queue[i]
                i += 1
                if not self.ai.can_afford(unit_id):
                    return
                if not self.is_tech_requirement_met(unit_id):
                    unit_id = None
                    continue
                building_id = BUILDING_OF_ORIGIN_DICT[unit_id]
                buildings = self.ai.structures(building_id).ready.idle
                if building_id == UnitTypeId.GATEWAY:
                    warpgates = self.ai.structures(UnitTypeId.WARPGATE).ready.idle
                    for warpgate in warpgates:
                        abilities = await self.ai.get_available_abilities(warpgate)
                        if ability.WARPGATETRAIN_ZEALOT in abilities:
                            buildings.append(warpgate)
                            break

            if buildings and unit_id:
                building = buildings.random
                if building.type_id == UnitTypeId.WARPGATE:
                    await self.warp_gate_trainer.standard(building, unit_id)
                else:
                    building.train(unit_id)

                self.training_queue.remove(unit_id)

    def add_units_to_training_queue(self, units):
        for unit in units:
            if unit not in self.training_queue:
                self.training_queue.append(unit)

    def is_tech_requirement_met(self, unit_type):
        if self.ai.tech_requirement_progress(unit_type) < 1:
            unit_info_id = PROTOSS_TECH_REQUIREMENT[unit_type]
            print("cannot produce unit {} tech requirement is not met: {}".format(unit_type, unit_info_id))
            return False
        return True