"""
The class contains element parameters and calculates the
necessary data based on them to use the finite element method.

"""

from typing import Final

import numpy as np

from src.fem.Node import Node


class Element:
    """
    The class contains element parameters and calculates the
    necessary data based on them to use the finite element method.
    The class is a finite element of the rectangle type with four nodes.

    Parameters
    ----------
    nodes : tuple
        Contains four elements of the Node class.

    Attributes
    ----------
    nodes : tuple
        Contains four elements of the Node class.

    Class Attributes
    ----------------
    NODE_COUNT : int
        Number of nodes.
    width : non-negative float
        Width of element.
    height : non-negative float
        Height of element.
    thickness : non-negative int
        Thickness of element.
    pressure : non-negative float
        Pressure on the plate from above.
    young : non-negative int
        Young's modulus (elasticity) of material of element.
    poisson : non-negative float
        Poisson ratio of material of element.

    """

    NODE_COUNT: Final = 4

    width: float
    height: float
    thickness: int
    pressure: float
    young: int
    poisson: float

    def __init__(self, nodes: tuple) -> None:
        self.nodes: Final = nodes

    @staticmethod
    def set_parameters(
        width: float, height: float, thickness: int, pressure: float, young: int, poisson: float
    ) -> None:
        """
        Sets the parameters of the element.

        Parameters
        ----------
        width : non-negative float
            Width of element.
        height : non-negative float
            Height of element.
        thickness : non-negative int
            Thickness of element.
        pressure : float
            Pressure on the plate from above.
        young : non-negative int
            Young's modulus (elasticity) of material of element.
        poisson : non-negative float
            Poisson ratio of material of element.

        """
        Element.width = width
        Element.height = height
        Element.thickness = thickness
        Element.pressure = pressure
        Element.young = young
        Element.poisson = poisson

    @staticmethod
    def get_local_stiffness_matrix() -> np.ndarray:
        """
        Calculates the local stiffness matrix.

        Returns
        -------
        ndarray
            Local stiffness matrix.

        """
        a = Element.width
        b = Element.height
        alpha = a / b
        beta = b / a

        e = Element.young
        u = Element.poisson

        coef = e * Element.thickness ** 3 / (48 * (1 - u ** 2) * a * b)

        i1 = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        i2 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        i3 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]])

        k11 = np.array(
            [
                [
                    4 * (beta ** 2 + alpha ** 2) + (2 / 5) * (7 - 2 * u),
                    b * (2 * alpha ** 2 + (1 / 5) * (1 + 4 * u)),
                    a * (-2 * beta ** 2 - (1 / 5) * (1 + 4 * u)),
                ],
                [
                    b * (2 * alpha ** 2 + (1 / 5) * (1 + 4 * u)),
                    b ** 2 * ((4 / 3) * alpha ** 2 + (4 / 15) * (1 - u)),
                    -(u * a * b),
                ],
                [
                    a * (-2 * beta ** 2 - (1 / 5) * (1 + 4 * u)),
                    -(u * a * b),
                    a ** 2 * ((4 / 3) * beta ** 2 + (4 / 15) * (1 - u)),
                ],
            ]
        )

        k12 = np.array(
            [
                [
                    -(2 * (2 * beta ** 2 - alpha ** 2) + (2 / 5) * (7 - 2 * u)),
                    b * (alpha ** 2 - (1 / 5) * (1 + 4 * u)),
                    -(a * (2 * beta ** 2 + (1 / 5) * (1 - u))),
                ],
                [
                    b * (alpha ** 2 - (1 / 5) * (1 + 4 * u)),
                    b ** 2 * ((2 / 3) * alpha ** 2 - (4 / 15) * (1 - u)),
                    0,
                ],
                [
                    a * (2 * beta ** 2 + (1 / 5) * (1 - u)),
                    0,
                    a ** 2 * ((2 / 3) * beta ** 2 - (1 / 15) * (1 - u)),
                ],
            ]
        )

        k13 = np.array(
            [
                [
                    -(2 * (beta ** 2 + alpha ** 2) + (2 / 5) * (7 - 2 * u)),
                    b * (alpha ** 2 - (1 / 5) * (1 - u)),
                    a * (-(beta ** 2) + (1 / 5) * (1 - u)),
                ],
                [
                    b * (-(alpha ** 2) + (1 / 5) * (1 - u)),
                    b ** 2 * ((1 / 3) * alpha ** 2 + (1 / 15) * (1 - u)),
                    0,
                ],
                [
                    a * (beta ** 2 - (1 / 5) * (1 - u)),
                    0,
                    a ** 2 * ((1 / 3) * beta ** 2 + (1 / 15) * (1 - u)),
                ],
            ]
        )

        k14 = np.array(
            [
                [
                    2 * (beta ** 2 - 2 * alpha ** 2) - (2 / 5) * (7 - 2 * u),
                    b * (2 * alpha ** 2 + (1 / 5) * (1 - u)),
                    a * (-(beta ** 2) + (1 / 5) * (1 + 4 * u)),
                ],
                [
                    b * (-2 * (alpha ** 2) - (1 / 5) * (1 - u)),
                    b ** 2 * ((2 / 3) * alpha ** 2 - (1 / 15) * (1 - u)),
                    0,
                ],
                [
                    a * (-(beta ** 2) + (1 / 5) * (1 + 4 * u)),
                    0,
                    a ** 2 * ((2 / 3) * beta ** 2 - (4 / 15) * (1 - u)),
                ],
            ]
        )

        k22 = i3.T @ k11 @ i3
        k23 = i3.T @ k14 @ i3
        k24 = i3.T @ k23 @ i3
        k33 = i1.T @ k11 @ i1
        k34 = i1.T @ k12 @ i1
        k44 = i2.T @ k11 @ i2

        k = np.array(
            [
                [k11, k12, k13, k14],
                [k12.T, k22, k23, k24],
                [k13.T, k23.T, k33, k34],
                [k14.T, k24.T, k34.T, k44],
            ]
        )

        k0 = k[0].reshape(12, 3).transpose()
        k1 = k[1].reshape(12, 3).transpose()
        k2 = k[2].reshape(12, 3).transpose()
        k3 = k[3].reshape(12, 3).transpose()

        k = np.array([k0, k1, k2, k3])

        return coef * k.reshape(
            Element.NODE_COUNT * Node.DOF_COUNT, Element.NODE_COUNT * Node.DOF_COUNT
        )

    @staticmethod
    def get_local_nodal_force_matrix() -> np.ndarray:
        """
        Calculates the local nodal forces.

        Returns
        -------
        ndarray
            Local nodal forces.

        """
        a = Element.width
        b = Element.height
        coef = Element.pressure * a * b / 3
        matrix = np.array([3, b, -a, 3, b, a, 3, -b, -a, 3, -b, -a])
        matrix *= np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0])
        return coef * matrix
