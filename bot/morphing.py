from sc2.ids.ability_id import AbilityId
from sc2.unit import UnitTypeId as unit
from sc2.ids.upgrade_id import UpgradeId as upgrade



class Morphing:
    def __init__(self, ai):
        self.ai = ai

    async def morph_gates(self):
        for gateway in self.ai.structures(unit.GATEWAY).ready:
            abilities = await self.ai.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.ai.can_afford(AbilityId.MORPH_WARPGATE):
                self.ai.do(gateway(AbilityId.MORPH_WARPGATE))

    async def morph_Archons(self):
        if upgrade.PSISTORMTECH is self.ai.state.upgrades or self.ai.already_pending_upgrade(upgrade.PSISTORMTECH):
            archons = self.ai.army(unit.ARCHON)
            ht_amount = int(archons.amount / 2)
            ht_thresh = ht_amount + 1
        else:
            ht_thresh = 1
        if self.ai.units(unit.HIGHTEMPLAR).amount > ht_thresh:
            hts = self.ai.units(unit.HIGHTEMPLAR).sorted(lambda u: u.energy)
            ht2 = hts[0]
            ht1 = hts[1]
            if ht2 and ht1:
                for ht in self.ai.army(unit.HIGHTEMPLAR):
                    if ht.tag == ht1.tag or ht.tag == ht2.tag:
                        self.ai.army.remove(ht)
                if ht1.distance_to(ht2) > 4:
                    if ht1.distance_to(self.ai.main_base_ramp.bottom_center) > 30:
                        self.ai.do(ht1.move(ht2))
                        self.ai.do(ht2.move(ht1))
                    else:
                        self.ai.do(ht1.move(self.ai.main_base_ramp.bottom_center))
                        self.ai.do(ht2.move(self.ai.main_base_ramp.bottom_center))
                else:
                    # print('morphing!')
                    from s2clientprotocol import raw_pb2 as raw_pb
                    from s2clientprotocol import sc2api_pb2 as sc_pb
                    command = raw_pb.ActionRawUnitCommand(
                        ability_id=AbilityId.MORPH_ARCHON.value,
                        unit_tags=[ht1.tag, ht2.tag],
                        queue_command=False
                    )
                    action = raw_pb.ActionRaw(unit_command=command)
                    await self.ai._client._execute(action=sc_pb.RequestAction(
                        actions=[sc_pb.Action(action_raw=action)]
                    ))
