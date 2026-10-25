"""Unidades explícitas; el peso interno es fuerza, nunca masa."""
import math

KT_TO_FPS = 1852 / 0.3048 / 3600
RHO0 = 0.002376892406675  # slug/ft³, atmósfera estándar al nivel del mar

UNITS = {
    'weight': {'lbf': 1.0, 'N': 1/4.4482216152605},
    'area': {'ft²': 1.0, 'm²': 1/0.3048**2},
    'length': {'ft': 1.0, 'm': 1/0.3048},
    'density': {'slug/ft³': 1.0, 'kg/m³': 1/515.3788183931961, 'lbm/ft³': 1/32.17404855643044},
    'slope': {'1/rad': 1.0, '1/deg': 180/math.pi},
    'speed': {'kt EAS': 1.0, 'ft/s EAS': 1/KT_TO_FPS, 'm/s EAS': 3600/1852},
    'gust': {'ft/s': 1.0, 'm/s': 1/0.3048},
    'accel': {'ft/s²': 1.0, 'm/s²': 1/0.3048},
    'ratio': {'1': 1.0},
    'loading': {'lbf/ft²': 1.0, 'Pa': 1/47.88025898033584},
}

def convert(value, unit, dimension):
    if value is None:
        raise ValueError('Dato pendiente')
    if isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError('El valor debe ser numérico y finito')
    if dimension not in UNITS or unit not in UNITS[dimension]:
        raise ValueError(f'Unidad {unit!r} no válida para {dimension}')
    return float(value) * UNITS[dimension][unit]

def eas_to_tas(eas, rho, rho0=RHO0):
    if rho <= 0 or rho0 <= 0:
        raise ValueError('Densidad no positiva')
    return eas*math.sqrt(rho0/rho)
