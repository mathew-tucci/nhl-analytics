# Processes goal json files.
#
# Decisions regarding where and how to structure
# the datasets still need to be made; this
# script is intended to expose what key-value pairs
# and other data is saved in each frame of the goal
# visualizations.
#
# how to use ffmpeg to create a video from the data:
#
# cd data/
# ffmpeg -f image2 -pattern_type glob -framerate 10 -i 'goal_frame_*.png' -s 1200x800 my_goal.mp4

import json
import os
from mplhockey import NHLRink
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

import numpy as np

# Required to handle multiple separate plot pop-ups on MacOS
matplotlib.use('TkAgg')

def get_coords(frame):
    """
        Gets (x,y) coordinates of all players on the ice
        and puck coordinates as well.

    """

    # puck coordinates
    # puck = (frame['onIce']['1']['x'], frame['onIce']['1']['y'])

    # all other coordinates
    # check what fastest way of handling data structure is
    n_players = len(frame['onIce'].keys())
    x = np.zeros(n_players)
    y = np.zeros(n_players)
    teams = []

    i = 0
    for key in frame['onIce']:

        # the data is gonna require re-normalization;
        # need to see if this is rink-dependent.
        # if key == '14088':
        #     goalie = (frame['onIce'][key]['x'], frame['onIce'][key]['y'])
        # else:
        #     x[i] = frame['onIce'][key]['x']
        #     y[i] = frame['onIce'][key]['y']
        # not sure what units this is in

        x[i] = frame['onIce'][key]['x']
        y[i] = frame['onIce'][key]['y']
        teams.append(frame['onIce'][key].get('teamAbbrev'))
    
        i+=1
        
    # players = list(frame['onIce'].keys())[:-1]
    # x = frame['onIce'][players]['x']
    # y = frame['onIce'][players]['y']

    # NHL edge gives player positions in inches and
    # sets the upper left corner of the rink to (0,0).
    #
    # inches *could* be used in the NHLRink API; the
    # conversion to feet isn't really needed
    x_feet = (x / 12.0) - 100.0
    y_feet = 42.5 - (y / 12.0)

    return x_feet, y_feet, teams


# NHL rink dimensions in feet, origin at center ice
# (matches the coordinate system returned by get_coords)
RINK_HALF_LENGTH = 100.0       # 200 ft long
RINK_HALF_WIDTH = 42.5         # 85 ft wide
CORNER_RADIUS = 28.0
BLUE_LINE_X = 25.0             # blue lines 25 ft from center
LINE_WIDTH_FT = 1.0            # blue / red lines are 12 in wide
GOAL_LINE_X = 89.0             # 11 ft from end boards
CIRCLE_RADIUS = 15.0
END_ZONE_DOT_X = 69.0          # 20 ft out from goal line
FACEOFF_DOT_Y = 22.0           # 22 ft either side of center
NEUTRAL_DOT_X = 20.0           # 5 ft inside the blue lines
HASH_OFFSET_X = 2.875          # hashmarks 5'9" apart (2'10.5" from dot)
HASH_LENGTH = 2.0
CREASE_RADIUS = 6.0

RED = '#c8102e'
BLUE = '#0033a0'


def draw_rink_markings(
    ax,
    boards=True,
    center_line=True,
    blue_lines=True,
    goal_lines=True,
    center_circle=True,
    faceoff_circles=True,
    hashmarks=True,
    faceoff_dots=True,
    creases=True,
):
    """
        Draws NHL rink markings on a matplotlib axis.

        Each feature can be toggled independently so they
        can be exposed as parameters later.
    """

    if boards:
        ax.add_patch(FancyBboxPatch(
            (-RINK_HALF_LENGTH, -RINK_HALF_WIDTH),
            2 * RINK_HALF_LENGTH, 2 * RINK_HALF_WIDTH,
            boxstyle=f'round,pad=0,rounding_size={CORNER_RADIUS}',
            fill=False, edgecolor='black', lw=2, zorder=1,
        ))

    if center_line:
        ax.plot([0, 0], [-RINK_HALF_WIDTH, RINK_HALF_WIDTH],
                color=RED, lw=3, zorder=1)

    if blue_lines:
        for sign in (-1, 1):
            ax.fill_between(
                [sign * BLUE_LINE_X - LINE_WIDTH_FT / 2,
                 sign * BLUE_LINE_X + LINE_WIDTH_FT / 2],
                -RINK_HALF_WIDTH, RINK_HALF_WIDTH,
                color=BLUE, zorder=1,
            )

    if goal_lines:
        # goal lines stop at the curved boards
        for sign in (-1, 1):
            dx = GOAL_LINE_X - (RINK_HALF_LENGTH - CORNER_RADIUS)
            dy = np.sqrt(CORNER_RADIUS**2 - dx**2)
            y_edge = (RINK_HALF_WIDTH - CORNER_RADIUS) + dy
            ax.plot([sign * GOAL_LINE_X] * 2, [-y_edge, y_edge],
                    color=RED, lw=1, zorder=1)

    if center_circle:
        ax.add_patch(Circle((0, 0), CIRCLE_RADIUS, fill=False,
                            edgecolor=BLUE, lw=1.5, zorder=1))

    end_zone_spots = [(sx * END_ZONE_DOT_X, sy * FACEOFF_DOT_Y)
                      for sx in (-1, 1) for sy in (-1, 1)]

    if faceoff_circles:
        for cx, cy in end_zone_spots:
            ax.add_patch(Circle((cx, cy), CIRCLE_RADIUS, fill=False,
                                edgecolor=RED, lw=1.5, zorder=1))

    if hashmarks:
        # short lines on the top and bottom of each end-zone circle
        for cx, cy in end_zone_spots:
            for hx in (-HASH_OFFSET_X, HASH_OFFSET_X):
                for sy in (-1, 1):
                    y0 = cy + sy * np.sqrt(CIRCLE_RADIUS**2 - hx**2)
                    ax.plot([cx + hx] * 2, [y0, y0 + sy * HASH_LENGTH],
                            color=RED, lw=1.5, zorder=1)

    if faceoff_dots:
        neutral_spots = [(sx * NEUTRAL_DOT_X, sy * FACEOFF_DOT_Y)
                         for sx in (-1, 1) for sy in (-1, 1)]
        for cx, cy in end_zone_spots + neutral_spots:
            ax.add_patch(Circle((cx, cy), 1.0, color=RED, zorder=1))
        ax.add_patch(Circle((0, 0), 0.5, color=BLUE, zorder=1))

    if creases:
        for sign in (-1, 1):
            theta = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
            ax.fill(sign * (GOAL_LINE_X + CREASE_RADIUS * np.cos(theta)),
                    CREASE_RADIUS * np.sin(theta),
                    color='#8ecae6', alpha=0.6, zorder=1)

    ax.set_xlim(-RINK_HALF_LENGTH - 2, RINK_HALF_LENGTH + 2)
    ax.set_ylim(-RINK_HALF_WIDTH - 2, RINK_HALF_WIDTH + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    return ax


TEAM_COLORS = {
    'ANA': '#F47A38', 'ARI': '#8C2633', 'BOS': '#FFB81C', 'BUF': '#003087',
    'CAR': '#CE1126', 'CBJ': '#CE1126', 'CGY': '#C8102E', 'CHI': '#CF0A2C',
    'COL': '#6F263D', 'DAL': '#006847', 'DET': '#CE1126', 'EDM': '#FF4C00',
    'FLA': '#C8102E', 'LAK': '#A2AAAD', 'MIN': '#154734', 'MTL': '#AF1E2D',
    'NJD': '#CE1126', 'NSH': '#FFB81C', 'NYI': '#F26924', 'NYR': '#0038A8',
    'OTT': '#C52032', 'PHI': '#F74902', 'PIT': '#FFB81C', 'SEA': '#99D9D9',
    'SJS': '#006D75', 'STL': '#FFB81C', 'TBL': '#002868', 'TOR': '#00205B',
    'UTA': '#6CACE3', 'VAN': '#00205B', 'VGK': '#B4975A', 'WPG': '#55565A',
    'WSH': '#C8102E',
}

def team_color(abbrev):
    if abbrev in TEAM_COLORS:
        return TEAM_COLORS[abbrev]
    # unknown team / puck: fall back to a neutral color
    return 'black'


# json file; hardcoded for now
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(SCRIPT_DIR, 'json_goal.json')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# set to True to use mplhockey instead of draw_rink_markings
USE_MPLHOCKEY = False

# toggle individual rink features (passed to draw_rink_markings)
RINK_OPTIONS = dict(
    boards=True,
    center_line=True,
    blue_lines=True,
    goal_lines=True,
    center_circle=True,
    faceoff_circles=True,
    hashmarks=True,
    faceoff_dots=True,
    creases=True,
)

if __name__ == "__main__":

    # 1. load the json file
    with open(JSON_FILE, 'r') as f:
        file = json.load(f)

    # 2. show the available keys
    print(file[0].keys())

    # I think 1 is the puck; need to confirm this
    
    # 3. re-create goal visualization - requires mplhockey
    # plt.show()
    # plt.close('all')
    i = 0
    for frame in file:
        # get x and y coordinates for each player
        # (eventually separate by team)
        if USE_MPLHOCKEY:
            rink = NHLRink(units= 'ft')
            my_drawn_rink = rink.draw()
        else:
            fig, my_drawn_rink = plt.subplots(figsize=(12, 5.5))
            draw_rink_markings(my_drawn_rink, **RINK_OPTIONS)
        
        # fig, ax = plt.figure()


        x, y, teams = get_coords(frame)
        matchup = ' vs '.join(sorted({t for t in teams if t}))
        my_drawn_rink.set_title(matchup)
        colors = [team_color(t) for t in teams]
        my_drawn_rink.scatter(x, y, c=colors, zorder=3,
                              edgecolors='white', linewidths=0.5)
        # plt.scatter(x,y)
        # my_drawn_rink.scatter(x, y, c='black')
        # print(x)
        
        # save the figure
        plt.savefig(os.path.join(DATA_DIR, f'goal_frame_{i:03d}'))
        plt.close('all')
        # NOTE: collecting all the data and plotting
        #       in one go might be a more
        #       efficient approach; need to explore this.

        i+=1
        

    # for each frame, overlay a scatterplot with players,
    # and save the figures. 

    # note: need to combine these with ffmpeg - easier to
    #       do this within a python script, but matplotlib's
    #       animation function seems way too slow.


    # 4. try to track speed or another quantity
    #    TODO: check spatial resolution / accuracy / uncertainty

    # 5. do something else cool!


    # 6. save the goal coordinates in a larger dataset?
    #    (goal is to compute metrics with this)