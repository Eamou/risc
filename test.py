
from main import RISCProcessor

def test(testname:str, inputfile: str, programfile: str, sreg_vals: dict[str, int], dreg_vals: dict[str, int],\
         mem_vals: dict[int, int], cache_vals: list, pc_val: int) -> (str):
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.parseInputData(inputfile)
    myRiscProcessor.loadProgramToMemory(programfile)
    status_regs, data_regs, memory, cache, pc, complexity = myRiscProcessor.execute()
    for k in sreg_vals.keys():
        assert status_regs[k] == sreg_vals[k], "test: {name} - Status register {k}: excpected: {v} | actual: {vactual}"\
            .format(name=testname, k=int(k), v=sreg_vals[k], vactual=status_regs[k])
    
    for k in dreg_vals.keys():
        assert data_regs[k] == dreg_vals[k], "test: {name} - Data register {k}: expected: {v} | actual: {vactual}"\
            .format(name=testname, k=int(k), v=dreg_vals[k], vactual=data_regs[k])
    # memory test
    for i, item in enumerate(cache_vals):
        key,value = cache.popitem(last = False)
        assert key == item[0] and value == item[1], "test: {name} - Cache pos {i}: expected {e} | actual {a}"\
            .format(name=testname, i=i, e=item, a=(key,value))

    assert pc == pc_val, "test: {name} - Program counter: expected {v} | actual: {vactual}"\
            .format(name=testname, v=pc_val, vactual=pc)
    return "OK"

def main():
    results = {}
    results['factorialTest'] = test('factorial', './algos/factorial/inputdata.txt',\
        './algos/factorial/program.txt', {'0': True}, {'0': 120, '1': 0}, {}, [], 7)
    results['fibTest'] = test('fib', './algos/fib/abs_val_ver/inputdata.txt',\
        './algos/fib/abs_val_ver/program.txt', {'0': True}, {'0': 8, '1': 13}, {}, [], 10)
    results['sumTest'] = test('sum', './algos/sum/inputdata.txt', './algos/sum/program.txt',\
        {'0': True}, {'0': 15, '1': 0}, {}, [], 7)
    results['cacheTest'] = test('cache test', './algos/cache_test/inputdata.txt',\
        './algos/cache_test/program.txt', {'0': 0}, {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6},\
            {}, [('3', 4), ('5', 6), ('2', 3), ('4', 5)], 8)
    print("starting tests...\n")
    for k in results.keys():
        print("{k}: {v}".format(k=k, v=results[k]))

if __name__ == '__main__':
    main()