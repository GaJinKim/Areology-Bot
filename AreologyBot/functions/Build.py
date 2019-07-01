import itertools
import random

import sc2
from sc2.ids.ability_id import AbilityId as AbilID
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2

class Build:
    async def build_spawning_pool(self):
        # spawning pool costs more than 200 minerals
        if self.minerals < 200:
            return
        # get current step
        current_step = self.buildorder[self.buildorder_step]
        # need at least 200 minerals to build a spawning pool
        if self.spawning_pools.amount == 0 and (current_step == "ALLIN PHASE" or current_step == "MACRO PHASE"):
            self.pauseArmyProduction.append(False)
            self.pauseDroneProduction.append(False)

            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.SPAWNINGPOOL, position))

            self.pauseArmyProduction.append(True)
            self.pauseDroneProduction.append(False)

    async def build_roach_warren(self):
        # need at least 150 minerals to build a roach warren
        if self.minerals < 150:
            return
        # get current step
        current_step = self.buildorder[self.buildorder_step]
        # in case warren was destroyed some point after the build phase
        if self.roach_warrens.amount == 0 and (current_step == "ALLIN PHASE" or current_step == "MACRO PHASE"):
            self.pauseArmyProduction.append(False)
            self.pauseDroneProduction.append(False)

            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.ROACHWARREN, position))

            self.pauseArmyProduction.append(True)
            self.pauseDroneProduction.append(False)

    async def upgrade_to_lair(self):
        # need at least 150 minerals and 100 vespene to morph lair
        if self.minerals < 150 or self.vespene < 100 or self.hatcheries.amount < 3:
            return
        if self.lairs == 0 and self.spawning_pool_finished and self.units(UnitID.HATCHERY).idle:
            self.pauseDroneProduction.append(False)
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)

            hatch = self.units(UnitID.HATCHERY).first
            self.actions.append(hatch(AbilID.UPGRADETOLAIR_LAIR))

            self.pauseDroneProduction.append(False)
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)

    async def upgrade_to_hive(self):
        # need at least 200 minerals and 150 vespene to morph hive
        if self.minerals < 200 or self.vespene < 150 or self.hatcheries.amount < 4:
            return
        if self.hives == 0 and self.infestation_pits and self.units(UnitID.LAIR).idle:
            self.pauseDroneProduction.append(False)
            self.pauseQueenProduction.append(False)
            self.pauseArmyProduction.append(False)

            lair = self.units(UnitID.LAIR).first
            self.actions.append(lair(AbilID.UPGRADETOHIVE_HIVE))

            self.pauseDroneProduction.append(False)
            self.pauseQueenProduction.append(True)
            self.pauseArmyProduction.append(True)

    async def build_hatchery(self):
        # need at least 300 minerals to build a hatchery
        if self.minerals < 300:
            return
        self.hatch_limit = self.supply_workers / 20
        if not self.already_pending(UnitID.HATCHERY) and self.hatcheries.amount < self.hatch_limit:
            self.pauseArmyProduction.append(False)
            await self.expand_now()
            self.pauseArmyProduction.append(True)

    async def build_extractor(self):
        # need at least 25 minerals to build an extractor
        if self.minerals < 25:
            return
        for hatch in self.townhalls.ready:
            for target_vespene in self.state.vespene_geyser.closer_than(10.0, hatch):
                worker = self.select_build_worker(target_vespene)
                self.actions.append(worker.build(UnitID.EXTRACTOR, target_vespene))

    async def build_evolution_chamber(self):
        # need at least 150 minerals to build a pair of evo chambers
        if self.minerals < 150:
            return
        if self.evolution_chambers.amount < 2 and self.hatcheries.amount + self.lairs.amount >= 3:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.EVOLUTIONCHAMBER, position))
            self.pauseArmyProduction.append(True)

    async def build_hydralisk_den(self):
        # need at least 100 minerals and 100 vespene to build a hydra den
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.hydralisk_dens.amount  == 0 and self.lair_finished:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.game_info.map_center, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.HYDRALISKDEN, position))
            self.pauseArmyProduction.append(True)

    async def build_infestation_pit(self):
        # need at least 100 minerals and 100 vespene to build a infestation pit
        if self.minerals < 100 or self.vespene < 100:
            return
        if self.infestation_pits.amount and self.lair_finished and self.hydralisk_den_finished:
            self.pauseArmyProduction.append(False)
            position = self.units(UnitID.HATCHERY).ready.first.position.towards(self.main_base_ramp.depot_in_middle, 7)
            worker = self.workers.closest_to(position)
            self.actions.append(worker.build(UnitID.INFESTATIONPIT, position))
            self.pauseArmyProduction.append(True)
