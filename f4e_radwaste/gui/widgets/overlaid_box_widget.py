# pylint: disable=E1101
from enum import Enum, auto

import pyvista as pv
from qtpy import QtWidgets

from f4e_radwaste.gui.widgets.box_generated_widget import BoxGeneratedWidget
from f4e_radwaste.gui.widgets.custom_box_loaded_widget import (
    CustomBoxLoadedWidget,
)
from f4e_radwaste.gui.widgets.no_box_loaded_widget import no_box_loaded_widget


class WindowKeys(Enum):
    NO_BOX_LOADED = auto()
    BOX_GENERATED = auto()
    CUSTOM_BOX_LOADED = auto()


class OverlaidBoxWidget(QtWidgets.QWidget):
    """
    The left side of the window. Three different widgets are built and hidden.
    One of them will be displayed depending on if there is no radwaste box or if
    it has been generated by the GUI or loaded as an STL.
    """

    def __init__(self, parent, manager):
        super().__init__(parent=parent)
        self.box_grid = pv.StructuredGrid()
        self.setLayout(QtWidgets.QHBoxLayout())
        self._sub_windows = {
            WindowKeys.NO_BOX_LOADED: no_box_loaded_widget(manager=manager),
            WindowKeys.BOX_GENERATED: BoxGeneratedWidget(manager=manager),
            WindowKeys.CUSTOM_BOX_LOADED: CustomBoxLoadedWidget(manager=manager),
        }
        for widget in self._sub_windows.values():
            self.layout().addWidget(widget)
        self.show_no_box_loaded_widget()

    def show_no_widget(self):
        for widget in self._sub_windows.values():
            widget.setVisible(False)

    def show_no_box_loaded_widget(self):
        self.show_no_widget()
        self._sub_windows[WindowKeys.NO_BOX_LOADED].setVisible(True)

    def show_box_generated_widget(self):
        self.show_no_widget()
        self._sub_windows[WindowKeys.BOX_GENERATED].setVisible(True)

    def show_custom_box_loaded_widget(self):
        self.show_no_widget()
        self._sub_windows[WindowKeys.CUSTOM_BOX_LOADED].setVisible(True)

    def set_box_parameters_to_fit_mesh(self, mesh):
        if mesh is None:
            return
        bounds = mesh.bounds
        box_generated_widget = self._sub_windows[WindowKeys.BOX_GENERATED]
        box_generated_widget.origin_x.setValue(bounds[0])
        box_generated_widget.size_x.setValue(bounds[1] - bounds[0])
        box_generated_widget.origin_y.setValue(bounds[2])
        box_generated_widget.size_y.setValue(bounds[3] - bounds[2])
        box_generated_widget.origin_z.setValue(bounds[4])
        box_generated_widget.size_z.setValue(bounds[5] - bounds[4])

    def generate_box_according_to_box_input_lines(self):
        box_generated_widget = self._sub_windows[WindowKeys.BOX_GENERATED]
        origin = (
            box_generated_widget.origin_x.value(),
            box_generated_widget.origin_y.value(),
            box_generated_widget.origin_z.value(),
        )
        size = (
            box_generated_widget.size_x.value(),
            box_generated_widget.size_y.value(),
            box_generated_widget.size_z.value(),
        )
        rotation = (
            box_generated_widget.rot_x.value(),
            box_generated_widget.rot_y.value(),
            box_generated_widget.rot_z.value(),
        )
        self.box_grid = pv.Box(
            (
                origin[0],
                origin[0] + size[0],
                origin[1],
                origin[1] + size[1],
                origin[2],
                origin[2] + size[2],
            )
        )
        assert self.box_grid is not None
        self.box_grid.rotate_x(rotation[0], inplace=True)
        self.box_grid.rotate_y(rotation[1], inplace=True)
        self.box_grid.rotate_z(rotation[2], inplace=True)

    def load_stl_as_box(self, stl_file_path):
        self.box_grid = pv.read(stl_file_path)
