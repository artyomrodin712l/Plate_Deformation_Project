"""
Class for drawing graphs using matplotlib.

"""

from PyQt5.QtWidgets import QSizePolicy

import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class MatplotlibCanvas(FigureCanvasQTAgg):
    """
    Canvas for drawing graphs using matplotlib.

    Attributes
    ----------
    fig : Figure
        The top level container for all the plot elements.
    ax : Axes
        Used for creating and editing graphs.

    """

    def __init__(self) -> None:
        matplotlib.rcParams.update({"font.size": 10})
        self.fig: Figure = Figure(constrained_layout=True)
        self.ax: Axes = self.fig.subplots()
        super().__init__(self.fig)
        FigureCanvasQTAgg.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        FigureCanvasQTAgg.updateGeometry(self)
