from army.micros.microABS import MicroABS
from sc2.constants import FakeEffectID
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2
from sc2.ids.effect_id import EffectId as effect


class SentryMicro(MicroABS):
    def __init__(self, ai):
        super().__init__('SentryMicro', ai)

    async def do_micro(self, division):
        #  Sentry region  #
        sentries = division.get_units(self.ai.iteration, unit.SENTRY)
        # sentries = self.ai.army(unit.SENTRY)
        in_position = 0
        if sentries.exists:
            m = -1
            sentry = None
            for se in sentries:
                close = sentries.closer_than(7, se.position).amount
                if close > m:
                    m = close
                    sentry = se
            force_fields = []
            guardian_shield_on = False
            for eff in self.ai.state.effects:
                if eff.id == FakeEffectID.get(unit.FORCEFIELD.value):
                    force_fields.append(eff)
                elif not guardian_shield_on and eff.id == effect.GUARDIANSHIELDPERSISTENT:
                    guardian_shield_on = True
            threats = self.ai.enemy_units().filter(
                lambda unit_: unit_.can_attack_ground or unit_.can_attack_air and unit_.distance_to(sentry.position) <= 9 and
                              unit_.type_id not in self.ai.units_to_ignore and unit_.type_id not in self.ai.workers_ids
            and not unit_.is_hallucination)
            if not threats:
                in_position += 1
            has_energy_amount = sentries.filter(lambda x2: x2.energy >= 50).amount
            points = []

            if has_energy_amount > 0 and len(
                    force_fields) < 5 and threats.amount > 4:  # and self.ai.time - self.ai.force_field_time > 1:
                enemy_army_center = threats.center.towards(sentry, -1)
                gap = 3
                points.append(enemy_army_center)
                points.append(Point2((enemy_army_center.x - gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x + gap, enemy_army_center.y)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y - gap)))
                points.append(Point2((enemy_army_center.x, enemy_army_center.y + gap)))
            for se in self.ai.units(unit.SENTRY):
                abilities = await self.ai.get_available_abilities(se)
                if threats.amount > 4 and not guardian_shield_on and ability.GUARDIANSHIELD_GUARDIANSHIELD in abilities \
                        and se.distance_to(threats.closest_to(se).position) < 7:
                    se(ability.GUARDIANSHIELD_GUARDIANSHIELD)
                    guardian_shield_on = True
                if ability.FORCEFIELD_FORCEFIELD in abilities and len(points) > 0:
                    se(ability.FORCEFIELD_FORCEFIELD, points.pop(0))
                else:
                    army_nearby = self.ai.army.closer_than(9, se.position)
                    if army_nearby.exists:
                        if threats.exists:
                            se.move(army_nearby.center.towards(threats.closest_to(se), -2))
        return in_position