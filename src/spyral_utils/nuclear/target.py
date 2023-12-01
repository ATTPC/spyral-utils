"""Module containing AT-TPC representation of target materials and their associated energy loss calculations.

Classes should never be directly instantiated, rather use the load_target function to do the work for you.

Classes
-------
TargetData
    Raw target dataclass, should never be instantiated directly by user
GasTarget
    AT-TPC representation of a gas target
SolidTarget
    AT-TPC representation of a gas target

Functions
---------
load_target_data(target_path: Path, nuclear_map: NuclearDataMap) -> TargetData | None
    Load raw target data from JSON. Should never be used directly.
save_target_data(target_path: Path, target_data: TargetData)
    Save raw target data to JSON. Should never be used directly.
load_target(target_path: Path, nuclear_map: NuclearDataMap) -> GasTarget | SolidTarget | None
    Load a target from JSON. This is what should be used to load a target.
save_target(target_path: Path, target: GasTarget | SolidTarget)
    Save a targe to JSON. This is what should be used to save a target.
"""

from .nuclear_map import NuclearDataMap, NucleusData
from ..constants import AMU_2_MEV, GAS_CONSTANT, ROOM_TEMPERATURE

import pycatima as catima
from dataclasses import dataclass, field
from pathlib import Path
from json import load, dumps
import numpy as np


@dataclass
class TargetData:
    """Raw target dataclass

    Attributes
    ----------
    compound: list[tuple[int, int, int]]
        list of Z, A, S for each element in the compound
    pressure: float | None
        optional pressure of the gas in Torr
    thickness: float | None
        optional thickness of the solid in ug/cm^2

    Methods
    -------
    density() -> float
        get the density of the gas (return 0 if solid as this should not be used)
    """

    compound: list[tuple[int, int, int]] = field(default_factory=list)  # (Z, A, S)
    pressure: float | None = None  # torr
    thickness: float | None = None  # ug/cm^2

    def density(self) -> float:
        """Get the gas density in g/cm^3

        Returns
        -------
        float
            density of the gas in g/cm^3 (0 if the target is solid)
        """
        if self.pressure is None:
            return 0.0
        else:
            molar_mass: float = 0.0
            for z, a, s in self.compound:
                molar_mass += a * s
            return molar_mass * self.pressure / (GAS_CONSTANT * ROOM_TEMPERATURE)


def load_target_data(
    target_path: Path, nuclear_map: NuclearDataMap
) -> TargetData | None:
    """Load the raw target data from a JSON file

    Parameters
    ----------
    target_path: Path
        Path to JSON file containing target data
    nuclear_map: NuclearDataMap
        Mass data; unused

    Returns
    -------
    TargetData | None
        If the data loaded successfully, returns a TargetData. Otherwise returns None.
    """
    with open(target_path, "r") as target_file:
        json_data = load(target_file)
        if (
            "compound" not in json_data
            or "pressure(Torr)" not in json_data
            or "thickness(ug/cm^2)" not in json_data
        ):
            return None
        else:
            return TargetData(
                json_data["compound"],
                json_data["pressure(Torr)"],
                json_data["thickness(ug/cm^2)"],
            )


def save_target_data(target_path: Path, data: TargetData):
    """Write raw target data to JSON file

    Parameters
    ----------
    target_path: Path
        Path to JSON file to write target data
    data: TargetData
        data to be written
    """
    with open(target_path, "w") as target_file:
        json_str = dumps(
            data,
            default=lambda data: {
                "compound": data.compound,
                "pressure(Torr)": data.pressure,
                "thickness(ug/cm^2)": data.thickness,
            },
        )
        target_file.write(json_str)


class GasTarget:
    """An AT-TPC gas target

    Gas target for which energy loss can be calculated using pycatima. Can perform several types of
    energy loss calculations (straggling, dEdx, energy lost, etc.)

    Attributes
    ----------
    data: TargetData
        The raw target data from a JSON file
    ugly_string: str
        A string representation without rich formatting
    pretty_string: str
        A string representation with rich formatting
    material: catima.Material
        The catima representation of the target
    density: float
        The target density in g/cm^3

    Methods
    -------
    get_dedx(projectile_data: NucleusData, projectile_energy: float) -> float
        get the stopping power (dEdx) for a projectile in this target
    get_angular_straggling(projectile_data: NucleusData, projectile_energy: float) -> float:
        get the angular straggling for a projectile in this target
    get_energy_loss(projectile_data: NucleusData, projectile_energy: float, distances: ndarray) -> ndarray:
        get the energy loss values for a projectile travelling distances through the target
    """

    def __init__(self, target_data: TargetData, nuclear_data: NuclearDataMap):
        self.data = target_data

        self.pretty_string: str = "(Gas)" + "".join(
            [
                f"{nuclear_data.get_data(z, a).pretty_iso_symbol}<sub>{s}</sub>"
                for (z, a, s) in self.data.compound
            ]
        )
        self.ugly_string: str = "(Gas)" + "".join(
            [
                f"{nuclear_data.get_data(z, a).isotopic_symbol}{s}"
                for (z, a, s) in self.data.compound
            ]
        )

        # Construct the target material
        self.material = catima.Material()
        for (
            z,
            a,
            s,
        ) in self.data.compound:
            self.material.add_element(
                nuclear_data.get_data(z, a).atomic_mass, z, float(s)
            )
        self.density: float = self.data.density()
        self.material.density(self.density)

    def __str__(self) -> str:
        return self.pretty_string

    def get_dedx(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        """Calculate the stopping power of the target for a projectile

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV

        Returns
        -------
        float
            dEdx in MeV/g/cm^2
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z)
        projectile.T(projectile_energy / mass_u)
        return catima.dedx(projectile, self.material)

    def get_angular_straggling(
        self, projectile_data: NucleusData, projectile_energy: float
    ) -> float:
        """Calculate the angular straggling for a projectile

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV

        Returns
        -------
        float
            angular straggling in radians
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(
            mass_u, projectile_data.Z, T=projectile_energy / mass_u
        )
        return catima.calculate(projectile, self.material).get_dict()["sigma_a"]

    def get_energy_loss(
        self,
        projectile_data: NucleusData,
        projectile_energy: float,
        distances: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate the energy loss of a projectile traveling over a set of distances

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV
        distances: ndarray
            a set of distances in meters over which to calculate the energy loss

        Returns
        -------
        ndarray
            set of energy losses
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(
            mass_u, projectile_data.Z, T=projectile_energy / mass_u
        )
        eloss = np.zeros(len(distances))
        for idx, distance in enumerate(distances):
            self.material.thickness_cm(distance * 100.0)
            projectile.T(projectile_energy / mass_u)
            eloss[idx] = catima.calculate(projectile, self.material).get_dict()["Eloss"]
        return eloss


class SolidTarget:
    """An AT-TPC gas target

    Gas target for which energy loss can be calculated using pycatima. Can perform several types of
    energy loss calculations (straggling, dEdx, energy lost, etc.)

    Attributes
    ----------
    data: TargetData
        The raw target data from a JSON file
    ugly_string: str
        A string representation without rich formatting
    pretty_string: str
        A string representation with rich formatting
    material: catima.Material
        The catima representation of the target

    Methods
    -------
    get_dedx(projectile_data: NucleusData, projectile_energy: float) -> float
        get the stopping power (dEdx) for a projectile in this target
    get_angular_straggling(projectile_data: NucleusData, projectile_energy: float) -> float:
        get the angular straggling for a projectile in this target
    get_energy_loss(projectile_data: NucleusData, projectile_energy: float, distances: ndarray) -> ndarray:
        get the energy loss values for a projectile travelling distances through the target
    """

    UG2G: float = 1.0e-6  # convert ug to g

    def __init__(self, target_data: TargetData, nuclear_data: NuclearDataMap):
        self.data = target_data
        self.pretty_string: str = "(Solid)" + "".join(
            [
                f"{nuclear_data.get_data(z, a).pretty_iso_symbol}<sub>{s}</sub>"
                for (z, a, s) in self.data.compound
            ]
        )
        self.ugly_string: str = "(Solid)" + "".join(
            [
                f"{nuclear_data.get_data(z, a).isotopic_symbol}{s}"
                for (z, a, s) in self.data.compound
            ]
        )

        self.material = catima.Material()
        for (
            z,
            a,
            s,
        ) in self.data.compound:
            self.material.add_element(
                nuclear_data.get_data(z, a).atomic_mass, z, float(s)
            )
        self.material.thickness(
            target_data.thickness * self.UG2G
        )  # Convert ug/cm^2 to g/cm^2

    def get_dedx(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        """Calculate the stopping power of the target for a projectile

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV

        Returns
        -------
        float
            dEdx in MeV/g/cm^2
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z)
        projectile.T(projectile_energy / mass_u)
        return catima.dedx(projectile, self.material)

    def get_angular_straggling(
        self, projectile_data: NucleusData, projectile_energy: float
    ) -> float:
        """Calculate the angular straggling for a projectile

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV

        Returns
        -------
        float
            angular straggling in radians
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(
            mass_u, projectile_data.Z, T=projectile_energy / mass_u
        )
        return catima.calculate(projectile, self.material).get_dict()["sigma_a"]

    def get_energy_loss(
        self,
        projectile_data: NucleusData,
        projectile_energy: float,
        incident_angles: np.ndarray,
    ) -> np.ndarray:
        """Calculate the energy loss of a projectile traveling through the solid target for a given set of incident angles

        Assumes travelling through the entire target at an incident angle.

        Parameters
        ----------
        projectile_data: NucleusData
            the projectile type
        projectile_energy: float
            the projectile kinetic energy in MeV
        incident_angles: ndarray
            a set of incident angles, describing the angle between the particle trajectory and the normal of the target surface

        Returns
        -------
        ndarray
            set of energy losses
        """
        mass_u = projectile_data.mass / AMU_2_MEV  # convert to u
        projectile = catima.Projectile(
            mass_u, projectile_data.Z, T=projectile_energy / mass_u
        )
        eloss = np.zeros(len(incident_angles))
        nominal_thickness = self.material.thickness()
        for idx, angle in enumerate(incident_angles):
            self.material.thickness(nominal_thickness / abs(np.cos(angle)))
            projectile.T(projectile_energy / mass_u)
            eloss[idx] = catima.calculate(projectile, self.material).get_dict()["Eloss"]
        self.material.thickness(nominal_thickness)
        return eloss


def load_target(
    target_path: Path, nuclear_map: NuclearDataMap
) -> GasTarget | SolidTarget | None:
    """Load a target from a JSON file

    Read the JSON data, and construct the appropriate target type.

    Parameters
    ----------
    target_path: Path
        Path to JSON data
    nuclear_map: NuclearDataMap
        Nucleus mass data

    Returns
    -------
    GasTarget | SolidTarget | None
        Return a GasTarget or SolidTarget where appropriate. Return None on failure.
    """
    data = load_target_data(target_path, nuclear_map)
    if data is None:
        return None
    elif data.pressure is None:
        return SolidTarget(data, nuclear_map)
    else:
        return GasTarget(data, nuclear_map)


def save_target(target_path: Path, target: GasTarget | SolidTarget):
    """Write a target to a JSON file

    Create the JSON data, and write to disk.

    Parameters
    ----------
    target_path: Path
        Path to JSON data file
    target: GasTarget | SolidTarget
        Target to be written
    """
    save_target_data(target_path, target.data)
