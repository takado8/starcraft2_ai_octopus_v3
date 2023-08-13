from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit


async def cancel_damaged_build(ai):
    enemy = ai.enemy_units()
    if enemy.amount > 1:
        for build in ai.structures().filter(lambda x: not x.is_ready and x.type_id != unit.ORACLESTASISTRAP):
            if build.health < 50 and build.shield < 10:
                threats = enemy.filter(lambda x: x.distance_to(build) <= x.ground_range + 4 and x.can_attack_ground)
                if threats.amount > 1:
                    build(ability.CANCEL_BUILDINPROGRESS)