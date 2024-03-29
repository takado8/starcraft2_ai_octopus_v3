from sc2.ids.unit_typeid import UnitTypeId as unit
from sc2.ids.ability_id import AbilityId as ability
from sc2.ids.buff_id import BuffId as buff
from sc2 import Race


class NexusTrainer:
    def __init__(self, ai):
        self.ai = ai

    def probes_standard(self):
        if self.ai.can_afford(unit.PROBE):
            assimilators_amount = self.ai.structures(unit.ASSIMILATOR).amount
            workers_amount = self.ai.workers.amount + assimilators_amount
            nexuses_amount = self.ai.townhalls().amount

            if not self.ai.structures(unit.PYLON).exists and workers_amount == 14:
                return

            correct_workers_amount = (16 * nexuses_amount + 3 * assimilators_amount) + 1
            if workers_amount < correct_workers_amount and workers_amount < 86:
                chronoboosted = self.ai.townhalls().filter(lambda x: x.has_buff(buff.CHRONOBOOSTENERGYCOST) and
                                                                     x.is_idle)
                for nex in chronoboosted:
                    nex.train(unit.PROBE)
                for nexus in self.ai.structures(unit.NEXUS).ready:
                    if nexus.is_idle:
                        if workers_amount < correct_workers_amount and workers_amount < 86:
                            nexus.train(unit.PROBE)
                            workers_amount += 1
            # elif 54 < workers < 74:
            #     if self.ai.can_afford(unit.PROBE) and not self.ai.already_pending(unit.PROBE):
            #         if self.ai.structures(unit.NEXUS).idle.amount < nexuses_amount:
            #             return
            #         nexus = self.ai.structures(unit.NEXUS).ready.idle.random
            #         nexus.train(unit.PROBE)


class GateTrainer:
    def __init__(self, ai, units_training_dict=None):
        self.ai = ai
        self.units_training_dict = units_training_dict

    def zealots(self):
        if self.ai.minerals > 250 and self.ai.supply_left > 1 and self.ai.units(unit.ZEALOT).amount < 17:
            gateway = self.ai.structures(unit.GATEWAY).ready.idle
            if gateway.exists:
                gateway = gateway.random
                gateway.train(unit.ZEALOT)

    def zealots_and_sentry(self):
        def train(self, unit_):
            gateway = self.ai.structures(unit.GATEWAY).ready.idle
            if gateway.exists:
                gateway = gateway.random
                self.ai.do(gateway.train(unit_))

        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists and self.ai.units(unit.SENTRY).amount <\
                self.units_training_dict[unit.SENTRY] and self.ai.can_afford(unit.SENTRY) and not \
            self.ai.already_pending(unit.SENTRY):
            train(self, unit.SENTRY)
        if self.ai.minerals > 350 and self.ai.supply_left > 1 and self.ai.units(unit.ZEALOT).amount <\
                self.units_training_dict[unit.ZEALOT]:
            train(self, unit.ZEALOT)

    def zealots_and_stalker(self):
        gateway = self.ai.structures(unit.GATEWAY).ready.idle
        if gateway.exists:
            gateway = gateway.random
            if self.ai.structures(unit.CYBERNETICSCORE).ready.exists and self.ai.army(unit.STALKER).amount < 1 and \
                    self.ai.can_afford(unit.STALKER):
                self.ai.do(gateway.train(unit.STALKER))
            elif self.ai.minerals > 250 and self.ai.supply_left > 1 and self.ai.units(unit.ZEALOT).amount < 11:
                self.ai.do(gateway.train(unit.ZEALOT))

    def stalkers(self):
        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists:
            gateways = self.ai.structures(unit.GATEWAY).ready.idle
            for gateway in gateways:
                if self.ai.can_afford(unit.STALKER):
                    self.ai.do(gateway.train(unit.STALKER))

    def adepts_proxy(self):
        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists:
            gateways = self.ai.structures(unit.GATEWAY).ready.idle
            for gateway in gateways:
                if self.ai.can_afford(unit.ADEPT):
                    self.ai.do(gateway.train(unit.ADEPT))

    def defend_rush(self):
        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists and self.ai.can_afford(unit.STALKER):
            u = unit.STALKER
        elif self.ai.can_afford(unit.ZEALOT):
            if self.ai.enemy_race == Race.Zerg:
                amount = 3
            else:
                amount = 1
            if self.ai.army(unit.ZEALOT).amount + self.ai.already_pending(unit.ZEALOT) < amount:
                u = unit.ZEALOT
            else:
                return
        else:
            return
        gateways = self.ai.structures(unit.GATEWAY).ready.idle
        for gateway in gateways:
            if self.ai.can_afford(u):
                self.ai.do(gateway.train(u))

    def adepts_defend(self):
        if self.ai.structures(unit.CYBERNETICSCORE).ready.exists:
            if self.ai.can_afford(unit.ADEPT):
                u = unit.ADEPT
            elif self.ai.can_afford(unit.SENTRY):
                u = unit.SENTRY
            else:
                return
        elif self.ai.army(unit.ZEALOT).amount < 1:
            u = unit.ZEALOT
        else:
            return
        gateways = self.ai.structures(unit.GATEWAY).ready.idle
        for gateway in gateways:
            self.ai.do(gateway.train(u))

    def standard(self):
        gateway = self.ai.structures(unit.GATEWAY).ready
        if gateway.idle.exists:
            max_stalkers = self.units_training_dict[unit.STALKER]
            max_zealots = self.units_training_dict[unit.ZEALOT]
            max_adepts = self.units_training_dict[unit.ADEPT]
            if self.ai.can_afford(unit.STALKER) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists and \
                    self.ai.army(unit.STALKER).amount < max_stalkers:
                u = unit.STALKER
            elif self.ai.minerals > 155 and self.ai.units(unit.ZEALOT).amount < max_zealots:
                u = unit.ZEALOT
            elif self.ai.can_afford(unit.ADEPT) and self.ai.structures(unit.CYBERNETICSCORE).ready.exists and \
                    self.ai.army(unit.ADEPT).amount < max_adepts:
                u = unit.ADEPT
            else:
                return
            gateway = gateway.ready.idle.random
            self.ai.do(gateway.train(u))


class WarpgateTrainer:
    def __init__(self, ai):
        self.ai = ai

    async def standard(self, warpgate, unit_id):
        if self.ai.attack:
            prisms = self.ai.units(unit.WARPPRISMPHASING)
            if prisms.exists:
                pos = prisms.furthest_to(self.ai.start_location).position
            else:
                furthest_pylon = self.ai.structures(unit.PYLON).ready.furthest_to(self.ai.start_location.position)
                pos = furthest_pylon.position
        else:
            pos = self.ai.get_super_pylon().position
        placement = None
        i = 0
        while placement is None and i < 7:
            i += 1
            placement = await self.ai.find_placement(ability.TRAINWARP_ADEPT, near=pos.random_on_distance(5),
                                                     max_distance=5, placement_step=2, random_alternative=False)

        if placement:
            warpgate.warp_in(unit_id, placement)
        else:
            print("can't find position for warpin.")


class StargateTrainer:
    def __init__(self, ai, units_training_dict=None):
        self.ai = ai
        self.units_training_dict = units_training_dict

    def none(self):
        pass

    def carriers(self):
        oracles_amount = self.units_training_dict[unit.ORACLE]
        voidrays_amount = self.units_training_dict[unit.VOIDRAY]
        # carriers_amount = self.units_training_dict[unit.CARRIER]
        # tempests_amount = self.units_training_dict[unit.TEMPEST]

        if self.ai.structures(unit.STARGATE).ready.idle.exists:
            if self.ai.structures(unit.FLEETBEACON).ready.exists:
                carrier_amount = self.ai.army(unit.CARRIER).amount + self.ai.already_pending(unit.CARRIER)
                tempest_amount = self.ai.army(unit.TEMPEST).amount + self.ai.already_pending(unit.TEMPEST)
                voidray_amount = self.ai.army(unit.VOIDRAY).amount + self.ai.already_pending(unit.VOIDRAY)
                if self.ai.can_afford(unit.CARRIER) and carrier_amount <= tempest_amount:
                    self.ai.train(unit_type=unit.CARRIER)
                elif self.ai.can_afford(unit.TEMPEST) and tempest_amount < carrier_amount:
                    self.ai.train(unit.TEMPEST)
                elif self.ai.can_afford(unit.VOIDRAY) and carrier_amount + tempest_amount > voidray_amount < voidrays_amount:
                    self.ai.train(unit.VOIDRAY)
            elif self.ai.units(unit.ORACLE).amount < oracles_amount:
                if self.ai.can_afford(unit.ORACLE):
                    self.ai.train(unit.ORACLE)
                    self.units_training_dict[unit.ORACLE] -= 1
            elif self.ai.can_afford(unit.VOIDRAY) and self.ai.army(unit.VOIDRAY).amount < voidrays_amount:
                self.ai.train(unit.VOIDRAY)

    def voidray(self):
        if self.ai.structures(unit.STARGATE).ready.idle.exists:
            if self.ai.units(unit.ORACLE).amount < 1:
                if self.ai.can_afford(unit.ORACLE):
                    self.ai.train(unit.ORACLE)
            if self.ai.can_afford(unit.VOIDRAY):
                self.ai.train(unit.VOIDRAY)


class RoboticsTrainer:
    def __init__(self, ai, units_training_dict=None):
        self.ai = ai
        self.units_training_dict = units_training_dict

    def none(self):
        pass

    def observer(self):
        robotics = self.ai.structures(unit.ROBOTICSFACILITY).ready.idle
        if self.ai.units(unit.OBSERVER).amount + self.ai.units(unit.OBSERVERSIEGEMODE).amount < 1 and \
                self.ai.can_afford(unit.OBSERVER):
            for factory in robotics:
                factory.train(unit.OBSERVER)
                return

    def standard_new(self):
        robotics = self.ai.structures(unit.ROBOTICSFACILITY).ready.idle
        if robotics.exists:
            max_immortals = self.units_training_dict[unit.IMMORTAL]
            immortals = self.ai.units(unit.IMMORTAL)
            if self.ai.units(unit.OBSERVER).amount + self.ai.units(unit.OBSERVERSIEGEMODE).amount < 1 and \
                    self.ai.can_afford(unit.OBSERVER):
                for factory in robotics:
                    factory.train(unit.OBSERVER)
                    break
            elif self.ai.units(unit.WARPPRISMPHASING).amount + self.ai.units(unit.WARPPRISM).amount < 1 \
                    and self.ai.can_afford(unit.WARPPRISM) and not self.ai.already_pending(
                unit.WARPPRISM) and (immortals.amount > 1 or self.ai.attack):
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    factory.train(unit.WARPPRISM)
                    break
            # elif self.ai.can_afford(unit.COLOSSUS) and self.ai.supply_left > 5 and self.ai.structures(
            #         unit.ROBOTICSBAY).ready.exists \
            #         and self.ai.units(unit.COLOSSUS).amount < 3:
            #     for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
            #         self.ai.do(factory.train(unit.COLOSSUS))
            # elif self.ai.can_afford(unit.DISRUPTOR) and self.ai.supply_left > 3 and self.ai.structures(
            #         unit.ROBOTICSBAY).ready.exists \
            #         and self.ai.units(unit.DISRUPTOR).amount < 3:
            #     for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
            #         self.ai.do(factory.train(unit.DISRUPTOR))
            else:
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    if self.ai.can_afford(unit.IMMORTAL) and immortals.amount < max_immortals:
                        factory.train(unit.IMMORTAL)


    def colossus(self):
        robotics = self.ai.structures(unit.ROBOTICSFACILITY).ready.idle
        if robotics.exists:
            immortals = self.ai.units(unit.IMMORTAL)
            if self.ai.structures(unit.ROBOTICSBAY).ready.exists \
                    and self.ai.units(unit.COLOSSUS).amount < 2:
                immortals_amm = 1
            else:
                immortals_amm = 12
            if self.ai.units(unit.OBSERVER).amount + self.ai.units(unit.OBSERVERSIEGEMODE).amount < 1 and \
                    self.ai.can_afford(unit.OBSERVER):
                for factory in robotics:
                    self.ai.do(factory.train(unit.OBSERVER))
                    break
            elif self.ai.units(unit.WARPPRISMPHASING).amount + self.ai.units(unit.WARPPRISM).amount < 1 \
                    and self.ai.can_afford(unit.WARPPRISM) and not self.ai.already_pending(
                unit.WARPPRISM) and self.ai.supply_left > 2 and (immortals.amount > 0 or self.ai.attack):
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    self.ai.do(factory.train(unit.WARPPRISM))
                    break

            elif self.ai.can_afford(unit.COLOSSUS) and self.ai.supply_left > 5 and self.ai.structures(
                    unit.ROBOTICSBAY).ready.exists \
                    and self.ai.units(unit.COLOSSUS).amount < 3:
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    self.ai.do(factory.train(unit.COLOSSUS))
            # elif self.ai.can_afford(unit.DISRUPTOR) and self.ai.supply_left > 3 and self.ai.structures(
            #         unit.ROBOTICSBAY).ready.exists \
            #         and self.ai.units(unit.DISRUPTOR).amount < 3:
            #     for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
            #         self.ai.do(factory.train(unit.DISRUPTOR))
            elif self.ai.can_afford(unit.IMMORTAL) and self.ai.supply_left > 3 and self.ai.structures(
                    unit.ROBOTICSFACILITY).ready.exists \
                    and immortals.amount < immortals_amm:
                for factory in self.ai.structures(unit.ROBOTICSFACILITY).ready.idle:
                    self.ai.do(factory.train(unit.IMMORTAL))
