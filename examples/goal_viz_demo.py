"""Visualize all goals from a specific NHL game using Edge tracking sprites.

For each goal event in the game's play-by-play, this script downloads the
player-tracking sprite JSON from wsr.nhle.com and animates it with matplotlib.

Run:  python examples\\help_goal_demo.py
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import requests
from matplotlib.widgets import Button

from nhl_analytics import NHLClient
from nhl_analytics.rink import draw_rink_markings, sprite_to_feet

DEFAULT_GAME_ID = 2026020151


def get_goal_event_ids(game_id: int) -> list[int]:
    """Return eventIds for every goal in the game via play-by-play."""
    with NHLClient() as client:
        pbp = client.endpoints.get_game_play_by_play(game_id)
    goals = [p for p in pbp.get("plays", []) if p.get("typeDescKey") == "goal"]
    return [g["eventId"] for g in goals]


def fetch_sprite_json(session: requests.Session, game_id: int, season: str, event_id: int) -> list:
    """Download one goal's tracking frames from wsr.nhle.com."""
    page_url = f"https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}/"
    json_url = f"https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json"

    # Hit the HTML page once per event for cookies/referer
    session.get(page_url, headers={"Accept": "text/html,application/xhtml+xml"})
    resp = session.get(
        json_url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nhl.com",
            "Referer": page_url,
        },
    )
    resp.raise_for_status()
    return resp.json()


def animate_goals(goals: list[dict], game_id: int):
    """Animate all goals in one window with Prev/Next buttons.

    goals: list of {"event_id": int, "frames": list}
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.subplots_adjust(bottom=0.15)  # room for buttons
    fig.patch.set_facecolor("#eaf2f8")

    # Color per team
    team_colors = {}
    palette = ["#ff5252", "#40c4ff", "#ffd740", "#69f0ae"]

    def get_color(abbrev: str) -> str:
        if abbrev not in team_colors:
            team_colors[abbrev] = palette[len(team_colors) % len(palette)]
        return team_colors[abbrev]

    # Precompute positions per goal (converted to feet from center ice)
    for g in goals:
        g["positions"] = [
            [
                {**p, "x": sprite_to_feet(p["x"], p["y"])[0],
                 "y": sprite_to_feet(p["x"], p["y"])[1]}
                for p in f.get("onIce", {}).values()
            ]
            for f in g["frames"]
        ]

    state = {"goal_idx": 0, "frame_idx": 0}

    def draw_rink_and_title():
        draw_rink_markings(ax)
        g = goals[state["goal_idx"]]
        ax.set_title(
            f"Game {game_id} — Goal {state['goal_idx'] + 1}/{len(goals)} (event {g['event_id']})",
            color="black", fontsize=14,
        )

    def update(_):
        ax.clear()
        draw_rink_and_title()

        goal = goals[state["goal_idx"]]
        positions = goal["positions"]
        i = state["frame_idx"] % len(positions)

        # Trails: every position up to the current frame per player
        trail_map = {}
        for f in positions[: i + 1]:
            for p in f:
                trail_map.setdefault(p["id"], {"team": p["teamAbbrev"], "pts": []})
                trail_map[p["id"]]["pts"].append((p["x"], p["y"]))
        for d in trail_map.values():
            pts = d["pts"]
            ax.plot([q[0] for q in pts], [q[1] for q in pts],
                    color=get_color(d["team"]), alpha=0.3, lw=1)

        for p in positions[i]:
            ax.scatter(p["x"], p["y"], c=get_color(p["teamAbbrev"]), s=140,
                       edgecolors="white", linewidths=0.6, zorder=3)

        state["frame_idx"] += 1
        return []

    def next_goal(_):
        state["goal_idx"] = (state["goal_idx"] + 1) % len(goals)
        state["frame_idx"] = 0

    def prev_goal(_):
        state["goal_idx"] = (state["goal_idx"] - 1) % len(goals)
        state["frame_idx"] = 0

    # Buttons
    ax_prev = fig.add_axes([0.25, 0.04, 0.15, 0.06])
    ax_next = fig.add_axes([0.60, 0.04, 0.15, 0.06])
    btn_prev = Button(ax_prev, "< Prev Goal")
    btn_next = Button(ax_next, "Next Goal >")
    btn_prev.on_clicked(prev_goal)
    btn_next.on_clicked(next_goal)

    anim = animation.FuncAnimation(fig, update, interval=50, blit=False)
    plt.show()
    plt.close(fig)


def main():
    game_id = int(input(f"Game ID [{DEFAULT_GAME_ID}]: ").strip() or DEFAULT_GAME_ID)
    season = input("Season (8-digit, e.g. 20262027): ").strip()
    if not season:
        # derive: game IDs start with the season's start year
        season = f"{str(game_id)[:4]}{int(str(game_id)[:4]) + 1}"

    print(f"Fetching goals for game {game_id} (season {season})...")
    event_ids = get_goal_event_ids(game_id)
    print(f"Found {len(event_ids)} goals: {event_ids}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })

    goals = []
    for i, event_id in enumerate(event_ids, 1):
        print(f"[{i}/{len(event_ids)}] Goal event {event_id}...", end=" ")
        try:
            frames = fetch_sprite_json(session, game_id, season, event_id)
        except Exception as exc:
            print(f"Failed: {exc}")
            continue
        print(f"{len(frames)} frames")
        goals.append({"event_id": event_id, "frames": frames})

    if goals:
        animate_goals(goals, game_id)
    else:
        print("No goal data to visualize.")


if __name__ == "__main__":
    main()
