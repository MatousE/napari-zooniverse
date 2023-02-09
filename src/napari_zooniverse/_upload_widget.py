from pathlib import Path
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (QHBoxLayout,
                            QPushButton,
                            QWidget,
                            QLabel,
                            QVBoxLayout,
                            QLineEdit,
                            QFileDialog,
                            QFrame,
                            QComboBox)
from ._utils import set_border


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

        # OPEN SUBJECT DIR DIALOGUE
        # -------------------------
        self._open_dir_button = QPushButton("Subject Set Directory")
        self._open_dir_path = QLineEdit()
        open_dir_widget = QWidget()
        open_dir_widget.setLayout(QHBoxLayout())
        open_dir_widget.layout().addWidget(self._open_dir_button)
        open_dir_widget.layout().addWidget(self._open_dir_path)
        set_border(open_dir_widget)
        self.layout().addWidget(open_dir_widget)
        self._open_dir_button.clicked.connect(self._open_dir_dialogue)

        # ZOONIVERSE USERNAME WIDGET
        zooniverse_username_label = QLabel("Zooniverse Username:")
        self.zooniverse_username = QLineEdit()
        zooniverse_username_widget = QWidget()
        zooniverse_username_widget.setLayout(QHBoxLayout())
        zooniverse_username_widget.layout().addWidget(zooniverse_username_label)
        zooniverse_username_widget.layout().addWidget(self.zooniverse_username)
        set_border(zooniverse_username_widget)
        self.layout().addWidget(zooniverse_username_widget)

        # ZOONIVERSE PASSWORD WIDGET
        zooniverse_password_label = QLabel("Zooniverse Password")
        self.zooniverse_password = QLineEdit()
        self.zooniverse_password.setEchoMode(QLineEdit.Password)
        zooniverse_password_widget = QWidget()
        zooniverse_password_widget.setLayout(QHBoxLayout())
        zooniverse_password_widget.layout().addWidget(zooniverse_password_label)
        zooniverse_password_widget.layout().addWidget(self.zooniverse_password)
        set_border(zooniverse_password_widget)
        self.layout().addWidget(zooniverse_password_widget)

        # ZOONIVERSE LOGIN BUTTON
        self.zooniverse_login_button = QPushButton("Login")
        self.zooniverse_login_button.clicked.connect(self._login)
        self.layout().addWidget(self.zooniverse_login_button)

        # ZOONIVERSE PROJECT DROP-DOWN
        zooniverse_project_label = QLabel("Zooniverse Projects")
        self.zooniverse_project_combobox = QComboBox()
        zooniverse_project_widget = QWidget()
        zooniverse_project_widget.setLayout(QHBoxLayout())
        zooniverse_project_widget.layout().addWidget(zooniverse_project_label)
        zooniverse_project_widget.layout().addWidget(self.zooniverse_project_combobox)
        set_border(zooniverse_project_widget)
        self.layout().addWidget(zooniverse_project_widget)

        # SUBJECT SET NAME
        subject_set_label = QLabel("Subject Set Name:")
        self.subject_set_name = QLineEdit()
        subject_set_name_widget = QWidget()
        subject_set_name_widget.setLayout(QHBoxLayout())
        subject_set_name_widget.layout().addWidget(subject_set_label)
        subject_set_name_widget.layout().addWidget(self.subject_set_name)
        set_border(subject_set_name_widget)
        self.layout().addWidget(subject_set_name_widget)

        # UPLOAD SUBJECT SET BUTTON
        # -------------------------
        self.upload_button = QPushButton("Upload Subject")
        self.upload_button.clicked.connect(self._upload)
        self.layout().addWidget(self.upload_button)

    def _upload(self):
        print("napari has", len(self.viewer.layers), "layers")

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
        pass
