from army.micros.microABS import MicroABS
from sc2.constants import FakeEffectID
from sc2.ids.buff_id import BuffId as buff
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.position import Point2
from sc2.ids.effect_id import EffectId as effect


class SentryMicro(MicroABS):
    def __init__(self, ai, defend_position=None):
        super().__init__('SentryMicro', ai)
        self.defend_position = defend_position

    async def do_micro(self, division):
        #  Sentry region  #
        sentries = division.get_units(self.ai.iteration, unit.SENTRY)
        # sentries = self.ai.army(unit.SENTRY)
        in_position = 0
        if sentries.exists:

            guardian_shield_on = False
            for sentry in self.ai.units(unit.SENTRY):
                if sentry.has_buff(buff.GUARDIANSHIELD):
                    guardian_shield_on = True
                    break
            for eff in self.ai.state.effects:
                if not guardian_shield_on and eff.id == effect.GUARDIANSHIELDPERSISTENT:
                    guardian_shield_on = True
                    break

            for sentry in sentries:
                threats = self.ai.enemy_units().filter(
                    lambda unit_: unit_.can_attack_ground and unit_.type_id not in self.ai.units_to_ignore and
                                  unit_.distance_to(sentry.position) <= 12 and not unit_.is_hallucination)
                abilities = await self.ai.get_available_abilities(sentry)

                if self.defend_position and self.ai.enemy_units() and sentry.distance_to(self.defend_position) <= 16\
                        and self.ai.enemy_units().closer_than(5, self.defend_position):
                    force_field_in_place = False
                    if ability.FORCEFIELD_FORCEFIELD in abilities:
                        for eff in self.ai.state.effects:
                            if eff.id == FakeEffectID[unit.FORCEFIELD.value]:
                                for position in eff.positions:
                                    if self.defend_position.distance_to(position) < 1.5:
                                        force_field_in_place = True
                        if not force_field_in_place:
                            sentry(ability.FORCEFIELD_FORCEFIELD, self.defend_position)

                if threats.amount > 4 and (not guardian_shield_on) and ability.GUARDIANSHIELD_GUARDIANSHIELD in abilities:
                    sentry(ability.GUARDIANSHIELD_GUARDIANSHIELD)
                    guardian_shield_on = True
                # if ability.FORCEFIELD_FORCEFIELD in abilities and len(points) > 0:
                #     se(ability.FORCEFIELD_FORCEFIELD, points.pop(0))
                else:
                    army_nearby = self.ai.army.closer_than(30, sentry.position)
                    if army_nearby.exists:
                        in_position += 1
                        if threats.exists:
                            sentry.move(army_nearby.center.towards(threats.closest_to(sentry), -2))
                    else:
                        sentry.move(self.ai.army.filter(lambda x: x.type_id not in {unit.SENTRY, unit.HIGHTEMPLAR,
                                                 unit.WARPPRISM,unit.WARPPRISMPHASING}).closest_to(sentry))
        return in_position