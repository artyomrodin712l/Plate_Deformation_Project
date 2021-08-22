"""
The class contains the index, coordinates and fixity of the node.

"""

from typing import Final


class Node:
    """
    The class contains the index, coordinates and fixity of the node.
    The node contains three degrees of freedom.

    Parameters
    ----------
    index : non-negative int
        Node index in the global node list.
    x : float
        Node's x-axis coordinate.
    y : float
        Node's y-axis coordinate.
    fixed : bool
        Determines whether the node is fixed.

    Attributes
    ----------
    index : non-negative int
        Node index in the global node list.
    x : float
        Node's x-axis coordinate.
    y : float
        Node's y-axis coordinate.
    fixed : bool
        Determines whether the node is fixed.

    Class Attributes
    ----------------
    DOF_COUNT : non-negative int
        Number of degrees of freedom (DOF).

    """

    DOF_COUNT: Final = 3

    def __init__(self, index: int, x: float, y: float, fixed: bool = False) -> None:
        self.index: Final = index
        self.x: Final = x
        self.y: Final = y
        self.fixed: Final = fixed
