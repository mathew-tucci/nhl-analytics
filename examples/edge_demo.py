"""Example: NHL Edge player-tracking requests for a player entered at runtime.

Run:  python examples\\edge_demo.py
"""

import json

from nhl_analytics import NHLClient


def show(title: str, data, max_chars: int = 800):
    """Print a compact preview of an API response."""
    print(f"\n=== {title} ===")
    text = json.dumps(data, indent=2) if not isinstance(data, str) else data
    print(text[:max_chars] + ("\n... (truncated)" if len(text) > max_chars else ""))


def main():
    player_id = int(input("Player ID (e.g. 8478402 for McDavid): ").strip())
    season = input("Season (8-digit like 20252026, or 'now') [now]: ").strip() or "now"

    with NHLClient(api="web") as client:
        # 1. Base detail: bio + percentile stats vs league average
        show("skater_detail", client.edge.skater_detail(player_id, season))

        # # 2. Shot speed analytics (max speed, average speed, attempt buckets)
        # show("skater_shot_speed_detail", client.edge.skater_shot_speed_detail(player_id, season))

        # # 3. Skating speed metrics (burst counts, max speed)
        # show("skater_skating_speed_detail", client.edge.skater_skating_speed_detail(player_id, season))

        # # 4. Shot location patterns and heat maps
        # show("skater_shot_location_detail", client.edge.skater_shot_location_detail(player_id, season))

        # # 5. Distance traveled per game and per shift
        # show("skater_skating_distance_detail", client.edge.skater_skating_distance_detail(player_id, season))

        # # 6. Comparison data vs league averages
        # show("skater_comparison", client.edge.skater_comparison(player_id, season))

        # # 7. Time spent in each zone (offensive/defensive/neutral)
        # show("skater_zone_time", client.edge.skater_zone_time(player_id, season))


if __name__ == "__main__":
    main()
