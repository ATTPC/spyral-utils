from scipy.constants import physical_constants, speed_of_light

AMU_2_MEV: float = physical_constants['atomic mass constant energy equivalent in MeV'][0] #CODATA 2018, convert u to MeV/c^2

ELECTRON_MASS_U: float = physical_constants['electron mass in u'][0] #CODATA 2018, evaluated by scipy

MEV_2_JOULE: float = physical_constants['electron volt-joule relationship'][0] * 1.0e6 # J/ev * ev/MeV = J/MeV

MEV_2_KG: float = physical_constants['electron volt-kilogram relationship'][0] * 1.0e6 # kg/ev * ev/MeV = kg/MeV (per c^2)

ROOM_TEMPERATURE: float = 293.0 #Kelvin

GAS_CONSTANT: float = physical_constants['molar gas constant'][0] * 0.0075 * ((100.0) ** 3.0)  # m^3 Pa / K mol -> m^3 Torr / K mol -> cm^3 Torr / K mol

QBRHO_2_P: float = 1.0e-9 * 10.0 * 100.0 * speed_of_light #T * m -> MeV/c^2

C = speed_of_light #m/s