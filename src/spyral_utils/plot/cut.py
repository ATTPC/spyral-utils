"""Module conatining methods for creating, saving, and using graphical Cuts on data

Classes
-------
CutHandler
    Handler to recieve vertices from a matplotlib selector (i.e. PolygonSelector).
Cut2D
    Implementation of 2D cuts as used in many types of graphical analyses

Functions
---------
write_cut_json(cut: Cut2D, filepath: Path) -> bool
    Write the JSON representation of a Cut2D to a file
load_cut_json(filepath: Path) -> Cut2D | None
    Deserialize the JSON representation of a Cut2D
"""
from polars import Series
from shapely import Polygon, Point, contains_xy
import numpy as np
import json
from pathlib import Path
from typing import Any


class CutHandler:
    """Handler to recieve vertices from a matplotlib selector (i.e. PolygonSelector).

    Typically will be used interactively. The onselect method should be passed to the selector object at construction.
    CutHandler can also be used in analysis applications to store cuts.

    An example script:

    ```python
    from spyral_utils.plot import CutHandler, Cut2D, write_cut_json
    from matplotlib.widgets import PolygonSelector
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1,1)
    handler = CutHandler()
    selector = PolygonSelector(ax, handler.onselect)

    #plot some data here...

    plt.show()

    #wait for user to draw a cut and close the window

    mycut = handler.cuts['cut_0']
    mycut.name = 'mycut'
    write_cut_json(mycut, 'mycut.json')
    ```

    Attributes
    ----------
    cuts: dict[str, Cut2D]
        mapping of cut name to Cut2D

    Methods
    -------
    mpl_on_select(verticies: list[tuple[float, float]])
        recieve a matplotlib polygon and create a Cut2D from it
    plotly_on_select(trace: Any, points: Any, selector: Any)
        recieve a plotly selection event and create a Cut2D from it
    """

    def __init__(self):
        self.cuts: dict[str, Cut2D] = {}

    def mpl_on_select(self, vertices: list[tuple[float, float]]):
        """Callback for use with matplotlib

        Parameters
        ----------
        vertices: list[tuple[float, float]]
            polygon vertices
        """
        cut_default_name = f"cut_{len(self.cuts)}"
        self.cuts[cut_default_name] = Cut2D(cut_default_name, vertices)

    def plotly_on_select(self, trace: Any, points: Any, selector: Any):
        """Callback for use with plotly

        Parameters
        ----------
        trace: Any
            The plotly trace from which the event originated (not relevant)
        points:
            A plotly Points object containing the data indicies within the selection (not relevant)
        selector:
            The selector object (either BoxSelector or LassoSelector)
        """
        if len(selector.xs) < 2:
            return

        cut_default_name = f"cut_{len(self.cuts)}"
        self.cuts[cut_default_name] = Cut2D(
            cut_default_name, list(zip(selector.xs, selector.ys))
        )


class Cut2D:
    """Implementation of 2D cuts as used in many types of graphical analyses

    Uses matplotlib Path objects. Takes in a name (to identify the cut) and a list of points. The Path
    takes the verticies, and can then be used to check if a point(s) is inside of the polygon using the
    is_*_inside functions. Can be serialized to json format. Can also retreive Nx2 ndarray of vertices
    for plotting after the fact.

    Attributes
    ----------
    path: matplotlib.path.Path
        A matplotlib path (polygon) that is the actual cut shape
    name: str
        A name for the cut

    Methods
    -------
    is_point_inside(x: float, y: float) -> bool
        Check if a single point (x,y) is inside the cut
    is_arr_inside(points: list[tuple[float, float]]) -> list[bool]
        Check if a list of points (x,y) are inside the cut
    is_cols_inside(columns: Series) -> Series
        Check if a set of polars Columns are inside the cut
    get_vertices() -> ndarray
        Get the cut vertices
    to_json_str() -> str
        Get the JSON representation of the cut
    """

    def __init__(self, name: str, vertices: list[tuple[float, float]]):
        self.polygon: Polygon = Polygon(vertices)
        self.name = name

    def is_point_inside(self, x: float, y: float) -> bool:
        """Is a point in the cut

        Parameters
        ----------
        x: float
            point x-coordinate
        y: float
            point y-coordinate

        Returns
        -------
        bool
            true if inside, false if outside
        """
        return self.polygon.contains(Point(x, y))

    def is_arr_inside(self, points: list[tuple[float, float]]) -> list[bool]:
        """Which of the points in this list are in the cut

        Parameters
        ----------
        points: list[tuple[float, float]]
            List of points (x,y)

        Returns
        -------
        list[bool]
            List of results of checking each point
        """
        return [contains_xy(self.polygon, point) for point in points]

    def is_cols_inside(self, columns: Series) -> Series:
        """Which of the points in this Series are in the cut

        Parameters
        ----------
        columns: Series
            Polars dataframe series to check

        Returns
        -------
        Series
            Series of True or False for each point
        """
        data = np.transpose(
            [columns.struct.field(name).to_list() for name in columns.struct.fields]
        )
        return Series(values=[contains_xy(point) for point in data])

    def get_vertices(self) -> np.ndarray:
        """Get the cut vertices

        Returns
        -------
        list[tuple]
            the vertices

        """
        return tuple(self.polygon.exterior.coords)

    def to_json_str(self) -> str:
        """Get the cut JSON representation

        Returns
        -------
        str
            JSON representation
        """
        return json.dumps(
            self,
            default=lambda obj: {
                "name": obj.name,
                "vertices": tuple(obj.polygon.exterior.coords),
            },
            indent=4,
        )


def write_cut_json(cut: Cut2D, filepath: Path) -> bool:
    """Write the JSON representation of a Cut2D to a file

    Parameters
    ----------
    cut: Cut2D
        Cut to serialize
    filepath: Path
        Path at which cut should be written

    Returns
    -------
    bool
        True on success, False on failure
    """
    json_str = cut.to_json_str()
    try:
        with open(filepath, "w") as output:
            output.write(json_str)
            return True
    except OSError as error:
        print(f"An error occurred writing cut {cut.name} to file {filepath}: {error}")
        return False


def load_cut_json(filepath: Path) -> Cut2D | None:
    """Deserialize the JSON representation of a Cut2D

    Parameters
    ----------
    filepath: Path
        Path at which cut should be read from

    Returns
    -------
    Cut2D | None
        Returns a Cut2D on success, None on failure
    """
    try:
        with open(filepath, "r") as input:
            buffer = input.read()
            cut_dict = json.loads(buffer)
            if "name" not in cut_dict or "vertices" not in cut_dict:
                print(
                    f"Data in file {filepath} is not the right format for Cut2D, could not load"
                )
                return None
            return Cut2D(cut_dict["name"], cut_dict["vertices"])
    except OSError as error:
        print(
            f"An error occurred reading trying to read a cut from file {filepath}: {error}"
        )
        return None
