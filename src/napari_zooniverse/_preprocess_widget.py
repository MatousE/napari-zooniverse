from typing import TYPE_CHECKING
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
        set_border(self.tiling_n_tiles_x)
        tiling_widget.layout().addWidget(self.tiling_n_tiles_x)

        y_label = QLabel("Y")
        set_border(y_label)
        tiling_widget.layout().addWidget(y_label)

        self.tiling_n_tiles_y = QSpinBox()
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
        self.span_value = QSpinBox()
        step_widget.layout().addWidget(self.span_value)
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
        self._open_file_button = QPushButton("Open File")
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
        image = self.image_select.value.data

        if self.roi_checkbox.isChecked():
            rois = self.viewer.layers[self.roi_select.currentText()].data

            pass
        else:
            pass

        print("preview_on_click")


    def _subject_set_preview(self):
        pass

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

        print("napari has", len(self.viewer.layers), "layers")

    def open_file_dialogue(self):
        """
        If the `Open File` button is clicked a FielDialog will open
        and the users selected model will update the _open_file_path
        var.

        :return: path to the model.
        """
        filename = QFileDialog.getOpenFileName(self, 'Open File', '/', '*.json')
        self._open_file_path.setText(filename[0])
