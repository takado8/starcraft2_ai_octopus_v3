from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability


class ShieldBatteryHealBuildings(InterfaceABS):
    def __init__(self, ai):
        self.ai = ai

    async def execute(self):
        batteries = self.ai.structures(unit.SHIELDBATTERY).ready
        enemy = self.ai.enemy_units
        if batteries and enemy:
            total_energy = sum(battery.energy for battery in batteries)
            max_energy = batteries.amount * batteries.first.energy_max
            energy_percentage = total_energy / max_energy
            if energy_percentage > 0.2:
                for battery in batteries:
                    if battery.energy > 0:
                        damaged_structs = self.ai.structures().filter(lambda x: x.shield_percentage < 0.6
                                                                 and x.distance_to(battery) < 7)
                        if damaged_structs:
                            battery(ability.SMART, min(damaged_structs, key=lambda x: x.shield))
