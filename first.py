import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class DataProcessor:
    def __init__(self):
        pass

    def get_data(self):
        np.random.seed(196808)

        N = 100
        r0 = 0.6
        for i in range(0, N):
            print(i)


if __name__ == "__main__":
    d = DataProcessor()
    print(d.get_data())
