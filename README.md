# Generative Geometric Designs

Playing around with procedurally-generated graphics in Python. Currently it's one thing that generates raster images, but I also want to try out creating vector graphics this way.

## Installation/Setup

Create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

## Random Triangles

![Example random triangles design](rand_triangles/example_triangles.png)

### Use

```shell
cd rand_triangles
python rand_triangles.py
```

### Parameters

Change these in `rand_triangles/triangle_params.yaml`

- `bg_type` (str):
  Whether to fill the background with an `image`, `gradient` or solid `color`
- `out_filename` (str):
  Filename of the output image
- `fg_color` (str):
  Hex string of the color of the triangles
- `bg_image` (str):
  Path/filename of background image (used only if `bg_type` is `image`)
- `bg_color` (str):
  Hex string of background color (used only if `bg_type` is `color`)
- `bg_gradient` ([str, str]):
  List of 2 hex strings specifying start and end colors of the background gradient (used only if `bg_type` is `gradient`)
- `gradient_dir` (str):
  Direction of gradient, `horz` or `vert` (used for both gradient background and variable `fill_prob`
- `num_rows` (int):
  Number of rows of triangles. If `bg_type` is `image`, this determines the size of the rows and number of columns (`grid_dim` and `num_cols` will be ignored if set)
- `num_cols` (int):
  Number of columns of triangles. (Not used if `bg_type` is `image`)
- `grid_dim` (int):
  Dimensions (in pixels) of each row and column. (Not used if `bg_type` is `image`)
- `fill_prob` (number or [number number])
  What is the probability that a cell has a triangle in it? If set as a single number (in the range [0, 1]), the probability is constant across the image. If set as a list of two numbers, the probability will vary by row or column (depending on the value of `gradient_dir`)
- `fill_empty` (bool):
  If false, cells left empty by `fill_prob` will show the background color/image/gradient. If true, empty cells will be filled completely by the foreground color
- `show_grid` (bool, optional):
  Whether to show the grid on which the triangles are drawn. If not specified, defaults to False.
- `rand_seed` (int, optional):
  Optionally seed the random number generator to get repeatable creations.

## Isometric Photo

Create a version of an image with an isometric grid of triangles. This supports images with transparency. You can generate both SVG and PNG outputs.

![Example: The Great Wave off Kanagawa](isometric_photo/tri_great_wave.png)

*[The Great Wave off Kanagawa, by Katsushika Hokusai](https://en.wikipedia.org/wiki/The_Great_Wave_off_Kanagawa)*

### Use

```shell
cd isometric_photos
python isometric_photo.py YAML_PARAM_FILE
```

You can create your own YAML parameter file or use the example one: [isometric_params.yaml](isometric_photos/isometric_params.yaml)

### Parameters

Set these in your YAML parameters file.

- `source_img` (str):
  Filename to generate your triangular version of
- `out_filename` (str):
  Filename of the output image. Leave off the file extension; it will be generated automatically.
- `out_width` (int, optional):
  Width of the output images, in pixels. If not specified, it will match the dimensions of the input image.
- `num_cols` (int):
  Number of columns of triangles in the output image.
- `color_average_width` (int, optional):
  Width of the square area (px in the original image coordinates) in the center of each triangle to average to generate the color of the triangle. If not specified, it will default to 1px (center coordinate only).
- `generate_svg` (bool, optional):
  Whether to generate an SVG image output. If not specified, defaults to True.
- `generate_png` (bool, optional):
  Whether to generate a PNG image output. If not specified, defaults to True.

## More maybe coming ~~soon~~ eventually