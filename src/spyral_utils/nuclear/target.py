from .nuclear_map import NuclearDataMap, NucleusData
from ..constants import AMU_2_MEV, GAS_CONSTANT, ROOM_TEMPERATURE

import pycatima as catima
from dataclasses import dataclass, field
from pathlib import Path
from json import load, dumps
import numpy as np

@dataclass
class TargetData:
    compound: list[tuple[int, int, int]] = field(default_factory=list) #(Z, A, S)
    pressure: float | None = None #torr
    thickness: float | None = None #ug/cm^2

    def density(self) -> float:
        if self.pressure is None:
            return 0.0
        else:
            molar_mass: float = 0.0 
            for (z, a, s) in self.compound:
                molar_mass += a*s
            return molar_mass * self.pressure / (GAS_CONSTANT * ROOM_TEMPERATURE)
        
def load_target_data(target_path: Path, nuclear_map: NuclearDataMap) -> TargetData | None:
    with open(target_path, 'r') as target_file:
        json_data = load(target_file)
        if 'compound' not in json_data or 'pressure(Torr)' not in json_data or 'thickness(ug/cm^2)' not in json_data:
            return None
        else:
            return TargetData(json_data['compound'], json_data['pressure(Torr)'], json_data['thickness(ug/cm^2)'])

def save_target_data(target_path: Path, data: TargetData):
    with open(target_path, 'w') as target_file:
        json_str = dumps(data, default=lambda data: {'compound': data.compound, 'pressure(Torr)': data.pressure, 'thickness(ug/cm^2)': data.thickness})
        target_file.write(json_str)

class GasTarget:

    def __init__(self, target_data: TargetData, nuclear_data: NuclearDataMap):
        self.data = target_data

        self.pretty_string: str = '(Gas)' + ''.join([f'{nuclear_data.get_data(z, a).pretty_iso_symbol}<sub>{s}</sub>' for (z, a, s) in self.data.compound])
        self.ugly_string: str = '(Gas)' + ''.join([f'{nuclear_data.get_data(z, a).isotopic_symbol}{s}' for (z, a, s) in self.data.compound])
        
        #Construct the target material
        self.material = catima.Material()
        for z, a, s, in self.data.compound:
            self.material.add_element(nuclear_data.get_data(z, a).atomic_mass, z, float(s))
        self.density: float = self.data.density()
        self.material.density(self.density)

    def __str__(self) -> str:
        return self.pretty_string
    
    def get_dedx(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        '''
        Calculate the stopping power of the target for a projectile

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV

        ## Returns
        float: dEdx in MeV/g/cm^2
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z)
        projectile.T(projectile_energy/mass_u)
        return catima.dedx(projectile, self.material)
    
    def get_angular_straggling(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        '''
        Calculate the angular straggling for a projectile

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV

        ## Returns
        float: angular straggling in radians
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z,T=projectile_energy/mass_u)
        return catima.calculate(projectile, self.material).get_dict()['sigma_a']
    
    def get_energy_loss(self, projectile_data: NucleusData, projectile_energy: float, distances: np.ndarray) -> np.ndarray:
        '''
        Calculate the energy loss of a projectile traveling over a set of distances

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV
        distances: np.ndarray, a set of distances in meters over which to calculate the energy loss

        ## Returns
        np.ndarray: set of energy losses
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z, T=projectile_energy/mass_u)
        eloss = np.zeros(len(distances))
        for idx, distance in enumerate(distances):
            self.material.thickness_cm(distance * 100.0)
            projectile.T(projectile_energy/mass_u)
            eloss[idx] = catima.calculate(projectile, self.material).get_dict()['Eloss']
        return eloss
    
class SolidTarget:
    UG2G: float = 1.0e-6 #convert ug to g
    def __init__(self, target_data: TargetData, nuclear_data: NuclearDataMap):
        self.data = target_data
        self.pretty_string: str = '(Solid)' + ''.join([f'{nuclear_data.get_data(z, a).pretty_iso_symbol}<sub>{s}</sub>' for (z, a, s) in self.data.compound])
        self.ugly_string: str = '(Solid)' + ''.join([f'{nuclear_data.get_data(z, a).isotopic_symbol}{s}' for (z, a, s) in self.data.compound])

        self.material = catima.Material()
        for z, a, s, in self.data.compound:
            self.material.add_element(nuclear_data.get_data(z, a).atomic_mass, z, float(s))
        self.material.thickness(target_data.thickness * self.UG2G) #Convert ug/cm^2 to g/cm^2

    def get_dedx(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        '''
        Calculate the stopping power of the target for a projectile

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV

        ## Returns
        float: dEdx in MeV/g/cm^2
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z)
        projectile.T(projectile_energy/mass_u)
        return catima.dedx(projectile, self.material)
    
    def get_angular_straggling(self, projectile_data: NucleusData, projectile_energy: float) -> float:
        '''
        Calculate the angular straggling for a projectile

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV

        ## Returns
        float: angular straggling in radians
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z,T=projectile_energy/mass_u)
        return catima.calculate(projectile, self.material).get_dict()['sigma_a']
    
    def get_energy_loss(self, projectile_data: NucleusData, projectile_energy: float, incident_angles: np.ndarray) -> np.ndarray:
        '''
        Calculate the energy loss of a projectile traveling through the solid target for a given set of incident angles

        ## Parameters
        projectile_data: NucleusData, the projectile type
        projectile_energy: float, the projectile kinetic energy in MeV
        incident_angles: np.ndarray, a set of incident angles, describing the angle between the particle trajectory and the normal of the target surface

        ## Returns
        np.ndarray: set of energy losses
        '''
        mass_u = projectile_data.mass / AMU_2_MEV # convert to u
        projectile = catima.Projectile(mass_u, projectile_data.Z, T=projectile_energy/mass_u)
        eloss = np.zeros(len(incident_angles))
        nominal_thickness = self.material.thickness()
        for idx, angle in enumerate(incident_angles):
            self.material.thickness(nominal_thickness / abs(np.cos(angle)))
            projectile.T(projectile_energy/mass_u)
            eloss[idx] = catima.calculate(projectile, self.material).get_dict()['Eloss']
        self.material.thickness(nominal_thickness)
        return eloss
    
def load_target(target_path: Path, nuclear_map: NuclearDataMap) -> GasTarget | SolidTarget | None:
    data = load_target_data(target_path, nuclear_map)
    if data is None:
        return None
    elif data.pressure is None:
        return SolidTarget(data, nuclear_map) 
    else:
        return GasTarget(data, nuclear_map)
    
def save_target(target_path: Path, target: GasTarget | SolidTarget):
    save_target_data(target_path, target.data)
