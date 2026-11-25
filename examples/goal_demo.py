# Shows how to connect to the NHL Edge API
# to get goal data for a specific game
#
# Might make more sense for this to live in
# `edge_demo.py`; can move this around if desired

from nhl_analytics import NHLClient

GAME_ID = 2026020001  # replace with a real game ID

def main():
    # Get the game play by play

    # use a GET command to get the play-by-play from
    # NHL Edge's API:
    # https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play

    with NHLClient() as client:
        # URL_PLAYBYPLAY = f"https://api-web.nhle.com/v1/gamecenter/{GAME_ID}/play-by-play"
        URL_PLAYBYPLAY = f"gamecenter/{GAME_ID}/play-by-play"
        playbyplay = client.get(URL_PLAYBYPLAY)

        # turn this into a function, but save the items in the 'plays'
        # array that 
        goals = []
        for play in playbyplay['plays']:
            if play['typeDescKey'] == "goal":
                goals.append(play)

        # print(goals)
        num_goals = len(goals)
        print(f"Goals in Game {GAME_ID}: {num_goals}")
        # print(len(goals))

        # for each goal, get the sprite gif that's generated
        # from a JSON file!
        # sprite()
        # for goal in goals:

        # get the sprite for the first goal:
        goal_sprite_url = goals[0]['pptReplayUrl']
        print(goal_sprite_url[29:])
        print(goal_sprite_url)

        # use the NHLClient to get the goal sprite:
        # this required an update to the class itself
        #
        # might need to allow for another URL
        # to be accessed within the NHLClient from
        # here; Tucc is the best person to answer this

        # with NHLClient(api='sprites') as sprite_client:
        #     # get the goal sprite JSON
        #     goal_sprite_json = sprite_client.get(goal_sprite[29:])

        #     # save or dump it to a file eventually
        #     breakpoint()


    import time
    time.sleep(1)    # try to space the requests?
    import requests

    # switching up the URL slightly seems to work
    # url = goal_sprite_url
    # url = https://nhle.com{season}/{game_id}/ev{event_id}.json
    url = "https://nhle.com/20262027/2026020001/ev1211.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://nhl.com",
        "Origin": "https://nhl.com"
    }

    # resp = requests.get(url, headers=headers)
    # print(resp.status_code)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an error for 4xx/5xx status codes
        data = response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err} - Body: {response.text[:200]}")
    except requests.exceptions.JSONDecodeError:
        print(f"Response was not valid JSON: {response.text[:200]}")
    # breakpoint()

        ###################################################
        # turn these into plots using mplhockey (optionally)
        # print(goal_sprite)




        # (need to figure out how to quick stitch together)
        # mp4s; anim.save() was taking long in my experience.

    # "Locate the goal event in the plays array where "typeDescKey": "goal". Extract its eventId (or read the pptReplayUrl field directly from the goal object)."
    #
    # "Request the tracking sprite JSON from the NHL sprite host": 
    # https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json
    #
    #  https://wsr.nhle.com/sprites/20262027/2026020151/ev336.json
    #
    # (Note: There is also a metadata wrapper endpoint at https://nhle.com{game_id}/{event_id}, or you can call client.misc.goal_replay(game_id=..., event_id=...) using the nhl-api-py Python wrapper.
    #





    # TODO: check if using the nhl-api-py package is worth it
    #       for the goal replay getter

if __name__ == "__main__":
    main()
