"""Modules for creating and plotting histograms in matplotlib

The default matplotlib histogramming tools can be hard to use for large datasets
as they require a lot of rebinning or all of the data to be loaded. Here we give some of our own
which allow for incremental filling of histograms

Classes
-------
Hist1D
    A 1-D histogram dataclass. Should not be instantiated directly
Hist2D
    A 2-D histogram dataclass. Should not be instantiated directly
Histogrammer
    A parent object used to create, manage, draw histograms
"""

import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from matplotlib.axes import Axes
from matplotlib.text import Text
from matplotlib.colors import LogNorm
from matplotlib.backend_bases import LocationEvent
from matplotlib.collections import QuadMesh
import matplotlib.pyplot as plt
from matplotlib import colormaps
from math import floor

CMAP = colormaps.get_cmap("viridis").with_extremes(under="white")


# Utility functions
def clamp_low(x: float, edge: float) -> float:
    return x if x > edge else edge


def clamp_hi(x: float, edge: float) -> float:
    return x if x < edge else edge


def clamp_range(xrange: tuple[float, float], min_max: tuple[float, float]):
    return (clamp_low(xrange[0], min_max[0]), clamp_hi(xrange[1], min_max[1]))


@dataclass
class Hist1D:
    """Dataclass wrapping a numpy array used to store histogram data and retrieve histogram statistics

    Attributes
    ----------
    name: str
        histogram name
    counts: ndarray
        array of histogram counts
    bins: ndarray
        array of histogram bin edges
    bin_width: float
        the width of histogram bins

    Methods
    -------
    get_bin(x: float) -> int | None
        get the bin number for an x-coordinate value
    stats_for_range(xrange: tuple[float, float]) -> tuple[float, float, float] | None
        get some statistics for a subrange of the histogram
    get_subrange(xrange: tuple[float, float]) -> tuple[ndarray, ndarray]
        get a histogram subrange (bin edges, counts)
    """

    name: str
    counts: NDArray[np.float64]
    bins: NDArray[np.float64]
    bin_width: float

    def get_bin(self, x: float) -> int | None:
        """Get the bin number which contains the x-coordinate

        Parameters
        ----------
        x: float
            X-coordinate for which we want to find the bin number

        Returns
        -------
        int | None
            The bin number or None if the x value does not fall within the histogram
        """
        if x < self.bins.min() or x > self.bins.max():
            return None

        return int(floor((x - self.bins[0]) / self.bin_width))

    def stats_for_range(
        self, xrange: tuple[float, float]
    ) -> tuple[float, float, float] | None:
        """Get some statistics for a histogram subrange

        Calculates the mean, integral, and standard deviation of the sub-range

        Parameters
        ----------
        xrange: tuple[float, float]
            the subrange of the histogram (min, max) in x-coordinates

        Returns
        -------
        tuple[float, float, float] | None
            Returns a tuple of (integral, mean, std. dev.) for the subrange, or None if the subrange is not within the histogram bounds

        """
        clamped_range = clamp_range(xrange, (self.bins.min(), self.bins.max()))
        bin_min = self.get_bin(clamped_range[0])
        bin_max = self.get_bin(clamped_range[1])
        if bin_min is None or bin_max is None:
            return None
        integral = np.sum(self.counts[bin_min:bin_max])
        mean = np.average(
            self.bins[bin_min:bin_max], weights=self.counts[bin_min:bin_max]
        )
        variance = np.average(
            (self.bins[bin_min:bin_max] - mean) ** 2.0,
            weights=self.counts[bin_min:bin_max],
        )
        return (integral, mean, np.sqrt(variance))

    def get_subrange(
        self, xrange: tuple[float, float]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get a subrange of the histogram

        Parameters
        ----------
        xrange: tuple[float, float]
            the subrange of the histogram (min, max) in x-coordinates

        Returns
        -------
        tuple[ndarray, ndarray]
            the subrange (bin edges, counts)
        """
        mask = np.logical_and(self.bins > xrange[0], self.bins < xrange[1])
        return (self.bins[mask], self.counts[mask[:-1]])


@dataclass
class Hist2D:
    """Dataclass wrapping a numpy array used to store two-dimensional histogram data and retrieve histogram statistics

    Attributes
    ----------
    name: str
        histogram name
    counts: ndarray
        array of histogram counts
    x_bins: ndarray
        array of histogram x bin edges
    y_bins: ndarray
        array of histogram y bin edges
    x_bin_width: float
        the width of histogram x bins
    y_bin_width: float
        the width of histogram y bins

    Methods
    -------
    get_bin(coords: tuple[float, float]) -> tuple[int, int] | None
        get the x and y bin numbers for an (x,y)-coordinate value
    stats_for_range(xrange: tuple[float, float], yrange: tuple[float, float]) -> tuple[float, float, float, float, float] | None
        get some statistics for a subrange of the histogram
    get_subrange(xrange: tuple[float, float], xrange: tuple[float, float]) -> tuple[ndarray, ndarray, ndarray]
        get a histogram subrange (x bin edges, y bin edges, counts)
    """

    name: str
    counts: NDArray[np.float64]
    x_bins: NDArray[np.float64]
    y_bins: NDArray[np.float64]
    x_bin_width: float
    y_bin_width: float

    def get_bin(self, coords: tuple[float, float]) -> tuple[int, int] | None:
        """Get the x and y bin numbers for an (x,y)-coordinate value

        Parameters
        ----------
        coords: tuple[float, float]
            The (x,y) corrdinate for which we want to find the bin numbers

        Returns
        -------
        tuple[int, int] | None
            Returns the (x bin, y bin) numbers or None if out of range
        """
        if (coords[0] < self.x_bins.min() or coords[0] > self.x_bins.max()) or (
            coords[1] < self.y_bins.min() or coords[1] > self.y_bins.max()
        ):
            return None

        y_bin = int(floor((coords[1] - self.y_bins[0]) / self.y_bin_width))
        x_bin = int(floor((coords[0] - self.x_bins[0]) / self.x_bin_width))
        return (x_bin, y_bin)

    # returns (integral, mean x, std_dev x, mean y, std_dev y)
    def stats_for_range(
        self, xrange: tuple[float, float], yrange: tuple[float, float]
    ) -> tuple[float, float, float, float, float] | None:
        """Get some statistics for a histogram subrange

        Calculates the mean in x and y, integral, and standard deviation in x and y of the sub-range

        Parameters
        ----------
        xrange: tuple[float, float]
            the subrange of the histogram (min, max) in x-coordinates
        yrange: tuple[float, float]
            the subrange of the histogram (min, max) in y-coordinates

        Returns
        -------
        tuple[float, float, float, float, float] | None
            Returns a tuple of (integral, x mean, y mean, x std. dev., y std. dev.) for the subrange, or None if the subrange is not within the histogram bounds

        """
        clamped_x_range = clamp_range(xrange, (self.x_bins.min(), self.x_bins.max()))
        clamped_y_range = clamp_range(yrange, (self.y_bins.min(), self.y_bins.max()))
        bin_min = self.get_bin((clamped_x_range[0], clamped_y_range[0]))
        bin_max = self.get_bin((clamped_x_range[1], clamped_y_range[1]))

        x_bin_range = np.arange(start=bin_min[0], stop=bin_max[0], step=1)
        y_bin_range = np.arange(start=bin_min[1], stop=bin_max[1], step=1)
        bin_mesh = np.ix_(y_bin_range, x_bin_range)

        integral = np.sum(self.counts[bin_mesh])
        mean_x = np.average(
            self.x_bins[bin_min[0] : bin_max[0]],
            weights=np.sum(self.counts.T[bin_min[0] : bin_max[0]], 1),
        )
        mean_y = np.average(
            self.y_bins[bin_min[1] : bin_max[1]],
            weights=np.sum(self.counts[bin_min[1] : bin_max[1]], 1),
        )
        var_x = np.average(
            (self.x_bins[bin_min[0] : bin_max[0]] - mean_x) ** 2.0,
            weights=np.sum(self.counts.T[bin_min[0] : bin_max[0]], 1),
        )
        var_y = np.average(
            (self.y_bins[bin_min[1] : bin_max[1]] - mean_y) ** 2.0,
            weights=np.sum(self.counts[bin_min[1] : bin_max[1]], 1),
        )
        return (integral, mean_x, mean_y, np.sqrt(var_x), np.sqrt(var_y))

    def get_subrange(
        self, xrange: tuple[float, float], yrange: tuple[float, float]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get a subrange of the histogram

        Parameters
        ----------
        xrange: tuple[float, float]
            the subrange of the histogram (min, max) in x-coordinates
        yrange: tuple[float, float]
            the subrange of the histogram (min, max) in y-coordinates

        Returns
        -------
        tuple[ndarray, ndarray, ndarray]
            the subrange (x bin edges, y bin edges, counts)
        """
        x_mask = np.logical_and(self.x_bins > xrange[0], self.x_bins < xrange[1])
        y_mask = np.logical_and(self.y_bins > yrange[0], self.y_bins < yrange[1])
        bin_mesh = np.ix_(y_mask, x_mask)
        return (self.x_bins[x_mask], self.y_bins[y_mask], self.counts[bin_mesh])


class Histogrammer:
    """Histogrammer is a wrapper around a dictionary of str->Hist1D|Hist2D that interfaces with matplotlib

    A new histogram can be added to the dictionary using the add_hist1d/add_hist2d methods. The name passed to
    these methods is used as the key for the dictionary. To add data to the histograms use the fill_hist1d/fill_hist2d methods.
    The fill methods accept arrays of data, and this is by intent. It would not be efficient to fill the histograms point by point. Rather, prefer
    passing entire data sets (like dataframe columns). Finally, to retrieve a histogram (for plotting, etc), use the get_hist1d/get_hist2d methods.
    Prefer the getters over direct access to the underlying dictionary as the getters perfom some error checking.

    Attributes
    ----------
    histograms: dict[str, Hist1D | Hist2D]
        the histograms held by the Histogrammer, mapped by name
    axes: dict[Axes, tuple[str, Text | None]]
        mapping of mpl Axes to associated histogram names and Text for the stats
    figures: dict[str, bool]
        used to see if callbacks have been set for a given figure name

    Methods
    -------
    add_hist1d(name: str, bins: int, range: tuple[float, float])
        add a Hist1D
    add_hist2d(name: str, bins: tuple[int, int], ranges: tuple[tuple[float, float], tuple[float, float]])
        add a Hist2D
    fill_hist1d(self, name: str, data: ndarray) -> bool
        fill an existing Hist1D with some data
    fill_hist2d(self, name: str, x_data: ndarray, y_data: ndarray) -> bool
        fill an existing Hist2D with some data
    get_hist1d(name: str) -> Hist1D | None
        get a Hist1D by name
    get_hist2d(name: str) -> Hist2D | None
        get a Hist2D by name
    on_axes_enter_hist1d(event: LocationEvent)
        handler for when the user mouse enters an axis of a Hist1D
    on_axes_enter_hist2d(event: LocationEvent)
        handler for when the user mouse enters an axis of a Hist2D
    on_axes_enter(event: LocationEvent)
        matplotlib callback for when the user mouse enters an axis
    on_axes_leave(event: LocationEvent)
        matplotlib callback for when the user mouse leaves an axis
    connect_mpl_callbacks(axis: Axes)
        setup mpl callbacks for an axis
    draw_hist1d(name: str, axis: Axes)
        draw a Hist1D in a matplotlib Axes
    draw_hist2d(name: str, axis: Axes, log_z: bool = False) -> QuadMesh | None
        draw a Hist2D in a matplotlib Axes
    """

    def __init__(self):
        self.histograms: dict[str, Hist1D | Hist2D] = {}
        self.axes: dict[Axes, tuple[str, Text | None]] = {}
        self.figures: dict[
            str, bool
        ] = {}  # used to indicate if callbacks have been bound for that figure

    def add_hist1d(self, name: str, bins: int, range: tuple[float, float]):
        """Add a Hist1D to the Histogrammer

        Parameters
        ----------
        name: str
            The name of the histogram, it should be unqiue
        bins: int
            The number of bins
        range: tuple[float, float]
            The x-range of the histogram in x-axis coordinates
        """
        if name in self.histograms:
            print(f"Overwriting histogram named {name} in Histogrammer.add_histogram!")

        hist = Hist1D(
            name, np.empty(0), np.empty(0), np.abs(range[0] - range[1]) / float(bins)
        )
        hist.counts, hist.bins = np.histogram(a=[], bins=bins, range=range)
        self.histograms[name] = hist

    def add_hist2d(
        self,
        name: str,
        bins: tuple[int, int],
        ranges: tuple[tuple[float, float], tuple[float, float]],
    ):
        """Add a Hist2D to the Histogrammer

        Parameters
        ----------
        name: str
            The name of the histogram, it should be unqiue
        bins: tuple[int, int]
            The number of (x bins, y bins)
        ranges: tuple[tuple[float, float], tuple[float, float]]
            The range of the histogram ((min x, max x), (min y, max y))
        """
        if name in self.histograms:
            print(f"Overwriting histogram named {name} in Histogrammer.add_histogram!")

        hist = Hist2D(
            name,
            np.empty(0),
            np.empty(0),
            np.empty(0),
            np.abs(ranges[0][0] - ranges[0][1]) / float(bins[0]),
            np.abs(ranges[1][0] - ranges[1][1]) / float(bins[1]),
        )
        hist.counts, hist.x_bins, hist.y_bins = np.histogram2d(
            x=[], y=[], bins=bins, range=ranges
        )
        hist.counts = hist.counts.T
        self.histograms[name] = hist

    def fill_hist1d(self, name: str, data: np.ndarray) -> bool:
        """Fill a Hist1D with some data

        Parameters
        ----------
        name: str
            The name of the Hist1D
        data: ndarray
            The data to fill the histogram with. Should be a 1-D array

        Returns
        -------
        bool
            Indicates if data was successfully added to the histogram

        """
        if name not in self.histograms:
            return False

        hist = self.histograms[name]
        if type(hist) is not Hist1D:
            return False

        hist.counts = hist.counts + np.histogram(a=data, bins=hist.bins)[0]
        return True

    def fill_hist2d(self, name: str, x_data: np.ndarray, y_data: np.ndarray) -> bool:
        """Fill a Hist1D with some data

        The parameters x_data and y_data should have the same length.

        Parameters
        ----------
        name: str
            The name of the Hist1D
        x_data: ndarray
            The x coordinates of the data. Should be a 1-D array.
        y_data: ndarray
            The y coordinates of the data. Should be a 1-D array.

        Returns
        -------
        bool
            Indicates if data was successfully added to the histogram

        """
        if name not in self.histograms:
            return False

        hist = self.histograms[name]
        if type(hist) is not Hist2D:
            return False
        counts, _, _ = np.histogram2d(
            x_data.flatten(), y_data.flatten(), bins=(hist.x_bins, hist.y_bins)
        )
        hist.counts += counts.T
        return True

    def get_hist1d(self, name: str) -> Hist1D | None:
        """Retrieve a Hist1D by name

        Parameters
        ----------
        name: str
            The name of the histogram

        Returns
        -------
        Hist1D | None
            Returns Hist1D if a Hist1D exists with the given name. Otherwise returns None.

        """
        if name not in self.histograms:
            return None

        hist = self.histograms[name]
        if type(hist) is not Hist1D:
            return None
        else:
            return hist

    def get_hist2d(self, name: str) -> Hist2D | None:
        """Retrieve a Hist2D by name

        Parameters
        ----------
        name: str
            The name of the histogram

        Returns
        -------
        Hist2D | None
            Returns Hist2D if a Hist2D exists with the given name. Otherwise returns None.

        """
        if name not in self.histograms:
            return None

        hist = self.histograms[name]
        if type(hist) is not Hist2D:
            return None
        else:
            return hist

    def on_axes_enter_hist1d(self, event: LocationEvent):
        """Handler for AxesEnter events on Hist1D

        Parameters
        ----------
        event: LocationEvent
            The event which triggered the callback

        """
        data = self.axes[event.inaxes]
        xrange = event.inaxes.get_xbound()
        yrange = event.inaxes.get_ybound()
        stats = self.histograms[data[0]].stats_for_range(xrange)
        if data[1] is not None:
            data[1].remove()

        draw_x = xrange[1] - 0.25 * np.abs(xrange[0] - xrange[1])
        draw_y = yrange[1] - 0.25 * np.abs(yrange[0] - yrange[1])
        self.axes[event.inaxes] = (
            data[0],
            event.inaxes.text(
                draw_x,
                draw_y,
                f"Integral: {stats[0]}\nCentroid: {stats[1]:.3f}\nSigma: {stats[2]:.3f}",
            ),
        )
        plt.draw()

    def on_axes_enter_hist2d(self, event: LocationEvent):
        """Handler for AxesEnter events on Hist2D

        Parameters
        ----------
        event: LocationEvent
            The event which triggered the callback

        """
        data = self.axes[event.inaxes]
        xrange = event.inaxes.get_xbound()
        yrange = event.inaxes.get_ybound()
        stats = self.histograms[data[0]].stats_for_range(xrange, yrange)
        if data[1] is not None:
            data[1].remove()

        draw_x = xrange[1] - 0.25 * np.abs(xrange[0] - xrange[1])
        draw_y = yrange[1] - 0.25 * np.abs(yrange[0] - yrange[1])
        self.axes[event.inaxes] = (
            data[0],
            event.inaxes.text(
                draw_x,
                draw_y,
                f"Integral: {stats[0]}\nCentroid X: {stats[1]:.3f}\nCentroid Y: {stats[2]:.3f}\nSigma X: {stats[3]:.3f}\nSigma Y: {stats[4]:.3f}",
                color="black",
            ),
        )
        plt.draw()

    def on_axes_enter(self, event: LocationEvent):
        """Callback function for AxesEnter events from matplotlib on histograms to display stats

        Parameters
        ----------
        event: LocationEvent
            The event which triggered the callback

        """
        if event.inaxes not in self.axes:
            return

        if type(self.histograms[self.axes[event.inaxes][0]]) is Hist1D:
            self.on_axes_enter_hist1d(event)
        elif type(self.histograms[self.axes[event.inaxes][0]]) is Hist2D:
            self.on_axes_enter_hist2d(event)

    def on_axes_leave(self, event: LocationEvent):
        """Callback function for AxesLeave events from matplotlib on histograms to un-display stats

        Parameters
        ----------
        event: LocationEvent
            The event which triggered the callback

        """
        if event.inaxes not in self.axes:
            return
        data = self.axes[event.inaxes]
        if data[1] is None:
            return
        data[1].remove()
        self.axes[event.inaxes] = (data[0], None)
        plt.draw()

    def connect_mpl_callbacks(self, axis: Axes):
        """Setup callbacks for matplotlib with a given axis

        Parameters
        ----------
        axis: Axes
            The Axes to bind the callbacks to

        """
        if not hasattr(axis.figure, "_suptitle"):
            axis.figure.suptitle(f"Figure {len(self.figures)}")
        elif axis.figure._suptitle in self.figures:
            return

        self.figures[axis.figure._suptitle] = True
        axis.figure.canvas.mpl_connect("axes_enter_event", self.on_axes_enter)
        axis.figure.canvas.mpl_connect("axes_leave_event", self.on_axes_leave)

    def draw_hist1d(self, name: str, axis: Axes):
        """Draw a Hist1D on a given Axes

        Parameters
        ----------
        name: str
            The name of the histogram to draw
        axis: Axes
            The Axes into which the histogram should be drawn

        """
        if name not in self.histograms:
            return

        hist = self.histograms[name]
        if type(hist) is not Hist1D:
            return

        axis.stairs(hist.counts, hist.bins)
        self.axes[axis] = (name, None)
        self.connect_mpl_callbacks(axis)

    def draw_hist2d(
        self, name: str, axis: Axes, log_z: bool = False
    ) -> QuadMesh | None:
        """Draw a Hist2D on a given Axes

        Parameters
        ----------
        name: str
            The name of the histogram to draw
        axis: Axes
            The Axes into which the histogram should be drawn
        log_z: bool
            Whether or not to logscale the z-axis (color). Default is False.

        Returns
        -------
        QuadMesh | None
            If successfully drawn, returns a QuadMesh of the color scale used to later draw a color bar. Otherwise returns None.

        """
        if name not in self.histograms:
            return None

        hist = self.histograms[name]
        if type(hist) is not Hist2D:
            return None
        mesh = None
        if log_z:
            mesh = axis.pcolormesh(
                hist.x_bins, hist.y_bins, hist.counts, cmap=CMAP, norm=LogNorm()
            )
        else:
            mesh = axis.pcolormesh(
                hist.x_bins, hist.y_bins, hist.counts, cmap=CMAP, vmin=1.0e-6
            )
        self.axes[axis] = (name, None)
        self.connect_mpl_callbacks(axis)
        return mesh
