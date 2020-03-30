from scipy.integrate import quad
import numpy as np


def process_data(data: dict) -> dict:
    d = data.copy()
    for key in d.keys():
        if is_digit(d[key]):
            d[key] = float(d[key])
        elif d[key] == 'None':
            d[key] = None
        else:
            raise ValueError
    return d


def is_digit(s: str) -> bool:
    if s.isdigit():
        return True
    else:
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True


def get_dist(x0: float, v: float, t: float) -> float:
    return x0 + v * t


def laplace(x: float, ex_x: float, a: float, b: float) -> float:
    sigma = 1.48 * ex_x * x
    phi1 = quad(integrand, 0, 0.5 * b / sigma)[0]
    phi2 = quad(integrand, 0, 0.5 * a / sigma)[0]
    return 4 * phi1 * phi2


def integrand(x: float) -> float:
    return np.exp(-0.5 * x ** 2) / np.sqrt(2 * np.pi)
