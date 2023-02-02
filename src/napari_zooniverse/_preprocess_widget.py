import os
import warnings
from typing import TYPE_CHECKING
import cv2
import numpy as np
from pathlib import Path
from napari.layers import Image, Shapes
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (QHBoxLayout,
                            QCheckBox,
                            QVBoxLayout,
                            QPushButton,
                            QWidget,
                            QLabel,
                            QComboBox,
                            QSpinBox,
                            QFileDialog,
                            QLineEdit)
from superqt import QCollapsible
from skimage.color import rgb2gray
from skimage.io import imsave
from ._utils import make_widget, set_border


class PreprocessWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()

        # INITIALISE WIDGET
        # -----------------
        self.viewer = napari_viewer
        self.setLayout(QVBoxLayout())

        # ADDING PLUGIN TOOL NAME
        # -----------------------
        plugin_label_font = QFont()
        plugin_label_font.setPointSize(20)
        self.plugin_label = QLabel("Subject Set Preprocessing Tool")
        self.plugin_label.setFont(plugin_label_font)
        self.layout().addWidget(self.plugin_label)

        # ADDING IMAGE DROPDOWN SELECT
        # ----------------------------
        image_select_w, self.image_select = make_widget(annotation=Image, label="Image")
        image_select_w.setToolTip('The selected image used for preprocessing.')
        self.layout().addWidget(image_select_w)
        napari_viewer.layers.selection.events.changed.connect(self._on_selection)

        # TILING/ROI COLLAPSABLE
        # ----------------------
        self.tile_collapse = QCollapsible('Tiling/ROI Options', self)

        # ROI
        roi_label = QLabel("ROI")
        set_border(roi_label)
        self.tile_collapse.addWidget(roi_label)

        roi_widget = QWidget()
        roi_widget.setLayout(QHBoxLayout())
        set_border(roi_widget)

        self.roi_checkbox = QCheckBox()
        self.roi_checkbox.setChecked(True)
        set_border(self.roi_checkbox)
        roi_widget.layout().addWidget(self.roi_checkbox)
        self.roi_checkbox.toggled.connect(self._roi_on_click)

        self.roi_select = QComboBox()
        set_border(self.roi_select)
        roi_widget.layout().addWidget(self.roi_select)
        self.tile_collapse.addWidget(roi_widget)

        # TILING
        tiling_label = QLabel("Tiling")
        set_border(roi_label)
        self.tile_collapse.addWidget(tiling_label)

        tiling_widget = QWidget()
        tiling_widget.setLayout(QHBoxLayout())
        set_border(tiling_widget)

        self.tiling_checkbox = QCheckBox()
        set_border(self.tiling_checkbox)
        tiling_widget.layout().addWidget(self.tiling_checkbox)
        self.tiling_checkbox.toggled.connect(self._tiling_on_click)

        x_label = QLabel("X")
        set_border(x_label)
        tiling_widget.layout().addWidget(x_label)

        self.tiling_n_tiles_x = QSpinBox()
        self.tiling_n_tiles_x.setMinimum(1)
        set_border(self.tiling_n_tiles_x)
        tiling_widget.layout().addWidget(self.tiling_n_tiles_x)

        y_label = QLabel("Y")
        set_border(y_label)
        tiling_widget.layout().addWidget(y_label)

        self.tiling_n_tiles_y = QSpinBox()
        self.tiling_n_tiles_y.setMinimum(1)
        set_border(self.tiling_n_tiles_y)
        tiling_widget.layout().addWidget(self.tiling_n_tiles_y)

        self.tile_collapse.addWidget(tiling_widget)

        # TILING/ROI BUTTON
        self.preview_tiling_button = QPushButton("Preview Tiling/ROI")
        self.preview_tiling_button.clicked.connect(self._tiling_roi_preview)
        self.tile_collapse.addWidget(self.preview_tiling_button)
        set_border(self.preview_tiling_button)

        set_border(self.tile_collapse)
        self.layout().addWidget(self.tile_collapse)

        # SUBJECT SET COLLAPSABLE
        # -----------------------
        self.subject_collapse = QCollapsible("Subject Set Options", self)

        # SPAN
        span_widget = QWidget()
        span_widget.setLayout(QHBoxLayout())
        set_border(span_widget)
        span_label = QLabel("Span")
        span_widget.layout().addWidget(span_label)
        self.span_value = QSpinBox()
        span_widget.layout().addWidget(self.span_value)
        self.subject_collapse.addWidget(span_widget)

        # STEP
        step_widget = QWidget()
        step_widget.setLayout(QHBoxLayout())
        set_border(step_widget)
        step_label = QLabel("Step")
        step_widget.layout().addWidget(step_label)
        self.step_val = QSpinBox()
        step_widget.layout().addWidget(self.step_val)
        self.subject_collapse.addWidget(step_widget)

        # SUBJECT SET SIZE
        subject_set_size_widget = QWidget()
        subject_set_size_widget.setLayout(QHBoxLayout())
        set_border(subject_set_size_widget)
        subject_set_size_label = QLabel("Subject Set Size")
        subject_set_size_widget.layout().addWidget(subject_set_size_label)
        self.subject_set_size_value = QSpinBox()
        subject_set_size_widget.layout().addWidget(self.subject_set_size_value)
        self.subject_collapse.addWidget(subject_set_size_widget)

        # SUBJECT PREVIEW BUTTON
        self.subject_preview_button = QPushButton("Preview Subject Sets")
        set_border(self.subject_preview_button)
        self.subject_collapse.addWidget(self.subject_preview_button)
        self.subject_preview_button.clicked.connect(self._subject_set_preview)

        set_border(self.subject_collapse)
        self.layout().addWidget(self.subject_collapse)

        # OUTPUT DIRECTORY FILE DIALOGUE
        # ------------------------------
        # OPEN FILE DIALOGUE
        self._open_file_button = QPushButton("Output Directory")
        self._open_file_path = QLineEdit()
        open_file_widget = QWidget()
        open_file_widget.setLayout(QHBoxLayout())
        open_file_widget.layout().addWidget(self._open_file_button)
        open_file_widget.layout().addWidget(self._open_file_path)
        set_border(open_file_widget)
        self.layout().addWidget(open_file_widget)
        self._open_file_button.clicked.connect(self.open_file_dialogue)

        # ADDING PREPROCESS BUTTON AND CONNECTING TO FUNCTION
        # ----------------------------------------
        self.preprocess_button = QPushButton("Process")
        self.preprocess_button.clicked.connect(self._preprocess)
        self.layout().addWidget(self.preprocess_button)

    def _roi_on_click(self):
        if self.roi_checkbox.isChecked():
            self.tiling_checkbox.setChecked(False)

            self.roi_select.clear()

            for l in self.viewer.layers:
                if isinstance(l, Shapes):
                    self.roi_select.addItem(l.name)

        else:
            self.tiling_checkbox.setChecked(True)

    def _tiling_on_click(self):
        if self.tiling_checkbox.isChecked():
            self.roi_checkbox.setChecked(False)
        else:
            self.roi_checkbox.setChecked(True)

    def _tiling_roi_preview(self):
        """
        FUNCTION CALLED WHEN  DOING TILING/ROI PREVIEW


        :return:
        """
        if self.image_select.value.data is None:
            warnings.warn("Image not selected")
            return

        image = np.array(self.image_select.value.data)

        if image.ndim == 2:
            print(image.reshape((1,) + image.shape).shape)
        elif image.ndim == 3 & image.shape[2] == 3:
            image = rgb2gray(image)
            image = image.reshape((1,) + image.shape)
            print(image.shape)

        if self.roi_checkbox.isChecked():
            if self.roi_select.currentText() is None:
                warnings.warn("No Shapes ROI selected")
                return

            shapes = self.viewer.layers[self.roi_select.currentText()].data
            shape_types = self.viewer.layers[self.roi_select.currentText()].shape_type
            mask = np.zeros(image[0].shape)
            for shape_count, [shape, shape_type] in enumerate(zip(shapes,
                                                                  shape_types)):
                shape = np.array(shape[:, 1:], dtype=np.int32)
                shape = np.array([shape[i][::-1] for i in range(len(shape))])
                cv2.fillPoly(mask, [shape], 1)
            self.viewer.add_image(image * mask)
            return

        if self.tiling_checkbox.isChecked():
            print("tiling now")

            x = self.tiling_n_tiles_x.value()
            y = self.tiling_n_tiles_y.value()

            image_w_grid = []
            for i in range(len(image)):
                im = image[i]
                dx, dy = round(im.shape[0] / y), round(im.shape[1] / x)
                im[:, ::dy] = 0
                im[::dx, :] = 0
                image_w_grid.append(im)

            self.viewer.add_image(np.asarray(image_w_grid))
            return

    def _subject_set_preview(self):
        if self.image_select.value.data is None:
            warnings.warn("Image not selected")
            return

        span = self.span_value.value()
        step = self.step_val.value()
        subject_set_size = self.subject_set_size_value.value()

        image = np.array(self.image_select.value.data)

        starting_index = span * step

        subject_set = []
        for counter, list_start_abs in enumerate(
                range(starting_index, starting_index + len(image) - 2 * span * step, subject_set_size)):
            print("Subject:", list_start_abs)
            subject = []
            for i, idx in enumerate(range(list_start_abs - step * span, list_start_abs + (step * span) + 1, step)):
                print("Image:", idx)
                subject.append(image[idx])

            subject_set.append(subject)

        subject_set = np.asarray(subject_set)
        print(subject_set.shape)
        self.viewer.add_image(np.asarray(subject_set))

    def _on_selection(self, event=None):
        """
        Function simply updates the image and mask
        list to the available images and labels if
        a new image is added then list is updated.

        :param event: An instance of the user adding a new image or labels layer.
        :return: Updated image and mask layer list.
        """
        self.image_select.reset_choices(event)
        self._roi_on_click()

    def _preprocess(self):
        """
        FINAL PREPROCESS FUNCTION

        :return:
        """

        if self.image_select.value.data is None:
            warnings.warn("Image not selected")
            return

        image = np.array(self.image_select.value.data)

        if self.roi_checkbox.isChecked():
            if self.roi_select.currentText() == "":
                warnings.warn("No Shapes ROI selected")
                return

            shapes = self.viewer.layers[self.roi_select.currentText()].data

            output_path = self._open_file_path.text()
            if output_path == '':
                warnings.warn("Output directory not selected")
                return
            output_path += '/subject_sets'

            if not os.path.exists(output_path):
                os.mkdir(output_path)

            for shape in shapes:
                shape = np.array(shape[:, 1:], dtype=np.int32)
                print(shape.shape)
                print(shape)

                min_y, max_y = shape[0][0], shape[2][0]
                min_x, max_x = shape[0][1], shape[1][1]

                subject_path = output_path + '/image_x{0}_y{1}'.format(str(min_x).rjust(4, "0"),
                                                                       str(min_y).rjust(4, "0"))

                os.mkdir(subject_path)

                for i in range(len(image)):
                    imsave(subject_path + '/image_x{0}_y{1}_z{2}.jpeg'.format(str(min_x).rjust(4, "0"),
                                                                              str(min_y).rjust(4, "0"),
                                                                              str(i).rjust(4, "0"))
                           , image[i][min_y:max_y, min_x:max_x])

        if self.tiling_checkbox.isChecked():
            pass

    def open_file_dialogue(self):
        """
        If the `Open File` button is clicked a FielDialog will open
        and the users selected model will update the _open_file_path
        var.

        :return: path to the model.
        """
        output_path = QFileDialog.getExistingDirectory(self, 'Output Directory', str(Path))
        self._open_file_path.setText(output_path)
