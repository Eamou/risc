
from typing import List, Tuple


class RISCProcessor:
    def __init__(self, data_reg_size =10, status_reg_size =10):
        # look-up table for instructions
        self.instrs = { 'NOP': (lambda x: x), 'HALT': self._halt, 'CMP': (lambda x: self._logic(x, '=')),
        'JMP': self._jmp, 'LOAD': self._load, 'STORE': self._store, 'ADD': (lambda x: self._logic(x, '+')),
        'SUB': (lambda x: self._logic(x, '-')), 'MULT': lambda x: self._logic(x, '*') }

        # system variables
        self.data_regs = { str(x): 0 for x in range(data_reg_size) }
        self.status_regs = { str(x): 0 for x in range(status_reg_size) }
        self.memory = {}
        self.pc = 0
        self.run = True
        self.complexity = 0;

    def _halt(self, *args) -> (None):
        ''' HALT - stops machine'''
        self.run = False
    
    def _jmp(self, args: List[str]) -> (None):
        ''' JMP - resets what next instruction is. Possibly conditional on state of
        a given status register
        Eg: JMP 2 1 = if 1, pc = 2, else pc = pc
        '''
        if len(args) == 1:
            self.pc = int(args[0])
        else:
            self.pc = int(args[0]) if self.status_regs[args[1]] else self.pc
        self.complexity += 4

    def _load(self, args: List[str]) -> (None):
        '''LOAD - transfers contents of memory location to data register
        Eg: LOAD 0 1 = mem[0] -> dreg[1]
        '''
        self.data_regs[args[1]] = self.memory.get(args[0], 0)
        self.complexity += 2

    def _store(self, args: List[str]) -> (None):
        '''STORE - transfers contents of data register to specified memory location
        Eg: STORE 0 1 = dreg[0] -> dreg[1]
        '''
        self.memory[args[1]] = self.data_regs[args[0]]
        self.complexity += 2

    def _logic(self, args: List[str], mode: str) -> (None):
        '''Deriving from the lambda functions in the instruction dictionary, this
        function performs arithmetic and comparison operations'''
        arg1 = int(args[0][1:]) if args[0][0] == '#' else self.data_regs[args[0]]
        # use absolute value if # present, otherwise fetch from data register
        arg2 = int(args[1][1:]) if args[1][0] == '#' else self.data_regs[args[1]]
        if mode == '+':
            self.data_regs[args[2]] = arg1 + arg2
        elif mode == '-':
            self.data_regs[args[2]] = arg1 - arg2
        elif mode == "*":
            self.data_regs[args[2]] = arg1 * arg2
        elif mode == "=":
            self.status_regs[args[2]] = arg1 == arg2
        self.complexity += 4

    def parseInputData(self, filename: str ='inputdata.txt') -> (None):
        '''Attempts to read ./inputdata.txt which contains data register locations & values to be put
        in those locations. Catches errors such as incorrect number of arguments and incorrect address type'''
        try:
            inputdatafile = open(filename, 'r')
        except FileNotFoundError:
            raise Exception("{filename} does not exist, please check the path".format(filename=filename))
        while True:
            line = inputdatafile.readline()
            if not line:
                break
            line_as_arr = line.strip().split(' ') # convert strings to ints
            if len(line_as_arr) != 2:
                inputdatafile.close()
                raise Exception("Lines should contain exactly two numbers: [address] [data]")
            addr, data = line_as_arr
            if int(addr) < len(self.data_regs):
                try:
                    self.data_regs[addr] = int(data)
                except KeyError:
                    inputdatafile.close()
                    raise Exception("Address should be a number")
            else:
                inputdatafile.close()
                raise Exception("Memory address {addr} not in range: 0-{maxaddr}"
                .format(addr = addr, maxaddr = len(self.data_regs)-1))
        inputdatafile.close()

    def _validateInstruction(self, instr: List[str]) -> (Tuple[bool, str]):
        '''This function will validate a given line from program.txt to see if it
        is a valid instruction as per keywords, number of and type of arguments'''
        instr_word = instr[0]
        if len(instr_word) < 3 or len(instr_word) > 5:
            return (False, instr_word + " is not a valid keyword")
        else:
            if instr_word == "NOP" or instr_word == "HALT":
                return (True, "") if len(instr) == 1 else (False, instr_word + " should have 0 arguments")
            elif instr_word == "ADD" or instr_word == "SUB" or instr_word == "CMP" or instr_word == "MULT":
                if len(instr) != 4:
                    return (False, instr_word + " should have 3 arguments")
                else: # handle direct values as arguments
                    for arg in instr[1:3]: # middle 2 can be int or #int
                        try:
                            int(arg)
                        except ValueError:
                            if arg[0] != '#' or len(arg) == 1: # cannot be just #, but must start with #
                                return (False, instr_word + " arguments 1 and 2 must be int or #int")
                            else:
                                try: # anything after # must be an integer
                                    int(arg[1:])
                                except:
                                    return (False, instr_word + " # must be followed by integer")
                    try:
                        int(instr[3])
                        return (True, "")
                    except ValueError:
                        return (False, instr_word + " final argument must be int")
                        
            elif instr_word == "LOAD" or instr_word == "STORE":
                if len(instr) != 3:
                    return (False, instr_word + " should have 2 arguments")
            elif instr_word == "JMP":
                if len(instr) < 2 or len(instr) > 3:
                    return (False, instr_word + " should have 1 or 2 arguments")
            else:
                return (False, instr_word + " is not a valid keyword")
            try:
                list(map(int,instr[1:])) # try to convert args to ints from strs
                return (True, "")
            except ValueError:
                return (False, "Arguments should be integers")
        '''TODO:
        * check registers/memory are in range?
        * comments?
        '''

    def loadProgramToMemory(self, filename: str ='program.txt') -> (None):
        '''Attempts to read ./program.txt and loads program into memory whereby program.txt is a list of
        line-separated instructions'''
        try:
            programfile = open(filename, 'r')
        except FileNotFoundError:
            raise Exception("{filename} does not exist, please check path".format(filename=filename))
        line_num = 0
        while True:
            line = programfile.readline()
            if not line:
                break
            line_as_arr = line.strip().split(' ')
            valid_instr, err = self._validateInstruction(line_as_arr)
            if valid_instr:
                self.memory[line_num] = line_as_arr
            else:
                programfile.close()
                raise Exception("line {ln}: {err}".format(ln = line_num+1, err = err))
            line_num += 1
        programfile.close()

    def execute(self) -> (Tuple[dict, dict, dict, int, int]):
        '''Executes the program using the following logic:
        1) Retrieve instruction from memory address specified by Program Counter (pc)
        2) Increment program counter
        3) Decode instruction - fetch any required data from memory
        4) Execute and perform any modifications to PC, e.g, from JMP instruction
        We assume all instructions in memory are valid, but memory address may not be.'''
        while self.run:
            if self.pc in self.memory.keys():
                cur_instr = self.memory[self.pc]
                self.pc += 1
                if type(cur_instr) == int: # skip any memory locations that aren't instructions
                    continue
                instr = cur_instr[0]
                self.instrs[instr](cur_instr[1:]) # cast addresses to integers from str.
            else:
                break
        return (self.status_regs, self.data_regs, self.memory, self.pc, self.complexity)


def main():
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.parseInputData('./algos/sum/inputdata.txt')
    myRiscProcessor.loadProgramToMemory('./algos/sum/program.txt')
    status_regs, data_regs, memory, pc, complexity = myRiscProcessor.execute()

    print('### BEGIN STATUS REGISTERS ###')
    print(status_regs)
    print('### END STATUS REGISTERS ###\n')
    print('### BEGIN DATA REGISTERS ###')
    print(data_regs)
    print('### END DATA REGISTERS ###\n')
    print('### BEGIN MEMORY ###')
    print(memory)
    print('### END MEMORY ###\n')
    print('### BEING PC ###')
    print(pc)
    print('### END PC ###\n')
    print('COMPLEXITY: ', complexity)

if __name__ == '__main__':
    main()

'''
TODO:
* DIV
* linked lists how?
* test suite
* cache?
'''