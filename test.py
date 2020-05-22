from multiprocessing import Pool
import time
import os


def f(x):
    return x*x


if __name__ == '__main__':
    dr = os.path.dirname(os.path.abspath(__file__))
    print(dr)
