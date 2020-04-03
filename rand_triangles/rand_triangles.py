import random
import math
import itertools
from typing import Tuple

import yaml

from PIL import Image, ImageDraw


# Parameters
with open(r'triangle_params.yaml') as file:
    PARAMS = yaml.load(file, Loader=yaml.FullLoader)


def hex_to_rgb(hex):
    hex_map = {
        3: (0, 1, 2),
        4: (1, 2, 3),
        6: (0, 2, 4),
        7: (1, 3, 5)
    }
    lhex = len(hex)
    if lhex in [3, 4]:
        return tuple(int(hex[i]+hex[i], 16) for i in hex_map[lhex])
    elif lhex in [6, 7]:
        pass
        return tuple(int(hex[i:i+2], 16) for i in hex_map[lhex])
    else:
        # Invalid (not able to do RGBa yet)
        raise ValueError('String must be 8- or 16-bit hex string, with or without leading #')


def interpolate_color(start_color, end_color, interval):
    # How much the color changes by at each step
    delta_color = [(e - s) / interval for s, e in zip(start_color, end_color)]
    for i in range(interval):
        yield [round(s + delta * i) for s, delta in zip(start_color, delta_color)]


def interpolate_fill_prob(start_prob, end_prob, interval):
    delta_prob = (end_prob - start_prob) / interval
    return [start_prob + delta_prob*i for i in range(interval)]


def draw_gradient(draw, gradient_stops, width, height):
    gradient = list(map(hex_to_rgb, gradient_stops))
    direction = PARAMS['gradient_dir']
    if direction == 'horz':
        interval = width
    elif direction == 'vert':
        interval = height
    else:
        raise ValueError('"gradient_dir" parameter must be "horz" or "vert"')

    for i, color in enumerate(interpolate_color(gradient[0], gradient[1], interval)):
        if direction == 'horz':
            coords = [(i, 0), (i, height)]
        elif direction == 'vert':
            coords = [(0, i), (width, i)]
        draw.line(coords, fill=tuple(color), width=1)


def transform_coords(coords, row_col, grid_dim):
    return [
        ((row_col[0] + co[0]) * grid_dim,
         (row_col[1] + co[1]) * grid_dim)
        for co in coords
    ]


def draw_grid(draw, num_rows, num_cols, grid_dim):
    """
    Draw a grid of the squares
    """
    # Draw rows
    for r in range(1, num_rows):
        draw.line([(0, r*grid_dim), (num_cols*grid_dim, r*grid_dim)], '#666')
    # Draw columns
    for c in range(1, num_cols):
        draw.line([(c*grid_dim, 0), (c*grid_dim, num_rows*grid_dim)], '#666')


def gen_triangles():
    """
    Create all the triangles
    """

    # Seed the random number generator
    try:
        random.seed(PARAMS['rand_seed'])
    except KeyError:
        # No random seed specified; proceed with default seeding
        rand_seed = random.randint(0, 99999999999999999)  # I know this is hacky
        random.seed(rand_seed)
        print('Random seed:', rand_seed)

    # Create the canvas
    if PARAMS['bg_type'] == 'image':
        im = Image.open(PARAMS['bg_image'])
        width, height = im.size
        # With image background, only the num_rows is used; num_cols and grid_dim are based on image dimensions
        num_rows = PARAMS['num_rows']
        grid_dim = math.ceil(height / num_rows)
        num_cols = math.ceil(width / grid_dim)
    else:
        num_cols = PARAMS['num_cols']
        num_rows = PARAMS['num_rows']
        grid_dim = PARAMS['grid_dim']
        width = num_cols * grid_dim
        height = num_rows * grid_dim
        im = Image.new(
            'RGB',  # 3x8-bit pixels, true color
            (width, height),  # Image dimensions (width, height)
        )
    draw = ImageDraw.Draw(im)
    if PARAMS['bg_type'] == 'gradient':
        draw_gradient(draw, PARAMS['bg_gradient'], width, height)
    elif PARAMS['bg_type'] == 'color':
        # Draw the background
        draw.rectangle(
            [0, 0, width, height],
            fill=PARAMS['bg_color']
        )

    # Create list of which corners to draw
    corners = [random.randint(0, 3) for _ in range(num_rows*num_cols)]
    # Create list of (row, col) tuples
    rows_cols = itertools.product(range(num_cols), range(num_rows))

    # Mapping corner index to triangle shape
    corner_coords = [
        [(0, 0), (1, 0), (0, 1)],  # upper left
        [(0, 0), (1, 0), (1, 1)],  # upper right
        [(1, 0), (1, 1), (0, 1)],  # lower right
        [(0, 0), (1, 1), (0, 1)]  # lower left
    ]

    # Generate location-varying fill probability
    fill_prob = PARAMS['fill_prob']
    if type(fill_prob) == list:
        direction = PARAMS['gradient_dir']
        if direction == 'vert':
            interval = num_rows
            row_col_check = 1
        elif direction == 'horz':
            interval = num_cols
            row_col_check = 0
        else:
            raise ValueError('"gradient_dir" parameter must be "horz" or "vert"')
        fill_probs = interpolate_fill_prob(fill_prob[0], fill_prob[1], interval)
    elif type(fill_prob) in (float, int):
        interval = num_rows
        row_col_check = 1
        fill_probs = [fill_prob for _ in range(interval)]
    else:
        raise ValueError('"fill_prob" must be a number or list of 2 numbers')

    # Draw the triangles at these locations
    for corner, row_col in zip(corners, rows_cols):
        if random.random() <= fill_probs[row_col[row_col_check]]:
            draw.polygon(
                transform_coords(corner_coords[corner], row_col, grid_dim),
                fill=PARAMS['fg_color']
            )
        elif PARAMS['fill_empty']:
            draw.rectangle(
                transform_coords([(0, 0), (1, 1)], row_col, grid_dim),
                fill=PARAMS['fg_color']
            )

    # Draw a grid, if you're supposed to
    try:
        if PARAMS['show_grid']:
            draw_grid(draw, num_rows, num_cols, grid_dim)
    except KeyError:
        # show_grid not specified; default to False (no grid)
        pass

    # Save
    im.save(PARAMS['out_filename'], 'PNG')


if __name__ == "__main__":
    # Generate the image
    gen_triangles()
