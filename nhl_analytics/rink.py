"""NHL rink drawing helpers (units: feet, origin at center ice)."""

import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

RINK_HALF_LENGTH = 100.0       # 200 ft long
RINK_HALF_WIDTH = 42.5         # 85 ft wide
CORNER_RADIUS = 28.0
BLUE_LINE_X = 25.0
LINE_WIDTH_FT = 1.0
GOAL_LINE_X = 89.0
CIRCLE_RADIUS = 15.0
END_ZONE_DOT_X = 69.0
FACEOFF_DOT_Y = 22.0
NEUTRAL_DOT_X = 20.0
HASH_OFFSET_X = 2.875
HASH_LENGTH = 2.0
CREASE_RADIUS = 6.0

RED = '#c8102e'
BLUE = '#0033a0'


def sprite_to_feet(x, y):
    """Convert NHL Edge sprite coords (inches, top-left origin) to feet from center ice."""
    return x / 12.0 - 100.0, 42.5 - y / 12.0


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
    board_color='black',
):
    """Draw NHL rink markings on a matplotlib axis; each feature is toggleable."""

    if boards:
        ax.add_patch(FancyBboxPatch(
            (-RINK_HALF_LENGTH, -RINK_HALF_WIDTH),
            2 * RINK_HALF_LENGTH, 2 * RINK_HALF_WIDTH,
            boxstyle=f'round,pad=0,rounding_size={CORNER_RADIUS}',
            fill=False, edgecolor=board_color, lw=2, zorder=1,
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
        theta = np.linspace(np.pi / 2, 3 * np.pi / 2, 50)
        for sign in (-1, 1):
            ax.fill(sign * (GOAL_LINE_X + CREASE_RADIUS * np.cos(theta)),
                    CREASE_RADIUS * np.sin(theta),
                    color='#8ecae6', alpha=0.6, zorder=1)

    ax.set_xlim(-RINK_HALF_LENGTH - 2, RINK_HALF_LENGTH + 2)
    ax.set_ylim(-RINK_HALF_WIDTH - 2, RINK_HALF_WIDTH + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    return ax
