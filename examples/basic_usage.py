"""Example: fetch today's scores and team standings."""

from nhl_analytics import NHLClient


def main():
    with NHLClient() as client:
        # Today's scores
        scores = client.endpoints.get_score_today()
        for date in scores.get("gameWeek", []):
            for game in date.get("games", []):
                away = game["awayTeam"]["abbrev"]
                home = game["homeTeam"]["abbrev"]
                state = game["gameState"]
                print(f"{away} @ {home} — {state}")

        # Standings
        teams = client.endpoints.get_teams()
        print(f"\n{len(teams)} teams in the league")

        # Raw access to any endpoint
        raw = client.get("/standings/now")
        print(f"Raw standings keys: {list(raw.keys())}")


if __name__ == "__main__":
    main()
