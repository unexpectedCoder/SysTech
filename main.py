from helpers import process_data, laplace
from scene import Scene
import mytypes as tp
import visual

import csv


def main():
    # Data init
    data = None
    with open('data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data = row
    print(f"Read data:\n{data}")

    # Data preparing
    try:
        data = process_data(data)
        print(f"Processed data:\n{data}")
    except ValueError:
        print("Error: invalid initial data dictionary!")
        exit(-1)

    # Visualization
    visual.show_laplace(laplace, data)

    # Solution
    acc = 4         # Output accuracy
    spam_var, tank_var = '100', '100t'
    tank = tp.Tank(data, tank_var)
    spam = tp.SPAM(data, spam_var)
    scene = Scene(data)

    print(f"\nInit:\n{tank}\n{spam}\n{scene}\n")

    efficiency = {}                                                          # Efficiency coefficient
    events, time, dist, W, V = scene.start(spam, tank, acc=acc, out=False)
    efficiency[spam_var] = round(scene.get_spam_efficiency(), acc // 3)
    # Out
    show_results(events, time, dist, W, V, tank_var, spam_var, acc=acc)

    spam_var = '152'
    spam.set_variant(data, spam_var)
    events, time, dist, W, V = scene.start(spam, tank, acc=acc, out=False)
    efficiency[spam_var] = round(scene.get_spam_efficiency(), acc // 3)
    # Out
    show_results(events, time, dist, W, V, tank_var, spam_var, acc=acc)

    spam_var = 'ptur'
    spam.set_variant(data, spam_var)
    events, t_spam, t_tank, x_spam, x_tank, W, V = scene.start(spam, tank, acc=acc, ptur_num=10)
    efficiency[spam_var] = round(scene.get_spam_efficiency(), acc // 3)
    # Out
    time, dist = (t_spam, t_tank), (x_spam, x_tank)
    show_results_ptur(time, dist, W, V, tank_var, spam_var, acc=acc)

    print(f"\nResult:"
          f"\n - efficiency coefficients: {efficiency}")


def show_results(events: list, time: list, dist: list, W: list, V: list, tank_var: str, spam_var: str, acc: int = 3):
    print(f"\nResults for '{spam_var}' vs '{tank_var}':")

    etd_w = [etd for etd in zip(events, time, dist) if etd[0] == 'spam']
    print("SPAM:")
    for i, (etd, w) in enumerate(zip(etd_w, W)):
        print(f" shot #{i + 1}:\tt = {round(etd[1], acc)} [s]\tx = {round(etd[2], acc)} [m]\tW = {round(w, acc)}")

    print("Tank:")
    etd_v = [etd for etd in zip(events, time, dist) if etd[0] == 'tank']
    for i, (etd, v) in enumerate(zip(etd_v, V)):
        print(f" shot #{i + 1}:\tt = {round(etd[1], acc)} [s]\tx = {round(etd[2], acc)} [m]\tV = {round(v, acc)}")


def show_results_ptur(time: tuple, dist: tuple, W: list, V: list, tank_var: str, spam_var: str, acc: int = 3):
    print(f"\nResults for '{spam_var}' vs '{tank_var}':")
    print("SPAM:")
    for i, (t, x, w) in enumerate(zip(time[0], dist[0], W)):
        print(f" shot #{i + 1}:\tt = {round(t, acc)} [s]\tx = {round(x, acc)} [m]\tW = {round(w, acc)}")
    print("Tank:")
    for i, (t, x, v) in enumerate(zip(time[1], dist[1], V)):
        print(f" shot #{i + 1}:\tt = {round(t, acc)} [s]\tx = {round(x, acc)} [m]\tV = {round(v, acc)}")


if __name__ == '__main__':
    main()
else:
    print("Error: no entering point!")
    exit(-1)
