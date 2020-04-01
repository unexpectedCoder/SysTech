from helpers import laplace


class Tank:
    def __init__(self, data: dict, variant: str):
        self.V, self.Vi = [], []
        self.var = variant
        self.v = data['vt']
        self.a, self.b = data['at'], data['bt']
        self.omega = data['omega' + variant]
        self.n = data['n' + variant]
        self.t_shot = 60 / self.n
        self.Ex = 1 / data['Ex' + variant]

    def __str__(self):
        return f"Tank (var. {self.var}):" \
               f"\n - v = {self.v} [m/s]" \
               f"\n - a x b = {self.a} x {self.b} [m]" \
               f"\n - n = {self.n} [1/min]" \
               f"\n - Ex/x = 1 / {1 / self.Ex}" \
               f"\n - omega = {self.omega}" \
               f"\n - shot time = {self.t_shot} [s]"

    def __copy__(self):
        data = {
            'vt': self.v,
            'at': self.a,
            'bt': self.b,
            'omega' + self.var: self.omega,
            'n' + self.var: self.n,
            'Ex' + self.var: 1 / self.Ex
        }
        return Tank(data, self.var)

    def starting_update(self, x: float, atarg: float, btarg: float, coeff: float):
        self.Vi.append(laplace(x, self.Ex, atarg, btarg) / self.omega)
        self.V.append(coeff * self.Vi[0])

    def update(self, x: float, atarg: float, btarg: float, coeff: float):
        self.Vi.append(laplace(x, self.Ex, atarg, btarg) / self.omega)
        self.V.append(self.V[-1] + coeff * self.Vi[-1])


class SPAM:
    def __init__(self, data: dict, variant: str):
        self.W, self.Wi = [], []
        self.var = variant
        self.v = 0
        self.a, self.b = data['a'], data['b']
        self.omega = data['omega' + variant]
        self.n = data['n' + variant]
        self.t_shot = 60 / self.n if self.n is not None else None
        self.Ex = 1 / data['Ex' + variant]
        self.cost = data['C' + variant]

    def __str__(self):
        return f"SPAM (var. {self.var}):" \
               f"\n - v = {self.v} [m/s]" \
               f"\n - a x b = {self.a} x {self.b} [m]" \
               f"\n - omega = {self.omega}" \
               f"\n - n = {self.n} [1/min]" \
               f"\n - Ex/x = 1 / {1 / self.Ex}" \
               f"\n - shot time = {self.t_shot} [s]" \
               f"\n - cost = {self.cost}"

    def __copy__(self):
        data = {
            'a': self.a,
            'b': self.b,
            'omega' + self.var: self.omega,
            'n' + self.var: self.n,
            'Ex' + self.var: 1 / self.Ex,
            'C' + self.var: self.cost
        }
        return SPAM(data, self.var)

    def set_variant(self, data: dict, variant: str):
        self.var = variant
        self.omega = data['omega' + variant]
        self.n = data['n' + variant]
        self.t_shot = 60 / self.n if self.n is not None else None
        self.Ex = 1 / data['Ex' + variant]
        self.cost = data['C' + variant]

    def starting_update(self, x: float, atarg: float, btarg: float, coeff: float):
        self.Wi.append(laplace(x, self.Ex, atarg, btarg) / self.omega)
        self.W.append(coeff * self.Wi[0])

    def update(self, x: float, atarg: float, btarg: float, coeff: float):
        self.Wi.append(laplace(x, self.Ex, atarg, btarg) / self.omega)
        self.W.append(self.W[-1] + coeff * self.Wi[-1])

    def get_efficiency(self) -> float:
        return len(self.W) * self.cost / self.W[-1]
