"""
Class abstraction over all computations of plate bending
by the finite element method.

""" 

from typing import Final, List

import numpy as np

from src.fem.Node import Node
from src.fem.Element import Element


class FEM:
    """
    Сlass that uses the finite element method to calculate the plate
    bend based on the parameters obtained.

    Parameters
    ----------
    width : non-negative int
        Plate width.
    height : non-negative int
        Plate height.
    thickness : non-negative int
        Plate thickness.
    pressure : non-negative float
        Pressure on the plate from above.
    young : non-negative int
        Young's modulus (elasticity) of material of element.
    poisson : non-negative float
        Poisson ratio of material of element.
    h_element_count : non-negative int
        The number of finite elements horizontally.
    v_element_count : non-negative int
        The number of finite elements vertically.
    """

    def __init__(
        self,
        width: int,
        height: int,
        thickness: int,
        pressure: float,
        young: int,
        poisson: float,
        h_element_count: int,
        v_element_count: int,
    ) -> None:
        self.__width: Final = width
        self.__height: Final = height
        self.__thickness: Final = thickness
        self.__pressure: Final = pressure
        self.__young: Final = young
        self.__poisson: Final = poisson
        self.__h_element_count: Final = h_element_count
        self.__v_element_count: Final = v_element_count

        self.__h_node_count: int
        self.__v_node_count: int
        self.__element_width: float
        self.__element_height: float
        self.__vector_x: np.ndarray
        self.__vector_y: np.ndarray
        self.__nodes: List[Node]
        self.__elements: List[Element]
        self.__global_stiffness_matrix_size: int
        self.__global_stiffness_matrix: np.ndarray
        self.__global_nodal_forces: np.ndarray
        self.__solution: np.ndarray
        self.__nodes_deformation: np.ndarray

    def __determine_node_count(self) -> None:
        self.__h_node_count = self.__h_element_count + 1
        self.__v_node_count = self.__v_element_count + 1

    def __determine_element_size(self) -> None:
        self.__element_width = self.__width / self.__h_element_count
        self.__element_height = self.__height / self.__v_element_count

    def __set_element_parameters(self) -> None:
        Element.set_parameters(
            self.__element_width,
            self.__element_height,
            self.__thickness,
            self.__pressure,
            self.__young,
            self.__poisson,
        )

    def __determine_coordinate_vectors(self) -> None:
        self.__vector_x = np.linspace(0, self.__width, self.__h_node_count)
        self.__vector_y = np.linspace(0, self.__height, self.__v_node_count)

    def __create_node_list(self) -> None:
        self.__nodes = []
        for i, x in enumerate(self.__vector_x):
            for j, y in enumerate(self.__vector_y):
                if (
                    x == 0
                    and y == 0
                    or x == 0
                    and y == self.__height
                    #or x == self.__width
                    #and y == 0
                    or x == self.__width
                    and y == self.__height
                ):
                    node = Node(i * self.__v_node_count + j, x, y, True)
                else:
                    node = Node(i * self.__v_node_count + j, x, y)
                self.__nodes.append(node)

    def __create_element_list(self) -> None:
        self.__elements = []
        for i in range(self.__h_element_count):
            for j in range(self.__v_element_count):
                self.__elements.append(
                    Element(
                        (
                            self.__nodes[i * self.__v_node_count + j],
                            self.__nodes[i * self.__v_node_count + j + 1],
                            self.__nodes[(i + 1) * self.__v_node_count + j + 1],
                            self.__nodes[(i + 1) * self.__v_node_count + j],
                        )
                    )
                )

    def create_mesh(self) -> None:
        """
        Creates a plate mesh.

        """
        self.__determine_node_count()
        self.__determine_element_size()
        self.__set_element_parameters()
        self.__determine_coordinate_vectors()
        self.__create_node_list()
        self.__create_element_list()

    def __add_local_stiffness_matrix_to_global(
        self, nodes: tuple, local_stiffness_matrix: np.ndarray
    ) -> None:
        for i in range(Element.NODE_COUNT):
            for j in range(Element.NODE_COUNT):
                global_h_slice = slice(
                    Node.DOF_COUNT * nodes[i].index, Node.DOF_COUNT * (nodes[i].index + 1),
                )
                global_v_slice = slice(
                    Node.DOF_COUNT * nodes[j].index, Node.DOF_COUNT * (nodes[j].index + 1),
                )

                local_h_slice = slice(Node.DOF_COUNT * i, Node.DOF_COUNT * (i + 1))
                local_v_slice = slice(Node.DOF_COUNT * j, Node.DOF_COUNT * (j + 1))

                self.__global_stiffness_matrix[
                    global_h_slice, global_v_slice
                ] += local_stiffness_matrix[local_h_slice, local_v_slice]

    def __create_global_stiffness_matrix(self) -> None:
        self.__global_stiffness_matrix_size = (
            Node.DOF_COUNT * self.__h_node_count * self.__v_node_count
        )
        self.__global_stiffness_matrix = np.zeros(
            (self.__global_stiffness_matrix_size, self.__global_stiffness_matrix_size)
        )
        for elem in self.__elements:
            self.__add_local_stiffness_matrix_to_global(
                elem.nodes, Element.get_local_stiffness_matrix()
            )

    def __add_local_nodal_forces_to_global(
        self, nodes: tuple, local_nodal_forces: np.ndarray
    ) -> None:
        for i, node in enumerate(nodes):
            if not node.fixed:
                nodal_forces_slice = slice(
                    Node.DOF_COUNT * node.index, Node.DOF_COUNT * (node.index + 1)
                )
                local_nodal_forces_slice = slice(Node.DOF_COUNT * i, Node.DOF_COUNT * (i + 1))
                self.__global_nodal_forces[nodal_forces_slice] += local_nodal_forces[
                    local_nodal_forces_slice
                ]

    def __create_nodal_forces(self) -> None:
        self.__global_nodal_forces = np.zeros(self.__global_stiffness_matrix_size)
        for elem in self.__elements:
            self.__add_local_nodal_forces_to_global(
                elem.nodes, Element.get_local_nodal_force_matrix()
            )

    def __add_fixation(self) -> None:
        for node in self.__nodes:
            if node.fixed:
                for j in range(Node.DOF_COUNT):
                    t = Node.DOF_COUNT * node.index + j
                    self.__global_stiffness_matrix[t] = 0
                    self.__global_stiffness_matrix[:, t] = 0
                    self.__global_stiffness_matrix[t, t] = 1

    def __solve_equation(self) -> None:
        self.__solution = np.linalg.solve(
            self.__global_stiffness_matrix, self.__global_nodal_forces
        )

    def __determine_nodal_deformation(self) -> None:
        self.__nodes_deformation = self.__solution.reshape(-1, Node.DOF_COUNT)[:, 0]

    def __solution_processing(self) -> None:
        self.__determine_nodal_deformation()

    def calculate(self) -> None:
        """
        Performs a finite element method calculation.

        """
        self.__create_global_stiffness_matrix()
        self.__create_nodal_forces()
        self.__add_fixation()
        self.__solve_equation()
        self.__solution_processing()

    @property
    def width(self) -> int:
        """
        Property that returns the width of the plate.

        Returns
        -------
        non-negative int
            Plate width.

        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Property that returns the height of the plate.

        Returns
        -------
        non-negative int
            Plate height.

        """
        return self.__height

    @property
    def nodes(self) -> List[Node]:
        """
        Property that returns nodes of the mesh.

        Returns
        -------
        ndarray
            Nodes of the mesh.

        """
        return self.__nodes

    @property
    def elements(self) -> List[Element]:
        """
        Property that returns elements of the mesh.

        Returns
        -------
        ndarray
            Elements of the mesh.

        """
        return self.__elements

    def get_nodes_deformation_for_plot(self) -> np.ndarray:
        """
        Returns deformations of nodes.

        Returns
        -------
        ndarray
            Deformations of nodes in the form of a matrix.

        """
        return self.__nodes_deformation.reshape(self.__h_node_count, self.__v_node_count).T

    def get_max_node_deformation(self) -> float:
        """
        Returns max deformation of nodes.

        Returns
        -------
        float
            Max deformation of nodes.

        """
        return np.max(self.__nodes_deformation)
