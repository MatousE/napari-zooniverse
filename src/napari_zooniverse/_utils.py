import os
from qtpy.QtWidgets import (QLabel,
                            QWidget,
                            QHBoxLayout)
from magicgui.widgets import create_widget
from panoptes_client import Project, Panoptes, Subject, SubjectSet


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


def get_image_list(input_directory):
    file_list = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if
                 os.path.isfile(os.path.join(input_directory, f)) and
                 f.lower().endswith(('.jpeg', 'jpg'))]

    n_files = len(file_list)
    print(f"There are {n_files} jpg files in the directory {input_directory}")
    return file_list, n_files


def build_subject(project, file_list, centre_idx, span, step):
    subject = Subject()  # Inititialise a subject
    subject.links.project = project  # ...attach it to a project
    subject.metadata['Subject ID'] = centre_idx - step * span + 1  # Add the names of the images

    # For loop to attach the images to the subject one-by-one
    for i, idx in enumerate(range(centre_idx - step * span, centre_idx + (step * span) + 1, step)):
        fname = str(file_list[idx])
        print("Attaching %s to subject %d" % (os.path.basename(fname), centre_idx - step * span + 1))
        subject.add_location(fname)
        subject.metadata['Image %d' % i] = os.path.basename(fname)
    subject.metadata['default_frame'] = span + 1  # We want people to annotate the middle image

    # Metadata from here should be changed according to the data
    subject.metadata['Microscope'] = 'SBF SEM (with FCC)'
    subject.metadata['Raw XY resolution (nm)'] = 5
    subject.metadata['Raw Z resolution (nm)'] = 50
    subject.metadata['Scaling factor'] = 2
    subject.metadata['jpeg quality (%)'] = 90
    subject.metadata['Attribution'] = 'Matt Russell'
    subject.metadata['Description'] = 'MP009_FCC_5-161118_Cell1registered-binnedx2 (HeLa)'
    print("Starting to save")
    print(subject)
    subject.save()
    print("Subject saved")

    return subject


def initialise_subject_set(project, subject_name):
    subject_set = SubjectSet()
    subject_set.links.project = project
    subject_set.display_name = subject_name
    subject_set.save()
    return subject_set


def build_subject_set(project, file_list, file_idx_start, file_idx_stop, span, step, testing=False):
    print(f"project {project}\n",
          f"file_idx_start {file_idx_start}\n",
          f"file_idx_stop {file_idx_stop}\n",
          f"span {span}\n",
          f"step {step}")
    print(f"Building subject set from files {file_idx_start}-{file_idx_stop}")
    subjects = []
    min_idx = 0
    max_idx = len(file_list) - span * step

    for centre_idx in range(max(min_idx, file_idx_start), min(max_idx, file_idx_stop) + 1):
        if testing:
            print(f"Testing for subject centred on file {centre_idx} in the list")
        else:
            subject = build_subject(project, file_list, centre_idx, span, step)
            subjects.append(subject)
    return subjects
