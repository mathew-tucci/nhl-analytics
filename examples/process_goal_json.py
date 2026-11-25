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
from mplhockey import NHLRink
import matplotlib
from matplotlib import pyplot as plt

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

    return x_feet, y_feet

# json file; hardcoded for now
JSON_FILE = './json_goal.json'

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
        rink = NHLRink(units= 'ft')
        my_drawn_rink = rink.draw()
        
        # fig, ax = plt.figure()


        x, y = get_coords(frame)
        my_drawn_rink.scatter(x, y)
        # plt.scatter(x,y)
        # my_drawn_rink.scatter(x, y, c='black')
        # print(x)
        
        # save the figure
        plt.savefig(f'./data/goal_frame_{i:03d}')
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