from bot.constants import UNITS_TO_IGNORE
from strategy.interfaces.interfaceABS import InterfaceABS
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability


class Mothership(InterfaceABS):
    TIME_WARP_RADIUS = 3.5
    CLOAKING_FIELD_RADIUS = 5

    def __init__(self, ai):
        self.ai = ai
        self.builder_tag = None

    async def execute(self):
        motherships = self.ai.units(unit.MOTHERSHIP)
        if self.ai.army({unit.CARRIER, unit.TEMPEST}).amount >= 2 and not motherships.exists:
            await self.create_mothership()
        if motherships:
            mothership = motherships.first
            enemy = self.ai.enemy_units().filter(lambda x: x.type_id not in UNITS_TO_IGNORE and x.can_attack_air
                                                 and x.distance_to(mothership) < 12)
            if enemy and mothership.energy >= 100:
                target = max(enemy, key=lambda x: enemy.closer_than(self.TIME_WARP_RADIUS, x).amount)
                if enemy.closer_than(self.TIME_WARP_RADIUS, target).amount >= 5:
                    mothership(ability.EFFECT_TIMEWARP, target.position)
                    return
            army = self.ai.army
            if army:
                army_nearby = army.closer_than(30, mothership)
                if army_nearby.amount >= 5:
                    position = max(army_nearby, key=lambda x: army_nearby.closer_than(self.CLOAKING_FIELD_RADIUS, x).amount).position
                    mothership.move(position)
                else:
                    position = max(army, key=lambda x: army.closer_than(self.CLOAKING_FIELD_RADIUS, x).amount).position
                    mothership.move(position)

    async def create_mothership(self):
        nexus = self.ai.townhalls.ready.closest_to(self.ai.start_location)
        abilities = await self.ai.get_available_abilities(nexus)
        if ability.NEXUSTRAINMOTHERSHIP_MOTHERSHIP in abilities:
            nexus(ability.NEXUSTRAINMOTHERSHIP_MOTHERSHIP)
            self.ai.global_variables['is_mothership_created'] = True