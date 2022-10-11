
from main import RISCProcessor, ValidationException

import unittest

class ExceptionTests(unittest.TestCase):

    def testBinaryFibonacci(self):
        result = test('binary fibonacci test', './algos/fib/binary/inputdata.txt',\
        './algos/fib/binary/program.bin', {'0': True}, {'0': 8, '1': 13}, \
        {0: ['ADD', '0', '1', '1'], 1: ['SUB', '2', '3', '2'], 2: ['CMP', '2', '4', '0'], 3: ['JMP', '10', '0'], 4: ['ADD', '0', '1', '0'], 5: ['SUB', '2', '3', '2'], 6: ['CMP', '2', '4', '0'], 7: ['JMP', '10', '0'], 8: ['JMP', '0'], 9: ['HALT']},\
            [], 10)
        self.assertEqual(result, 'OK')
    
    def testCache(self):
        result = test('cache test', './algos/cache_test/inputdata.txt',\
        './algos/cache_test/program.txt', {'0': 0}, {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6},\
            {}, [('3', 4), ('5', 6), ('2', 3), ('4', 5)], 8)
        self.assertEqual(result, 'OK')

    def testSum(self):
        result = test('sum', './algos/sum/inputdata.txt', './algos/sum/program.txt',\
        {'0': True}, {'0': 15, '1': 0}, {}, [], 7)
        self.assertEqual(result, 'OK')

    def testFibonacci(self):
        result = test('fib', './algos/fib/abs_val_ver/inputdata.txt',\
        './algos/fib/abs_val_ver/program.txt', {'0': True}, {'0': 8, '1': 13}, {}, [], 10)
        self.assertEqual(result, 'OK')

    def testFactorial(self):
        result = test('factorial', './algos/factorial/inputdata.txt',\
        './algos/factorial/program.txt', {'0': True}, {'0': 120, '1': 0}, {}, [], 7)
        self.assertEqual(result, 'OK')
    
    def testInvalidInstruction(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_instr/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_instr/program.txt')
            rp.execute()
    
    def testInvalidArgument(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_arg/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_arg/program.txt')
            rp.execute()

    def testInvalidAbsVal(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_abs_val/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_abs_val/program.txt')
            rp.execute()

    def testInvalidReg(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_reg/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_reg/program.txt')
            rp.execute()

    def testInvalidJmpArg(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_jmp_arg/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_jmp_arg/program.txt')
            rp.execute()
    
    def testInvalidBinaryInstruction(self):
        with self.assertRaises(ValidationException):
            rp=RISCProcessor()
            rp.parseInputData('./tests/invalid_bin_instr/inputdata.txt')
            rp.loadProgramToMemory('./tests/invalid_bin_instr/program.bin')
            rp.execute()

def failString(testname: str, component: str, position, expected, actual) -> (str):
    '''create the string used to describe a test failure, given the components of the test'''
    return  f'test: {testname} - {component} {position}: expected: {expected} | actual: {actual}'

def test(testname:str, inputfile: str, programfile: str, sreg_vals: dict[str, int], dreg_vals: dict[str, int],\
         mem_vals: dict[int, list], cache_vals: list, pc_val: int) -> (str):
    '''test the output values of the processor against given expected values'''
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.parseInputData(inputfile)
    myRiscProcessor.loadProgramToMemory(programfile)
    status_regs, data_regs, memory, cache, pc, _ = myRiscProcessor.execute()
    for k in sreg_vals.keys():
        assert status_regs[k] == sreg_vals[k], failString(testname, 'status register', k, sreg_vals[k], status_regs[k])
    
    for k in dreg_vals.keys():
        assert data_regs[k] == dreg_vals[k], failString(testname, 'data register', k, dreg_vals[k], data_regs[k])
    
    for k in mem_vals.keys():
        assert memory[k] == mem_vals[k], failString(testname, 'memory', k, mem_vals[k], memory[k])

    for i, item in enumerate(cache_vals):
        key,value = cache.popitem(last = False)
        assert key == item[0] and value == item[1], failString(testname, 'cache', i, item, (key,value))

    assert pc == pc_val, failString(testname, 'program counter', 0, pc_val, pc)
    return 'OK'

if __name__ == '__main__':
    unittest.main()