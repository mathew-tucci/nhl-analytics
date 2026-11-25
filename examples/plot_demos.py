# Demos for mplhockey's rink plotting tools!
# 
# The first iterations of these are a subset of what's in
# the readme;
# https://github.com/Sport-Performance-Lab/mplhockey

# import gc
from mplhockey import NHLRink
import matplotlib
from matplotlib import pyplot as plt

# Required to handle multiple separate plot pop-ups on MacOS
matplotlib.use('TkAgg')

if __name__ == "__main__":

    # Regular, horizontal rink
    rink = NHLRink()
    my_drawn_rink = rink.draw()
    plt.show()
    plt.close('all')

    # O-zone
    new_rink = NHLRink()
    new_rink.draw(rotation=90, display_range="ozone")
    plt.show()

    # Other cool plots are on the way

    ##############################################
    ######## Wiring to NHL Edge Goal API #########    
    ##############################################

    