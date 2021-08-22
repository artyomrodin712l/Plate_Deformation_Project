"""
Class that wraps working with graphs using the
matplotlib library and displays them in the GUI.

"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from matplotlib.axes import Axes

from src.ui.widgets.MatplotlibCanvas import MatplotlibCanvas


class MatplotlibWidget(QWidget):
    """
    Widget that wraps working with graphs using the
    matplotlib library and displays them in the GUI.

    Parameters
    ----------
    parent : QWidget
        Parent element that contains this element.

    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__canvas: MatplotlibCanvas = MatplotlibCanvas()
        self.__vbl = QVBoxLayout()
        self.__vbl.setContentsMargins(0, 0, 0, 0)
        self.__vbl.addWidget(self.__canvas)
        self.setLayout(self.__vbl)

        self.__dpi: int = max(self.logicalDpiX(), self.logicalDpiY())
        self.__canvas.fig.set_dpi(self.__dpi)

    def update_widget(self, width: int, height: int) -> None:
        """
        Updates the graph (MatplotlibWidget) size when the parent widget is resized.

        Parameters
        ----------
        width : int
            Width of the parent widget.
        height : int
            Height of the parent widget.

        """
        self.setFixedSize(width, height)
        self.__canvas.fig.set_size_inches(width * 0.95 / self.__dpi, height * 0.96 / self.__dpi)

    @property
    def ax(self) -> Axes:
        """
        Property that returns the axis for drawing graphs.

        Returns
        -------
        Axes
           The axes for drawing graphs.

        """
        return self.__canvas.ax

    def clear(self) -> None:
        """
        Completely clears the chart widget.

        """
        if len(self.ax.images) > 0 and self.ax.images[-1].colorbar is not None:
            self.ax.images[-1].colorbar.remove()
        self.ax.clear()

    def draw(self) -> None:
        """
        Draws a graph in the GUI.

        """
        self.__canvas.draw()
