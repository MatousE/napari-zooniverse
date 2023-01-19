"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import (QHBoxLayout,
                            QPushButton,
                            QWidget,
                            QLabel)

if TYPE_CHECKING:
    import napari


class PreprocessWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.plugin_label = QLabel("Example Function")

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        # WIDGET FOR BUTTON WITH LABEL
        # ------------------------------------
        larger_widget = QWidget()
        larger_widget.setLayout(QHBoxLayout())
        larger_widget.layout().addWidget(self.plugin_label)
        larger_widget.layout().addWidget(btn)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.plugin_label)
        self.layout().addWidget(btn)

        self.layout().addWidget(larger_widget)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

