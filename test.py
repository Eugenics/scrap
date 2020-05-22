from multiprocessing import Pool
import time
import os


def f(x):
    return x*x


if __name__ == '__main__':
    with Pool(processes=os.cpu_count()) as pool:         # start 4 worker processes        
        # evaluate "f(10)" asynchronously in a single process
        result = pool.apply_async(f, (100000,))
        # prints "100" unless your computer is *very* slow
        print(result.get(timeout=1))

        print(pool.map(f, range(10)))       # prints "[0, 1, 4,..., 81]"

        it = pool.imap(f, range(10))
        print(next(it))                     # prints "0"
        print(next(it))                     # prints "1"
        # prints "4" unless your computer is *very* slow
        print(it.next(timeout=1))

        result = pool.apply_async(time.sleep, (10,))
        # raises multiprocessing.TimeoutError
        #print(result.get(timeout=1))
