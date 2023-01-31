import os
from sc2.main import run_replay
from sc2.observer_ai import ObserverAI


class ObserverBot(ObserverAI):
    async def on_start(self):
        pass

    async def on_step(self, iteration: int):
        # self._client.game_step = 20print(self.opponent_id)
        if iteration % 20 == 0:
            print(f"iteration: {iteration}")

            food = self.state.score.food_used_army
            sth = self.state.score.collected_minerals

            units = self.units().filter(lambda x: x.can_attack_ground and x.is_mine)
            print('food army: {}\nminerals: {}\nunits: {}'.format(food, sth, units))


if __name__ == "__main__":
    my_observer_ai = ObserverBot()
    replay_name = "a.SC2Replay"
    if os.path.isabs(replay_name):
        replay_path = replay_name
    else:
        folder_path = os.path.dirname(__file__)
        replay_path = os.path.join(folder_path, replay_name)
    assert os.path.isfile(
        replay_path
    ), "Run worker_rush.py in the same folder first to generate a replay. Then run watch_replay.py again."
    run_replay(my_observer_ai, replay_path=replay_path, realtime=True, observed_id=1, )
