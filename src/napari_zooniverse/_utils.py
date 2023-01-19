import numpy as np
from panoptes_client import Project, Panoptes, Subject, SubjectSet
import glob
import os
import sys
import getpass
import re
#-----------------------------------------------------------------------------------------------------------------------
# Preprocessing data
from qtpy.QtWidgets import (QLabel,
                            QWidget,
                            QHBoxLayout)
from magicgui.widgets import create_widget


def make_widget(annotation, label):
    w = QWidget()
    w.setLayout(QHBoxLayout())
    w.layout().addWidget(QLabel(label))

    magic_w = create_widget(annotation=annotation, label=label)
    w.layout().addWidget(magic_w.native)

    set_border(w)

    return w, magic_w


def set_border(widget: QWidget, spacing=2, margin=0):
    if hasattr(widget.layout(), "setContentsMargins"):
        widget.layout().setContentsMargins(margin, margin, margin, margin)
    if hasattr(widget.layout(), "setSpacing"):
        widget.layout().setSpacing(spacing)
#
#
# def fill_pixels(img,
#                 tile_x_idx,
#                 tile_y_idx,
#                 n_tiles_x,
#                 n_tiles_y,
#                 tile_size_x,
#                 tile_size_y,
#                 offset_x=0,
#                 offset_y=0,
#                 dtype=np.uint8):
#     """
#     Retrieves the pixels from the raw image and positions them in the new image to be saved. For offset tiling,
#     selected raw pixels will not fill the output image. Unfilled pixels are padded with zeroes, giving a black border.
#
#     :param img: Raw image, passed as a numpy array (2D)
#     :param tile_x_idx: Index of which tile (in the x-direction) is being considered (Integer)
#     :param tile_y_idx: Index of which tile (in the y-direction) is being considered (Integer)
#     :param n_tiles_x: Number of tiles in the x-direction
#     :param n_tiles_y: Number of tiles in the y-direction
#     :param tile_size_x: Size of tiles in the x-direction
#     :param tile_size_y: Size of tiles in the y-direction
#     :param offset_x: Offset in the x-direction
#     :param offset_y: Offset in the y-direction
#     :param dtype:
#     :return: Numpy array containing correctly positioned pixels from raw data
#     """
#
#     # An empty image to be filled with selected pixels from raw data
#     tile_data = np.zeros((tile_size_y, tile_size_x), dtype=dtype)
#     (raw_size_y, raw_size_x) = img.shape
#
#     # Calculate the x and y positions of the pixels we want to copy from the raw image
#     x_start_raw = tile_size_ x *tile_x_idx - offset_x
#     x_stop_raw = x_start_raw + tile_size_x
#     y_start_raw = tile_size_ y *tile_y_idx - offset_y
#     y_stop_raw = y_start_raw + tile_size_y
#
#     # In an offset image, the "start" position might be negative, or larger than the image size, so we need to "clip"
#     # these values to valid pixel positions
#     clip_y_start = np.clip(y_start_raw, 0, raw_size_y -1)
#     clip_y_stop = np.clip(y_stop_raw, 0, raw_size_y -1)
#     clip_x_start = np.clip(x_start_raw, 0, raw_size_x -1)
#     clip_x_stop = np.clip(x_stop_raw, 0, raw_size_x -1)
#
#     size_x_clip = clip_x_stop - clip_x_start
#     size_y_clip = clip_y_stop - clip_y_start
#
#     # Calculate the positions of the pixels we want to fill, depending on whether there's an offset
#     # and which tile we're considering
#     if tile_y_idx == 0:
#         fill_y_start = offset_y
#     else:
#         fill_y_start = 0
#
#     if tile_x_idx == 0:
#         fill_x_start = offset_x
#     else:
#         fill_x_start = 0
#
#     fill_y_stop = fill_y_start + size_y_clip
#     fill_x_stop = fill_x_start + size_x_clip
#
#     tile_data[fill_y_start:fill_y_stop, fill_x_start:fill_x_stop] = img[clip_y_start:clip_y_stop, clip_x_start:clip_x_stop]
#
#     print(f"Raw:\tX {clip_x_start}:{clip_x_stop}; Y {clip_y_start}:{clip_y_stop}")
#
#     return tile_data
#
#
# def fill_pixels_RGB(input_image,
#                     tile_x_idx,
#                     tile_y_idx,
#                     n_tiles_x,
#                     n_tiles_y,
#                     tile_size_x,
#                     tile_size_y,
#                     offset_x=0,
#                     offset_y=0,
#                     dtype=np.uint8):
#     """ Run the fill_pixels function for each channel of an RGB
#     """
#     R = input_image[: ,: ,0]
#     G = input_image[: ,: ,1]
#     B = input_image[: ,: ,2]
#
#     R_tile = fill_pixels(R,
#                          tile_x_idx,
#                          tile_y_idx,
#                          n_tiles_x,
#                          n_tiles_y,
#                          tile_size_x,
#                          tile_size_y,
#                          offset_x,
#                          offset_y,
#                          dtype)
#
#     G_tile = fill_pixels(G,
#                          tile_x_idx,
#                          tile_y_idx,
#                          n_tiles_x,
#                          n_tiles_y,
#                          tile_size_x,
#                          tile_size_y,
#                          offset_x,
#                          offset_y,
#                          dtype)
#
#     B_tile = fill_pixels(B,
#                          tile_x_idx,
#                          tile_y_idx,
#                          n_tiles_x,
#                          n_tiles_y,
#                          tile_size_x,
#                          tile_size_y,
#                          offset_x,
#                          offset_y,
#                          dtype)
#     RGB_tile = np.zeros(shape=(tile_size_y, tile_size_x, 3) ,dtype=np.uint8)
#     RGB_tile[: ,: ,0] = R_tile
#     RGB_tile[: ,: ,1] = G_tile
#     RGB_tile[: ,: ,2] = B_tile
#
#     return RGB_tile
#
#
# def tile_image(img, img_name, z_slice, n_tiles_x=1, n_tiles_y=1, offset=False, show_plot=False):
#     """
#     Create tiles of subregions of the input image
#
#     :param img: Input image
#     :param n_tiles_x: Number of tiles in X (equivalently number of columns) - Default 1
#     :param n_tiles_y: Number of tiles in Y (equivalently number of rows) - Default 1
#     :return: A dictionary containing ROI designations and the individual tiles
#     """
#     n_images = n_tiles_x * n_tiles_y
#     # images = {}
#     images = []
#     n_dims = img.ndim
#     if n_dims == 2:
#         (y_size, x_size) = img.shape  # Remember the arrays in python are indexed (rows, cols), equivalent to (y, x)
#         print(f"Image has dimensions X: {x_size}  and Y: {y_size}")
#     elif n_dims == 3:
#         (y_size, x_size,
#          z_size) = img.shape  # Remember the arrays in python are indexed (rows, cols), equivalent to (y, x)
#         print(f"Image has dimensions X: {x_size}  and Y: {y_size} and 3 channels (RGB)")
#     else:
#         print(f"Image has {n_dims} dimensions and I don't know what to do with it!")
#
#     y_size_tile = int(np.ceil(y_size / n_tiles_y))
#     x_size_tile = int(np.ceil(x_size / n_tiles_x))
#     if offset:
#         x_offset = int(np.ceil(x_size_tile / 2.))
#         y_offset = int(np.ceil(y_size_tile / 2.))
#         n_tiles_x += 1
#         n_tiles_y += 1
#     else:
#         x_offset = 0
#         y_offset = 0
#     print(f"Tile size: (X: {x_size_tile}, Y: {y_size_tile})")
#     file_index = 0
#     for x_tile in range(n_tiles_x):
#         x_start = x_tile * x_size_tile
#         for y_tile in range(n_tiles_y):
#             print(f"\n***\nProcessing tile {x_tile}, {y_tile}")
#             y_start = y_tile * y_size_tile
#             tile_name = f"{img_name[0:-4]}Tile_x{x_start - x_offset:04d}_y{y_start - y_offset:04d}_z{z_slice:04d}"
#             images.append(tile_name)
#             x_indices = np.add(x_start, np.arange(0, x_size_tile))
#             y_indices = np.add(y_start, np.arange(0, y_size_tile))
#             # print(f"{x_indices}")
#             if n_dims == 2:
#                 image_data = fill_pixels(img, x_tile, y_tile, n_tiles_x, n_tiles_y, x_size_tile, y_size_tile,
#                                          offset_x=x_offset, offset_y=y_offset)
#             elif n_dims == 3:
#                 image_data = fill_pixels_RGB(img, x_tile, y_tile, n_tiles_x, n_tiles_y, x_size_tile, y_size_tile,
#                                              offset_x=x_offset, offset_y=y_offset)
#             else:
#                 print(f"This image doesn't have 2 or 3-dimensions, it has {n_dims}. Exiting")
#                 (y_size, x_size, z_size) = img.shape
#                 print(f"X: {x_size}, Y: {y_size}, Z: {z_size}")
#                 success = False
#
#             file_index += 1
#             if offset is False:
#                 tile_str = f"Tiles_X{n_tiles_x}_Y{n_tiles_y}"
#             else:
#                 tile_str = f"Tiles_X{n_tiles_x - 1}_Y{n_tiles_y - 1}_OFFSET"
#             sub_dir = os.path.join(OUTPUT_DATA_DIR, tile_str, tile_name.split("_z")[0])
#             # If the sub-directory does not already exist, create it
#             if not os.path.exists(sub_dir):
#                 os.makedirs(sub_dir)
#             save_as_jpeg(image_data, tile_name, sub_dir)
#             if show_plot is True:
#                 plt.imshow(image_data, cmap='gray')
#                 plt.show()
#     print(f"Image names: {images}")
#     success = True
#
#     return success
#
#
# def save_as_jpeg(img, img_name, save_dir, scale_factor=1, quality_factor=90):
#     if scale_factor != 1:
#         print("Rescaling for JPEG")
#         # TODO: implement rescaling, probably using skimage.transform function dowscale_local_mean
#
#     print(f"Saving {img_name} as JPEG in {save_dir}")
#     file_name_to_save = os.path.join(save_dir, img_name + ".jpg")
#     imsave(file_name_to_save, img, quality=quality_factor)
#
#
# def test_single_image(dir_name, file_format="TIF", file_index=1, n_tiles_x=1, n_tiles_y=1, offset=False):
#     files = glob.glob(os.path.join(dir_name, f"*.{file_format.lower()}*"))
#     n_files = len(files)
#     if file_index > n_files:
#         print(
#             f"Sorry, you've asked for file {file_index} but there are only {n_files} files in the directory. Exiting")
#         return
#     files.sort()
#     file = files[file_index]
#     file_name = os.path.basename(file)
#     file_root = os.path.splitext(file_name)[0]
#     print(f"Reading {file_name}")
#
#     img = read_image(file)
#     print(f"Image has {img.ndim} dimensions")
#
#     # Assuming filename ends in XXX_0123.tif type format
#     #    z_slice = int(file_root.split('_')[-1])  # Old method assumes an underscore separator
#     z_slice = int(
#         re.findall(r'\d+', file_root)[-1])  # New method searches for last multi-digit number in the string
#     print(f"Z slice: {z_slice}")
#     tile_image(img, file_root, z_slice, n_tiles_x=n_tiles_x, n_tiles_y=n_tiles_y, offset=offset, show_plot=True)
#
#
# def loop_over_directory(dir_name, file_format="TIF", n_tiles_x=1, n_tiles_y=1, offset=False):
#     print(f"Reading from '{dir_name}'")
#     files = glob.glob(os.path.join(dir_name, f"*.{file_format.lower()}*"))
#     files.sort()
#     print(f"There are {len(files)} files")
#     for file in files:
#         file_name = os.path.basename(file)
#         file_root = os.path.splitext(file_name)[0]
#         print(f"Reading {file_name}")
#
#         img = read_image(file)
#         # Assuming filename ends in XXX_0123.tif type format
#         #     z_slice = int(file_root.split('_')[-1])
#         z_slice = int(
#             re.findall(r'\d+', file_root)[-1])  # New method searches for last multi-digit number in the string
#         print(f"Z slice: {z_slice}")
#         tile_image(img, file_root, z_slice, n_tiles_x=n_tiles_x, n_tiles_y=n_tiles_y, offset=offset)
#
#
# #---------------------------------------------------------------------------------------------
# # Uploading to zooniverse project
#
# # This function builds the subject from the chosen set of images and attaches metadata
# def build_subject(project, file_list, centre_idx, span, step):
#     subject = Subject()  # Inititialise a subject
#     subject.links.project = project  # ...attach it to a project
#     subject.metadata['Subject ID'] = centre_idx - step * span + 1  # Add the names of the images
#
#     # For loop to attach the images to the subject one-by-one
#     for i, idx in enumerate(range(centre_idx - step * span, centre_idx + (step * span) + 1, step)):
#         fname = str(file_list[idx])
#         print("Attaching %s to subject %d" % (os.path.basename(fname), centre_idx - step * span + 1))
#         subject.add_location(fname)
#         subject.metadata['Image %d' % i] = os.path.basename(fname)
#     subject.metadata['default_frame'] = span + 1  # We want people to annotate the middle image
#
#     # Metadata from here should be changed according to the data
#     subject.metadata['Microscope'] = 'SBF SEM (with FCC)'
#     subject.metadata['Raw XY resolution (nm)'] = 5
#     subject.metadata['Raw Z resolution (nm)'] = 50
#     subject.metadata['Scaling factor'] = 2
#     subject.metadata['jpeg quality (%)'] = 90
#     subject.metadata['Attribution'] = 'Matt Russell'
#     subject.metadata['Description'] = 'MP009_FCC_5-161118_Cell1registered-binnedx2 (HeLa)'
#     print("Starting to save")
#     print(subject)
#     subject.save()
#     print("Subject saved")
#
#     return subject
#
#
# def connect_to_zooniverse(project_id=PROJECT_ID, user_name=USERNAME):
#     try:
#         password = getpass.getpass(prompt='Password: ', stream=None)
#         Panoptes.connect(username=user_name, password=password)
#         print("Connected to Zooniverse")
#     except Exception as e:
#         print("Couldn't connect to Zooniverse")
#         print("Exception {}".format(e))
#         sys.exit(1)
#     print(f"Connecting to {project_id}...")
#     project = Project.find(slug=project_id)
#     print("...connected!")
#     return project
#
#
# # Helper function to initialise a "subject set" and attach it to a project
# def initialise_subject_set(project, subject_name):
#     subject_set = SubjectSet()
#     subject_set.links.project = project
#     subject_set.display_name = subject_name
#     subject_set.save()
#     return subject_set
#
# # Helper function to read all of the jpegs in a directory that have the given prefix
# def get_image_list(input_directory, prefix):
#     full_path = os.path.join(input_directory, prefix + '*.jpg')
#     file_list = glob.glob(full_path)
#     print(full_path)
#     n_files = len(file_list)
#     print(f"There are {n_files} jpg files in the directory {input_directory} with prefix {prefix}")
#     return file_list, n_files
#
#
# # Function to build a subject set from a fixed range of images
# def build_subject_set(project, file_list, file_idx_start, file_idx_stop, span, step, testing=False):
#     print(f"project {project}\n",
#           f"file_idx_start {file_idx_start}\n",
#           f"file_idx_stop {file_idx_stop}\n",
#           f"span {span}\n",
#           f"step {step}")
#     print(f"Building subject set from files {file_idx_start}-{file_idx_stop}")
#     subjects = []
#     min_idx = 0
#     max_idx = len(file_list) - span*step
#
#     for centre_idx in range(max(min_idx, file_idx_start), min(max_idx, file_idx_stop) + 1):
#         if testing:
#             print(f"Testing for subject centred on file {centre_idx} in the list")
#         else:
#             subject = build_subject(project, file_list, centre_idx, span, step)
#             subjects.append(subject)
#     return subjects


