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