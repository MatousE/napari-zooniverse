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
                            QSpinBox)
from superqt import QCollapsible
from ._utils import set_border


class VisualiseClassificationWidget(QWidget):
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
        self.plugin_label = QLabel("Visualise Classification Tool")
        self.plugin_label.setFont(plugin_label_font)
        self.layout().addWidget(self.plugin_label)

        # OPEN ZOONIVERSE CSV
        # -------------------------
        self.zooniverse_csv_collapsible = QCollapsible("1. Select Zooniverse CSV", self)

        # FILE DIALOGUE
        self._open_csv_button = QPushButton("Zooniverse CSV")
        self._open_csv_path = QLineEdit()
        open_csv_widget = QWidget()
        open_csv_widget.setLayout(QHBoxLayout())
        open_csv_widget.layout().addWidget(self._open_csv_button)
        open_csv_widget.layout().addWidget(self._open_csv_path)
        set_border(open_csv_widget)
        self.zooniverse_csv_collapsible.addWidget(open_csv_widget)
        self._open_csv_button.clicked.connect(self._open_csv_dialogue)

        set_border(self.zooniverse_csv_collapsible)
        self.layout().addWidget(self.zooniverse_csv_collapsible)

    def _open_csv_dialogue(self):
        """
        If the `Open File` button is clicked a FielDialog will open
        and the users selected model will update the _open_file_path
        var.

        :return: path to the model.
        """
        qfd = QFileDialog()
        path = str(Path)
        file_filter = "*.csv"

        zooniverse_file = QFileDialog.getOpenFileName(qfd, "Zooniverse CSV File", path, file_filter)

        self._open_csv_path.setText(zooniverse_file[0])


        print(zooniverse_file)