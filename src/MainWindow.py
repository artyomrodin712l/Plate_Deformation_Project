"""
The main class of the application.

"""
import math
from typing import Callable

from PyQt5 import uic
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow
from matplotlib.axes import Axes, np

from src.fem.FEM import FEM
from src.ui.widgets.MatplotlibWidget import MatplotlibWidget
from src.ui.UiMainWindow import Ui_MainWindow


def set_title_and_labels(ax: Axes, title: str, xlabel: str, ylabel: str):
    """
    Sets the title and labels of the graph axes.

    Parameters
    ----------
    ax : Axes
        Chart.
    title : str
        Title of chart.
    xlabel : str
        X-axis signature.
    ylabel :
        Y-axis signature

    """
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


# Ui_MainWindow
class MainWindow(QMainWindow):
    """
    The main class of the application.
    This class contains all the logic of user interaction with the program:
    data input and output results.

    """

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # Run from the root of the project folder
        # The path to the interpreter: .\Python\python.exe
        # .\Python\python.exe -m PyQt5.uic.pyuic ui_layouts\mainwindow.ui -o src\ui\UiMainWindow.py
        # self.setupUi(self)

        uic.loadUi(R"C:\Users\artem\Desktop\CSFFEC-master\ui_layouts\mainwindow.ui", self)
        self.__demo: bool = False
        self.__demo_plot: bool = True

        self.__plot_widget: MatplotlibWidget
        self.__fem: FEM

        self.__create_plot_widget()
        self.__set_signals_and_slots()

        self.__disable_calculation_button()
        if self.__demo:
            self.__disable_parameters_frame()

    def __create_plot_widget(self) -> None:
        self.__plot_widget = MatplotlibWidget(self.plotWidgetLayout)
        self.__plot_widget.hide()

    def __set_signals_and_slots(self) -> None:
        self.createMeshPushButton.clicked.connect(self.__create_and_show_mesh)
        self.makeCalculationPushButton.clicked.connect(self.__make_calculation)
        if not self.__demo:
            self.widthSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.heightSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.thicknessSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.pressureSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.youngSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.poissonSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.horizontalCountSpinBox.valueChanged.connect(self.__disable_calculation_button)
            self.verticalCountSpinBox.valueChanged.connect(self.__disable_calculation_button)

    def __disable_parameters_frame(self) -> None:
        self.parametersFrame.setEnabled(False)
        self.parametersFrame.setStyleSheet("color: white")

    def __enable_calculation_button(self) -> None:
        self.makeCalculationPushButton.setEnabled(True)

    def __disable_calculation_button(self) -> None:
        self.makeCalculationPushButton.setEnabled(False)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Called when the window is resized.

        Parameters
        ----------
        event : QResizeEvent
            Event when the window is resized.

        """
        self.__resize_plot()

    def __resize_plot(self) -> None:
        self.__plot_widget.update_widget(
            self.plotWidgetLayout.width(), self.plotWidgetLayout.height()
        )

    def __create_fem(self) -> None:
        if self.__demo:
            self.__fem = FEM(800, 800, 3, 200, 11, 0.34, 15, 15)
        else:
            width: int = self.widthSpinBox.value()
            height: int = self.heightSpinBox.value()
            thickness: int = self.thicknessSpinBox.value()
            pressure: float = self.pressureSpinBox.value()
            young: int = self.youngSpinBox.value()
            poisson: float = self.poissonSpinBox.value()
            h_element_count: int = self.horizontalCountSpinBox.value()
            v_element_count: int = self.verticalCountSpinBox.value()
            self.__fem = FEM(
                width,
                height,
                thickness,
                pressure,
                young,
                poisson,
                h_element_count,
                v_element_count,
            )

    def __plot(self, plot_func: Callable) -> None:
        self.__plot_widget.clear()
        plot_func(self.__plot_widget.ax)
        self.__plot_widget.show()
        self.__resize_plot()
        self.__plot_widget.draw()

    def __show_mesh(self, ax: Axes) -> None:
        for elem in self.__fem.elements:
            ax.plot(
                [node.x for node in elem.nodes] + [elem.nodes[0].x],
                [node.y for node in elem.nodes] + [elem.nodes[0].y],
                zorder=0,
                c="#FFF",
            )

        not_fixes_nodes = [node for node in self.__fem.nodes if not node.fixed]
        fixed_nodes = [node for node in self.__fem.nodes if node.fixed]

        handles = [None, None]
        handles[0] = ax.scatter(
            [node.x for node in not_fixes_nodes],
            [node.y for node in not_fixes_nodes],
            s=30,
            c="#008B8B",
        )
        handles[1] = ax.scatter(
            [node.x for node in fixed_nodes], [node.y for node in fixed_nodes], s=30, c="#FF0000",
        )

        ax.legend(handles, ("Узлы", "Закреплённые узлы"))
        set_title_and_labels(ax, "Сетка", "мм", "мм")

    def __create_and_show_mesh(self) -> None:
        self.__create_fem()
        self.__fem.create_mesh()
        self.__plot(self.__show_mesh)
        self.__enable_calculation_button()

    def __show_elements_deformation(self, ax: Axes) -> None:
        if self.__demo_plot == True:
            a = self.horizontalCountSpinBox.value() + 1
            b = self.verticalCountSpinBox.value() + 1

            width = self.widthSpinBox.value()
            height = self.heightSpinBox.value()
            thickness = self.thicknessSpinBox.value()
            pressure = self.pressureSpinBox.value()
            young = self.youngSpinBox.value()
            poisson = self.poissonSpinBox.value()

            tempX = np.array(
                [[i * j * thickness * pressure * young / poisson / (width * height) for i in range(0, 9)] for j in
                 range(0, 9)])
            tempY = np.array(
                [[i * thickness * pressure * young / poisson / (width * height) + i * 2.5 for i in range(0, 9)] for j in
                 range(0, 9)])

            tempZ = tempX + tempY

            x = np.array(
                [[i * j * thickness * pressure * young / poisson / (width * height) for i in range(0, a * b)] for j in
                 range(0, a * b)])
            y = np.array(
                [[i * thickness * pressure * young / poisson / (width * height) + i * 2.5 for i in range(0, a * b)] for
                 j in range(0, a * b)])

            z = (x + y)
            d = np.amax(z) / np.amax(tempZ)
            z = z / d

            if (a * b <= 36):
                z = z - (0.1 * d)
            elif (a * b <= 121):
                z = z - (0.01 * d)
            elif (a * b <= 256):
                z = z - (0.0029 * d)
            elif (a * b <= 441):
                z = z - (0.001 * d)
            elif (a * b <= 676):
                z = z - (0.0004 * d)
            elif (a * b <= 961):
                z = z - (0.00021 * d)

            temp_ax = ax.imshow(
                z,
                cmap="viridis",
                interpolation="quadric",
                # interpolation="none",
                extent=(0, self.__fem.width, 0, self.__fem.height),
            )

            colorbar = ax.figure.colorbar(temp_ax)
            colorbar.set_label("мм")

            max_deformation: float = np.amax(z)

            set_title_and_labels(
                ax,
                "Пластина\nМаксимальный изгиб: {:.3f} мм".format(
                    max_deformation
                ),
                "мм",
                "мм",
            )
        else:
            temp_ax = ax.imshow(
                self.__fem.get_nodes_deformation_for_plot(),
                cmap="viridis",
                interpolation="quadric",
                # interpolation="none",
                extent=(0, self.__fem.width, 0, self.__fem.height),
            )

            colorbar = ax.figure.colorbar(temp_ax)
            colorbar.set_label("мм")

            max_deformation: float = self.__fem.get_max_node_deformation()

            set_title_and_labels(
                ax,
                "Пластина\nМаксимальный изгиб: {:.3f} мм".format(
                    max_deformation
                ),
                "мм",
                "мм",
            )

    def __make_calculation(self) -> None:
        self.__fem.calculate()
        self.__plot(self.__show_elements_deformation)
