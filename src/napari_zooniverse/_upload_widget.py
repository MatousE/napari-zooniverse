import os
import numpy as np
from napari.utils.notifications import show_info, show_error
from panoptes_client import Project, Panoptes
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (QHBoxLayout,
                            QPushButton,
                            QWidget,
                            QLabel,
                            QVBoxLayout,
                            QLineEdit,
                            QFileDialog,
                            QFrame,
                            QSpinBox)
from skimage.io import imread
from superqt import QCollapsible
from pathlib import Path
from ._utils import set_border, get_image_list, build_subject_set, initialise_subject_set


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class UploadWidget(QWidget):
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
        self.plugin_label = QLabel("Subject Set Uploading Tool")
        self.plugin_label.setFont(plugin_label_font)
        self.layout().addWidget(self.plugin_label)

        # OPEN SUBJECT SET
        # -------------------------
        self.open_subject_collapsible = QCollapsible("1. Select Subject Set", self)

        # FILE DIALOGUE
        self._open_dir_button = QPushButton("Subject Set Directory")
        self._open_dir_path = QLineEdit()
        open_dir_widget = QWidget()
        open_dir_widget.setLayout(QHBoxLayout())
        open_dir_widget.layout().addWidget(self._open_dir_button)
        open_dir_widget.layout().addWidget(self._open_dir_path)
        set_border(open_dir_widget)
        self.open_subject_collapsible.addWidget(open_dir_widget)
        self._open_dir_button.clicked.connect(self._open_dir_dialogue)

        # PREVIEW SUBJECT
        self.view_subject_set = QPushButton("View Subject Set")
        set_border(self.view_subject_set)
        self.open_subject_collapsible.addWidget(self.view_subject_set)
        self.view_subject_set.clicked.connect(self._view_subject_set_napari)

        set_border(self.open_subject_collapsible)
        self.layout().addWidget(self.open_subject_collapsible)

        # ZOONIVERSE CONNECTION DROPDOWN
        # ------------------------------
        self.zooniverse_collapsible = QCollapsible("2. Zooniverse Project Connection", self)

        # ZOONIVERSE USERNAME WIDGET
        zooniverse_username_label = QLabel("Zooniverse Username:")
        self.zooniverse_username = QLineEdit()
        zooniverse_username_widget = QWidget()
        zooniverse_username_widget.setLayout(QHBoxLayout())
        zooniverse_username_widget.layout().addWidget(zooniverse_username_label)
        zooniverse_username_widget.layout().addWidget(self.zooniverse_username)
        set_border(zooniverse_username_widget)
        self.zooniverse_collapsible.addWidget(zooniverse_username_widget)

        # ZOONIVERSE PASSWORD WIDGET
        zooniverse_password_label = QLabel("Zooniverse Password")
        self.zooniverse_password = QLineEdit()
        self.zooniverse_password.setEchoMode(QLineEdit.Password)
        zooniverse_password_widget = QWidget()
        zooniverse_password_widget.setLayout(QHBoxLayout())
        zooniverse_password_widget.layout().addWidget(zooniverse_password_label)
        zooniverse_password_widget.layout().addWidget(self.zooniverse_password)
        set_border(zooniverse_password_widget)
        self.zooniverse_collapsible.addWidget(zooniverse_password_widget)

        # ZOONIVERSE PROJECT WIDGET
        zooniverse_project_label = QLabel("Zooniverse Project:")
        self.zooniverse_project = QLineEdit()
        zooniverse_project_widget = QWidget()
        zooniverse_project_widget.setLayout(QHBoxLayout())
        zooniverse_project_widget.layout().addWidget(zooniverse_project_label)
        zooniverse_project_widget.layout().addWidget(self.zooniverse_project)
        set_border(zooniverse_project_widget)
        self.zooniverse_collapsible.addWidget(zooniverse_project_widget)

        # ZOONIVERSE LOGIN BUTTON
        self.zooniverse_login_button = QPushButton("Login")
        self.zooniverse_login_button.clicked.connect(self._login)
        self.zooniverse_collapsible.addWidget(self.zooniverse_login_button)

        set_border(self.zooniverse_collapsible)
        self.layout().addWidget(self.zooniverse_collapsible)

        # SUBJECT SET OPTIONS
        # -------------------
        self.subject_collapse = QCollapsible("3. Subject Set Options", self)

        # SPAN
        span_widget = QWidget()
        span_widget.setLayout(QHBoxLayout())
        set_border(span_widget)
        span_label = QLabel("Span")
        span_widget.layout().addWidget(span_label)
        self.span_value = QSpinBox()
        self.span_value.setValue(2)
        span_widget.layout().addWidget(self.span_value)
        self.subject_collapse.addWidget(span_widget)

        # STEP
        step_widget = QWidget()
        step_widget.setLayout(QHBoxLayout())
        set_border(step_widget)
        step_label = QLabel("Step")
        step_widget.layout().addWidget(step_label)
        self.step_value = QSpinBox()
        self.step_value.setValue(10)
        step_widget.layout().addWidget(self.step_value)
        self.subject_collapse.addWidget(step_widget)

        # SUBJECT SET SIZE
        subject_set_size_widget = QWidget()
        subject_set_size_widget.setLayout(QHBoxLayout())
        set_border(subject_set_size_widget)
        subject_set_size_label = QLabel("Subject Set Size")
        subject_set_size_widget.layout().addWidget(subject_set_size_label)
        self.subject_set_size_value = QSpinBox()
        self.subject_set_size_value.setValue(5)
        subject_set_size_widget.layout().addWidget(self.subject_set_size_value)
        self.subject_collapse.addWidget(subject_set_size_widget)

        # SUBJECT SET NAME
        subject_set_label = QLabel("Subject Set Name:")
        self.subject_set_name = QLineEdit()
        subject_set_name_widget = QWidget()
        subject_set_name_widget.setLayout(QHBoxLayout())
        subject_set_name_widget.layout().addWidget(subject_set_label)
        subject_set_name_widget.layout().addWidget(self.subject_set_name)
        set_border(subject_set_name_widget)
        self.subject_collapse.addWidget(subject_set_name_widget)

        # SUBJECT PREVIEW BUTTON
        self.subject_preview_button = QPushButton("Preview Subject Sets")
        set_border(self.subject_preview_button)
        self.subject_collapse.addWidget(self.subject_preview_button)
        self.subject_preview_button.clicked.connect(self._subject_set_preview)

        set_border(self.subject_collapse)
        self.layout().addWidget(self.subject_collapse)

        # UPLOAD SUBJECT SET BUTTON
        # -------------------------
        self.upload_button = QPushButton("Upload Subject")
        self.upload_button.clicked.connect(self._upload)
        self.layout().addWidget(self.upload_button)

    # TODO : UPLOAD SELECTED SUBJECT SET TO ZOONIVERSE PROJECT
    def _upload(self):
        print("napari has", len(self.viewer.layers), "layers")

        span = self.span_value.value()
        step = self.step_value.value()
        subject_set_size = self.subject_set_size_value.value()

        project = self.project

        file_list, n_files = get_image_list(self._open_dir_path.text())
        file_list.sort()

        *prefix_list, z_str = file_list[0].split('_z')

        minimum_z = int(z_str.split('.jpeg')[0])
        starting_index = span * step + minimum_z  # This is the first index that we can build a 5 slice subject from
        successful_uploads = 0
        for counter, list_start_abs in enumerate(
                range(starting_index, starting_index + n_files - 2 * span * step, subject_set_size)):
            print(f"\n*******\nStep {counter}")
            list_start = list_start_abs - minimum_z  # Make sure we subtract the offset
            # Perform some text manipulation to extract the x, y, z values from the file name
            file_name = os.path.split(file_list[list_start])[-1]  # Changed from [list_start_abs] - is this correct?!
            *prefix_list, z_str = file_name.split('_z')
            if len(prefix_list) > 1:
                prefix = "_z".join(prefix_list)
            else:
                prefix = prefix_list[0]
            z_start = int(z_str.split('.jpeg')[0])
            z_end = int(z_start) + subject_set_size - 1
            if int(z_end) >= (minimum_z + n_files - span * step):
                z_end = minimum_z + n_files - span * step - 1
                print(f"There are fewer than the requested {subject_set_size} subjects in this subject set")
            if int(z_start) < starting_index or int(z_end) > (
                    starting_index + n_files - span * step):  # Skip the highest and lowest z slices
                print(f"Skipping, can't build {2 * span + 1} slice subject from slice {z_start}")
                continue

            print(f"List start (abs): {list_start_abs}\n"
                  f"List start (centre index): {list_start}\n"
                  f"Z start: {z_start}\n"
                  f"Indices to be included: {z_start - 2 * step}, {z_start - 1 * step}, {z_start}, {z_start + 1 * step}, {z_start + 2 * step}\n\n"
                  f"Filename: {file_name}\n"
                  f"Start index: {starting_index}\n")
            list_end = z_end - minimum_z  # list_start + subject_set_size
            subject_set_name = f"{span}_{step}_{prefix}_z{z_start}-{z_end:04d}"
            print(subject_set_name)

            try:
                subject_set = initialise_subject_set(project, subject_set_name)
            except:
                print(f"Subject set name {subject_set_name} appears to already be taken, skipping\n\n")
                continue
                # TODO: output a logfile with skipped subject set names
            print(f"Creating subject set name {subject_set_name}\n\n")
            subjects = build_subject_set(project, file_list, list_start, list_end, span, step, testing=False)
            subject_set.add(subjects)
            successful_uploads += 1

        print(f"Done, I have processed {successful_uploads} subject sets")

    def _open_dir_dialogue(self):
        """
        If the `Open File` button is clicked a FielDialog will open
        and the users selected model will update the _open_file_path
        var.

        :return: path to the model.
        """
        output_path = QFileDialog.getExistingDirectory(self, 'Output Directory', str(Path))
        self._open_dir_path.setText(output_path)

    def _login(self):
        try:
            self.user = Panoptes.connect(username=self.zooniverse_username.text(),
                                         password=self.zooniverse_password.text())
            self.project = Project.find(slug=self.zooniverse_project.text())
            show_info("Connected to Zooniverse")
        except Exception as e:
            show_error("Exception {}".format(e))

    def _subject_set_preview(self):

        image = self.validate_directory()

        span = self.span_value.value()
        step = self.step_value.value()
        subject_set_size = self.subject_set_size_value.value()

        starting_index = span * step

        subject_set = []
        for counter, list_start_abs in enumerate(
                range(starting_index, starting_index + len(image) - 2 * span * step, subject_set_size)):
            subject = []
            for i, idx in enumerate(range(list_start_abs - step * span, list_start_abs + (step * span) + 1, step)):
                subject.append(image[idx])
            subject_set.append(subject)

        subject_set = np.asarray(subject_set)

        if len(self.subject_set_name.text()) == 0:
            self.subject_set_name.setText(os.path.basename(self._open_dir_path.text()))

        self.viewer.add_image(np.asarray(subject_set), name=self.subject_set_name.text())

    def _view_subject_set_napari(self):

        preview_image_stack = self.validate_directory()

        self.viewer.add_image(preview_image_stack, name=os.path.basename(self._open_dir_path.text()))

    def validate_directory(self):
        only_files = [f for f in os.listdir(self._open_dir_path.text()) if
                      os.path.isfile(os.path.join(self._open_dir_path.text(), f)) and
                      f.lower().endswith(('.jpeg', 'jpg'))]

        only_files.sort()

        if len(only_files) == 0:
            show_error("Directory selected contains no images of type .jpeg or .jpg")
            return

        preview_image_stack = []
        for file in only_files:
            file_path = os.path.join(self._open_dir_path.text(), file)
            preview_image_stack.append(imread(file_path))

        return np.asarray(preview_image_stack)
