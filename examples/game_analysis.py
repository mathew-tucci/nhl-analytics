"""Example: pull a game boxscore and play-by-play into pandas."""

import pandas as pd

from nhl_analytics import NHLClient

GAME_ID = 2025020001  # replace with a real game ID


def main():
    with NHLClient() as client:
        boxscore = client.endpoints.get_game_boxscore(GAME_ID)

        # Player stats -> DataFrame
        players = []
        for team in boxscore.get("playerByGameStats", {}).get("homeTeam", {}).get("forwards", []):
            players.append(team)
        df = pd.json_normalize(players)
        print(df.head())

        # Play-by-play events
        pbp = client.endpoints.get_game_play_by_play(GAME_ID)
        events = pbp.get("plays", [])
        print(f"{len(events)} plays recorded")


if __name__ == "__main__":
    main()
