from sc2.ids.ability_id import AbilityId
from sc2.unit import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade


class Morphing:
    def __init__(self, ai):
        self.ai = ai

    async def morph_gates(self):
        for gateway in self.ai.structures(unit.GATEWAY).ready:
            abilities = await self.ai.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities:
                gateway(AbilityId.MORPH_WARPGATE)

    async def morph_Archons(self, leave_n_high_templars=0):
        hts = self.ai.units().filter(lambda x: x.type_id == unit.HIGHTEMPLAR and x.is_ready and
                                               x.is_idle).sorted(lambda u: u.energy)
        if hts.amount > leave_n_high_templars + 1:

            ht2 = hts[0]
            ht1 = hts[1]
            if ht2 and ht1:
                # for ht in self.ai.army(unit.HIGHTEMPLAR):
                #     if ht.tag == ht1.tag or ht.tag == ht2.tag:
                #         self.ai.army.remove(ht)
                # queue_merge = False
                if ht1.distance_to(ht2) > 5:
                    if self.ai.attack:
                        position = await self.ai.find_placement(unit.PYLON, self.ai.game_info.map_center)

                    else:
                        position = self.ai.main_base_ramp.bottom_center.towards(
                            self.ai.main_base_ramp.top_center, -8).towards(self.ai.game_info.map_center, 20)
                    ht1.move(position)
                    ht2.move(position)

                else:
                    # print('morphing!')
                    from s2clientprotocol import raw_pb2 as raw_pb
                    from s2clientprotocol import sc2api_pb2 as sc_pb
                    command = raw_pb.ActionRawUnitCommand(
                        ability_id=AbilityId.MORPH_ARCHON.value,
                        unit_tags=[ht1.tag, ht2.tag],
                        queue_command=True
                    )
                    action = raw_pb.ActionRaw(unit_command=command)
                    await self.ai._client._execute(action=sc_pb.RequestAction(
                        actions=[sc_pb.Action(action_raw=action)]
                    ))

    async def set_wall_gates_resp_inside_base(self):
        gates = self.ai.structures().filter(lambda x: x.type_id == unit.GATEWAY and not x.is_ready
                                  and x.distance_to(self.ai.main_base_ramp.protoss_wall_buildings[0]) < 4)
        for gate in gates:
            gate.smart(gate.position.towards(self.ai.main_base_ramp.bottom_center, -4))

    async def set_second_wall_gates_resp_inside_base(self):
        gates = self.ai.structures().filter(lambda x: x.type_id == unit.GATEWAY and not x.is_ready
                                  and x.distance_to(self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -10).towards(self.ai.game_info.map_center, 8)) < 8)
        for gate in gates:
            gate.smart(gate.position.towards(self.ai.main_base_ramp.bottom_center.towards(
                    self.ai.main_base_ramp.top_center, -6), 6))