from helpers import process_data, laplace
from scene import Scene
import mytypes as tp
import visual

import csv


def main():
    # Data init
    data = None
    with open('data (old).csv', 'r') as file:
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
    print(tank)
    spam = tp.SPAM(data, spam_var)
    print(spam)
    scene = Scene(data)
    print(scene)

    tf, xf, W, V = scene.start(spam, tank, acc=acc, out=False)
    show_results(tf, xf, W, V, tank_var, spam_var, acc=acc)

    spam_var = '152'
    spam.set_variant(data, spam_var)
    tf, xf, W, V = scene.start(spam, tank, acc=acc, out=False)
    show_results(tf, xf, W, V, tank_var, spam_var, acc=acc)

    spam_var = 'ptur'
    spam.set_variant(data, spam_var)
    tf, xf, W, V = scene.start(spam, tank, acc=acc)
    show_results(tf, xf, W, V, tank_var, spam_var, acc=acc)


def show_results(tf: float, xf: float, W: list, V: list, tank_var: str, spam_var: str, acc: int = 3):
    print(f"\nResults for {tank_var} and {spam_var}:"
          f"\tt = {tf}\tx = {xf} [m]")
    if len(W) == len(V):
        for i, (w, v) in enumerate(zip(W, V)):
            print(f"\tW{i + 1} = {round(w, acc)}\tV{i + 1} = {round(v, acc)}")
    else:
        for i, w in enumerate(W):
            print(f"\tW{i + 1} = {round(w, acc)}")
        for i, v in enumerate(V):
            print(f"\tV{i + 1} = {round(v, acc)}")


if __name__ == '__main__':
    main()
else:
    print("Error: no entering point!")
    exit(-1)
