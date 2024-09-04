import os
import sc2reader
import time
from dotenv import load_dotenv

load_dotenv()

REPLAY_LIMIT = int(os.getenv('REPLAY_LIMIT', 100))
REPLAY_FOLDER = os.getenv('REPLAY_FOLDER')
PLAYER = os.getenv('PLAYER')

def main():
    replay_folder = REPLAY_FOLDER
    replays_data = collect_replays_data(replay_folder)
    stats = calc_stats(replays_data, PLAYER)

    print(f"\nStats for {stats["player"]}:")
    counter = 0
    for key, stat in stats["opponents"].items():
        if counter > 100:
            break
        print(f"player: {key.ljust(20)} played: {stat["played"]} win: {stat["win"]} loss:{stat["loss"]} winRatio: {format(stat["winRatio"],".0%")} ")
        counter += 1


def parse_replay(replay_file):
    replay = sc2reader.load_replay(replay_file)

    if len(replay.players) != 2:
        return None
    
    if replay.winner is None:
        return None

    replay_info = {
        "player1": replay.players[0].name,
        "player2": replay.players[1].name,
        "race1": replay.teams[0].lineup,
        "race2": replay.teams[1].lineup,
        "duration": replay.game_length.total_seconds(),
        "winner": replay.winner.players[0].name,
    }

    return replay_info

def collect_replays_data(replay_folder):
    replays_data = []

    print(f"Parsing folder for replays: {replay_folder}")
    start = time.time()
    counter = 0
    skipped = 0

    for filename in os.listdir(replay_folder):
        if filename.endswith('.SC2Replay'):
            replay_file = os.path.join(replay_folder, filename)
            replay_info = parse_replay(replay_file)
            if replay_info is not None:
                replays_data.append(replay_info)
            else:
                    skipped += 1
            counter += 1
        
        if counter > REPLAY_LIMIT:
            break

        if counter % 100 == 0:
            print (f"Scanned: {counter} skipped: {skipped} ({round(time.time()-start)} s)")

    return replays_data

def calc_stats(replay_data, playerFocus):
    stats = {}
    stats["player"] = playerFocus
    stats["opponents"] = {}
    for replay in replay_data:
        opponent = replay["player1"] if replay["player1"] != playerFocus else replay["player2"]
        if not opponent in stats["opponents"]:
            stats["opponents"][opponent] = {"win": 0, "loss": 0, "played": 0}
        
        if replay["winner"] == playerFocus:
            stats["opponents"][opponent]["win"] += 1
        else:
            stats["opponents"][opponent]["loss"] += 1
        
        stats["opponents"][opponent]["played"] += 1

        played = stats["opponents"][opponent]["played"]
        wins = stats["opponents"][opponent]["win"]
        winRatio = wins/played

        stats["opponents"][opponent]["winRatio"] = round(winRatio, 2)

    sorted_opponents = dict(sorted(stats["opponents"].items(), key=lambda item: item[1]['played']*-1))
    stats["opponents"] = sorted_opponents
    return stats

if __name__ == "__main__":
    main()
