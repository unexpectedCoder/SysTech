from typing import Callable
import matplotlib.pyplot as plt
import numpy as np


def show_laplace(calc_laplace: Callable, data: dict, dist_min: float = 200.):
    x = np.linspace(dist_min, data['x0'], 100)
    phi_t = np.array([calc_laplace(dist, 1 / data['Ex100t'], data['a'], data['b']) for dist in x]) / data['omega100t']
    phi_100 = np.array([calc_laplace(dist, 1 / data['Ex100'], data['at'], data['bt']) for dist in x]) / data['omega100']
    phi_152 = np.array([calc_laplace(dist, 1 / data['Ex152'], data['at'], data['bt']) for dist in x]) / data['omega152']
    phi_ptur = np.array([calc_laplace(dist, 1 / data['Exptur'], data['at'], data['bt']) for dist in x]) / data['omegaptur']

    fig, ax = plt.subplots(1, 1)
    ax.plot(x, phi_t, lw=2, label='100Т')
    ax.plot(x, phi_100, lw=2, label='100')
    ax.plot(x, phi_152, lw=2, label='152')
    ax.plot(x, phi_ptur, lw=2, label='ПТУР')

    ax.set_xlabel('$x$, м')
    ax.set_ylabel(r'$W = P / \omega$')
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid()
    plt.show()
