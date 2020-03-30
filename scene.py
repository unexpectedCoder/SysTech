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

    def __str__(self):
        return f"Scene:" \
               f"\n - tank's first shot time = {self.t0} [s]" \
               f"\n - x0 = {self.x0} [m]" \
               f"\n - {self.spam}" \
               f"\n - {self.tank}"

    def start(self, spam: tp.SPAM, tank: tp.Tank, acc: int = 3, out: bool = False) -> tuple:
        self.spam, self.tank = copy(spam), copy(tank)
        self.v = abs(self.spam.v - self.tank.v)

        if self.spam.var == 'ptur':
            tf, xf = self.__calc_guided()
        else:
            self.events, self.time, self.x = self.get_sequence_unguided()
            tf, xf = self.__calc_unguided(acc=acc)

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

        return tf, xf, self.spam.W, self.tank.V

    def get_sequence_unguided(self) -> tuple:
        t1, t2 = 0, self.t0
        x1, x2 = self.x0, hlp.get_dist(self.x0, -self.v, self.t0)

        indx = 0
        events, time, dist = ['spam', 'tank'], [(t1, t2)], [(x1, x2)]
        while min(x1, x2) > 100:
            # SPAM (W)
            t1 += self.spam.t_shot
            x1 = hlp.get_dist(self.x0, -self.v, t1)
            events.append('spam')

            # Tank (V)
            t2 += self.tank.t_shot
            x2 = hlp.get_dist(self.x0, -self.v, t2)
            events.append('tank')

            time.append((t1, t2))
            dist.append((x1, x2))

            if x1 < x2:
                events[-1], events[-2] = events[-2], events[-1]

            indx += 2
            if events[indx] == 'tank':
                if x2 - x1 < self.v * self.spam.t_shot:
                    time[-1] = time[-1][1], time[-1][0]
                    dist[-1] = dist[-1][1], dist[-1][0]
                else:
                    events[-1], events[-2] = events[-2], events[-1]

        time = nparray([subval for val in time for subval in val])
        dist = nparray([subval for val in dist for subval in val])
        return nparray(events), time, dist

    def __calc_unguided(self, acc: int = 3) -> tuple:
        self.spam.starting_update(self.x[0], self.tank.a, self.tank.b, 1)
        self.tank.starting_update(self.x[1], self.spam.a, self.spam.b, self.__get_coeff())

        tf, xf = None, None
        for event, t, x in zip(self.events, self.time, self.x):
            if round(self.spam.W[-1] + self.tank.V[-1], acc) == 1:
                tf, xf = t, x
                break
            if event == 'spam':
                self.spam.update(x, self.tank.a, self.tank.b, self.__get_coeff())
            else:
                self.tank.update(x, self.spam.a, self.spam.b, self.__get_coeff())

        return tf, xf

    def __calc_guided(self) -> tuple:
        t_tank = self.t0

        v_relative = self.data['vptur'] + self.data['vt']
        x1 = self.x0
        t1 = self.x0 / v_relative
        n1 = int((t1 - self.t0) / self.tank.t_shot) + 1

        x2 = hlp.get_dist(self.x0, -self.v, t1)
        t_total = t1 + x2 / v_relative
        t2 = t_total - t1
        t_rem = t_total - self.data['t0']
        n_total = int(t_rem / self.tank.t_shot) + 1
        n2 = n_total - n1

        t_spam = [t1, t_total]
        t_tank, events = self.__get_sequence_guided([n1, n2])
        print(t_tank, t_spam, events)

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

        print("\nEvents:", events)
        print(f"\n - tank shot time = {self.tank.t_shot} [s]")
        print(f" - relative speed = {v_relative} [m/s]")
        print(f" - x1 = {x1} [m]")
        print(f" - t1 = {t1} [s]")
        print(f" - n1 = {n1}")
        print(f"\n - x2 = {x2} [m]")
        print(f" - t_total = {t_total} [s]")
        print(f" - t2 = {t2} [s]")
        print(f" - n2 = {n2}")
        print(f" - n_total = {n_total}\n")

        return max(t_tank[-1], t_spam[-1]), hlp.get_dist(self.x0, -self.v, max(t_tank[-1], t_spam[-1]))      # xf, tf

    def __get_sequence_guided(self, n: list) -> tuple:
        t, time = self.t0, []
        events = []
        for val in n:
            for i in range(val):
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
