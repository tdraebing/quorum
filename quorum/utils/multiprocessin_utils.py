from multiprocessing import Process


def run_funcs_parallel(funcAndArgs):
    procs = []
    for fargs in funcAndArgs:
        p = Process(target=fargs[0], args=fargs[1])
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
