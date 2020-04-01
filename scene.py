import mytypes as tp
import helpers as hlp

from copy import copy
from numpy import array as nparray


class Scene:
    def __init__(self, data: dict):
        self.data = data.copy()
        self.t0 = data['t0']
        self.x0 = data['x0']

        self.time, self.x = None, None
        self.events = None
        self.v = None
        self.tank, self.spam = None, None
        self.t_tank, self.t_spam = None, None

    def __str__(self):
        return f"Scene:" \
               f"\n - tank's first shot time = {self.t0} [s]" \
               f"\n - x0 = {self.x0} [m]" \
               f"\n - {self.spam}" \
               f"\n - {self.tank}"

    def get_spam_efficiency(self) -> float:
        return self.spam.get_efficiency()

    def start(self, spam: tp.SPAM, tank: tp.Tank, acc: int = 3,
              out: bool = False, ptur_num: int = 3) -> tuple:
        self.time, self.x = None, None
        self.t_tank, self.t_spam = None, None
        self.events = None
        self.spam, self.tank = copy(spam), copy(tank)
        self.v = abs(self.spam.v - self.tank.v)

        if self.spam.var == 'ptur':
            self.t_spam, self.t_tank, self.events = self.__calc_guided(num=ptur_num, acc=acc)
        else:
            self.__calc_unguided(acc=acc)

        if out:
            print("Sequencing results:")
            print(' events:')
            for i, (s1, s2) in enumerate(zip(self.events[::2], self.events[1::2])):
                print(f"\t{i + 1}.\t({s1}, {s2})")
            print(' time:')
            for i, (t1, t2) in enumerate(zip(self.time[::2], self.time[1::2])):
                print(f"\t{i + 1}.\t({round(t1, acc)}, {round(t2, acc)})")
            print(f" x:")
            for i, (x1, x2) in enumerate(zip(self.x[::2], self.x[1::2])):
                print(f"\t{i + 1}.\t({round(x1, acc)}, {round(x2, acc)})")

        if self.spam.var == 'ptur':
            x_spam = [hlp.get_dist(self.x0, -self.v, t) for t in self.t_spam]
            x_tank = [hlp.get_dist(self.x0, -self.v, t) for t in self.t_tank]

            return self.events, self.t_spam, self.t_tank, x_spam, x_tank, self.spam.W, self.tank.V
        return self.events, self.time, self.x, self.spam.W, self.tank.V

    def __calc_unguided(self, acc: int = 3):
        self.events, self.time, self.x = self.__get_sequence_unguided()

        self.spam.starting_update(self.x[0], self.tank.a, self.tank.b, 1)
        self.tank.starting_update(self.x[1], self.spam.a, self.spam.b, self.__get_coeff())

        for event, t, x in zip(self.events, self.time, self.x):
            if round(self.spam.W[-1] + self.tank.V[-1], acc) == 1:
                break
            if event == 'spam':
                self.spam.update(x, self.tank.a, self.tank.b, self.__get_coeff())
            else:
                self.tank.update(x, self.spam.a, self.spam.b, self.__get_coeff())

    def __get_sequence_unguided(self) -> tuple:
        t1, t2 = 0, self.t0
        x1, x2 = self.x0, hlp.get_dist(self.x0, -self.v, self.t0)

        events, time, dist = ['spam', 'tank'], [t1, t2], [x1, x2]
        while min(x1, x2) > self.x0 / 10:
            # SPAM (W)
            t1 += self.spam.t_shot
            x1 = hlp.get_dist(self.x0, -self.v, t1)

            # Tank (V)
            t2 += self.tank.t_shot
            x2 = hlp.get_dist(self.x0, -self.v, t2)

            if t1 > t2:
                t1 -= self.spam.t_shot

                events.append('tank')
                time.append(t2)
                dist.append(x2)
                continue

            events.extend(['spam', 'tank'])
            time.extend([t1, t2])
            dist.extend([x1, x2])

        return nparray(events), nparray(time), nparray(dist)

    def __calc_guided(self, num: int = 7, acc: int = 3) -> tuple:
        v_relative = self.data['vptur'] + self.data['vt']
        x = self.x0
        t = x / v_relative
        time = t

        nseq, t_spam = [int((t - self.t0) / self.tank.t_shot) + 1], [t]
        for i in range(num - 1):
            x = hlp.get_dist(self.x0, -self.v, time)
            time += x / v_relative
            t_spam.append(time)

            t = time - t
            t_rem = time - self.t0
            n_total = int(t_rem / self.tank.t_shot) + 1
            nseq.append(n_total - sum(nseq))
        t_tank, events = self.__get_sequence_guided(nseq)

        print(f"\nTank t: {t_tank}\nSPAM t: {t_spam}\nTank's shots: {nseq}\nEvents: {events}")

        self.tank.starting_update(hlp.get_dist(self.x0, -self.v, self.t0), self.spam.a, self.spam.b, 1)
        i, j = 1, 0
        for event in events[1:]:
            if event == 'spam':
                if not self.spam.Wi:
                    self.spam.starting_update(hlp.get_dist(self.x0, -self.v, t_spam[j]), self.tank.a, self.tank.b, self.__get_coeff())
                else:
                    self.spam.update(hlp.get_dist(self.x0, -self.v, t_spam[j]), self.tank.a, self.tank.b, self.__get_coeff())
                j += 1
            else:
                self.tank.update(hlp.get_dist(self.x0, -self.v, t_tank[i]), self.spam.a, self.spam.b, self.__get_coeff())
                i += 1

            if round(self.tank.V[-1] + self.spam.W[-1], acc) >= 1:
                break

        return t_spam, t_tank, events

    def __get_sequence_guided(self, tank_shots: list) -> tuple:
        t, time = self.t0, []
        events = []
        for shots in tank_shots:
            for i in range(shots):
                events.append('tank')
                time.append(t)
                t += self.tank.t_shot
            events.append('spam')
        return time, events

    def __get_coeff(self) -> float:
        mul = 1
        for w in self.spam.Wi:
            mul *= 1 - w
        for v in self.tank.Vi:
            mul *= 1 - v
        return mul
