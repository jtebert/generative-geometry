# Create a version of a photo with equilateral triangles

import sys
import itertools
import math
from typing import Tuple, List, Optional, Dict

import yaml
from PIL import Image, ImageDraw
import svgwrite
import numpy as np


def main(yaml_params: str):

    # Parameters
    with open(yaml_params) as file:
        params = yaml.load(file, Loader=yaml.FullLoader)

    num_cols = params['num_cols']
    photo_src = params['source_img']
    out_filename = params['out_filename']
    try:
        gen_png = params['generate_png']
    except KeyError:
        gen_png = True
    try:
        gen_svg = params['generate_svg']
    except KeyError:
        gen_svg = True
    try:
        c_avg_width = params['color_average_width']
    except KeyError:
        c_avg_width = 1

    if not gen_png and not gen_svg:
        print("ERROR: You chose to make neither an SVG or PNG. There's nothing for me to do!")
        exit(1)

    src_im = Image.open(photo_src, 'r')
    # Convert to RGB in case source file is something different
    src_im = src_im.convert('RGBA')
    src_img_dim = src_im.size

    # Set dimensions of SVG output to line up with triangles
    aa_multiple = 3
    # Use the input dimension
    # Scaling for anti-aliasing raster output
    if 'out_width' in params:
        out_width = int(params['out_width']*aa_multiple)
    else:
        out_width = src_img_dim[0]*aa_multiple
    out_scaling = out_width/src_img_dim[0]
    # Get the height from the ratio
    out_height = int(src_img_dim[1]*out_scaling)

    side_len = out_width / num_cols/out_scaling

    out_dim = (out_width, out_height)

    # Generate SVG
    src_tri_grid = gen_triangle_grid(src_img_dim, side_len, num_cols)
    out_tri_grid = gen_triangle_grid(out_dim, side_len*out_scaling, num_cols)

    if gen_svg:
        dwg = svgwrite.Drawing(out_filename+'.svg', size=out_dim, profile='tiny')
    if gen_png:
        # Generate raster (PNG)
        im = Image.new('RGBA', out_dim)
        draw = ImageDraw.Draw(im)
    # Draw the triangles
    for dir in ['up', 'down']:
        # Get center coordinates
        src_center_coords = [get_tri_center(start, side_len, dir) for start in src_tri_grid]
        out_center_coords = [get_tri_center(start, side_len*out_scaling, 'up') for start in out_tri_grid]
        # Get the coordinates of the triangle vertices
        tri_coords = [tri_points(start, side_len*out_scaling, dir) for start in out_tri_grid]
        if gen_svg:
            svg_center_colors = [get_color(src_im, center, type='svg', width=c_avg_width)
                                 for center in src_center_coords]
            [draw_triangle(dwg, points, color) for (points, color) in zip(tri_coords, svg_center_colors)]
        if gen_png:
            png_center_colors = [get_color(src_im, center, type='png', width=c_avg_width)
                                 for center in src_center_coords]
            [draw.polygon(points, fill=color) for (points, color) in zip(tri_coords, png_center_colors)]
            # [draw.ellipse((c[0]-2, c[1]-2, c[0]+2, c[1]+2), fill='red') for c in out_center_coords[:10]]
    if gen_svg:
        dwg.save()
    if gen_png:
        # Rescale down to get anti-aliasing
        im = im.resize(
            (int(out_width/aa_multiple), int(out_height/aa_multiple)),
            resample=Image.ANTIALIAS)
        im.save(out_filename+'.png', 'PNG')


def get_color(img, coord, type, width=1):
    max_x = img.size[0]-1
    max_y = img.size[1]-1
    x = min(coord[0], max_x)
    y = min(coord[1], max_y)

    if width > 1:
        w = width/2
        use_coords = (
            max(x-w, 0), max(y-w, 0),
            min(x+w, max_x), min(y+w, max_y)
        )
        area = img.crop(use_coords)
        # if 100 < x < 200 and 100 < y < 200:
        #     print(use_coords, area.size)
        if 0 in area.size:
            color = img.getpixel((x, y))
        else:
            row_color = np.average(area, axis=0)
            avg_color = np.average(row_color, axis=0)
            color = tuple(avg_color.astype(int))
            # if x < 100 and y < 100:
            #     print(color)
    else:
        color = img.getpixel((x, y))
    if type == 'svg':
        return svgwrite.rgb(*color[0:3]), color[3]
    elif type == 'png':
        return color


def tri_points(start: Tuple[float, float], side_len: float, orientation: str) -> List[Tuple[float, float]]:
    height = side_len * math.sin(math.degrees(60))  # Triangle height
    if orientation == 'up':
        y_point = start[1] - height
    elif orientation == 'down':
        y_point = start[1] + height
    else:
        raise ValueError('Invalid orientation. Must be "up" or "down".')
    return [start,
            (start[0]+side_len, start[1]),
            (start[0]+side_len/2, y_point)]


def draw_triangle(dwg, coords, color):
    # Don't draw fully transparent triangles
    if color[1] != 0:
        dwg.add(dwg.polygon(
            points=coords,
            stroke=color[0],
            stroke_width='0.5px',
            stroke_linejoin='round',
            stroke_opacity=color[1]/255,
            fill=color[0],
            fill_opacity=color[1]/255
        ))


def get_tri_center(start: Tuple[float, float], side_len: float, orientation: str) -> Tuple[float, float]:
    """
    Get the center coordinates (x,y) of an equilateral triangle based at `start`
    location, with side length `side_len`. Starting location is the furthest
    left coordinate of the triangle

    Parameters
    ----------
    start : Tuple[float, float]
        Furthest left (x,y) coordinate of the triangle (lowest x value)
    side_len : float
        Length in pixels of the equilateral triangle
    orientation : Optional[str], optional
        Direction of the equilateral triangle, up or down, by default 'up'

    Returns
    -------
    Tuple[float, float]
        (x,y) coordinates in pixels of the center of triangle
    """
    y_offset = side_len * math.sin(math.degrees(60))/3  # center is 1/3 of the way up
    if orientation == 'up':
        y_ctr = start[1] - y_offset
    elif orientation == 'down':
        y_ctr = start[1] + y_offset
    else:
        raise ValueError('Invalid orientation. Must be "up" or "down".')
    ctr = start[0] + side_len/2, y_ctr
    return ctr


def gen_triangle_grid(img_dim: Tuple[float, float], side_len: float, num_cols) \
        -> List[Tuple[float, float]]:
    """
        Generate the starting coordinates of a grid of equilateral triangles, for a
        given dimensions of image to fill (in pixels) and side length of triangle

        Parameters
        ----------
        img_dim : Tuple[float, float]
            (width, height) of the image to cover, in pixels
        side_len : float
            Length of the side of the equilateral triangles, in pixels

        Returns
        -------
        List[Tuple[float, float]]
            List of the (x, y) coordinates of the triangle starting positions
            (furthest left vertex)
        """
    # Compute the x coordinates
    # num_cols = math.ceil(img_dim[0]/side_len)+2
    num_cols = num_cols + 1
    x_offset = side_len/2
    x_coords_0 = [x*side_len for x in range(num_cols)]
    x_coords_shifted = [x*side_len-x_offset for x in range(num_cols)]

    # Compute the y coordinates
    row_height = side_len * math.sin(math.degrees(60))
    half_num_rows = math.ceil(img_dim[1]/row_height/2)+1
    # Every other row is shifted
    y_coords_0 = [y*2*row_height+row_height for y in range(half_num_rows)]
    y_coords_shifted = [y*2*row_height for y in range(half_num_rows)]

    # Cartesian cross to get all the coordinates (itertools.product)
    coords = list(itertools.product(x_coords_0, y_coords_0))
    coords.extend(itertools.product(x_coords_shifted, y_coords_shifted))
    return coords


if __name__ == '__main__':
    try:
        yaml_params = sys.argv[1]
    except IndexError:
        # No yaml file specified
        print('ERROR: Give me a YAML file for your parameters!')
        exit(1)
    main(yaml_params)
