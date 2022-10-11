
from typing import List, OrderedDict, Tuple

class ValidationException(Exception):
    def __init__(self, *args):
        if len(args) == 1:
            super().__init__(args[0])
        else:
            super().__init__()

class RISCProcessor:
    def __init__(self, data_reg_size: int =10, status_reg_size: int =10, cache_size: int =4):
        # look-up table for instructions
        self.instrs = { 'NOP': (lambda x: x), # use lamdbas to 'route' into _logic() to avoid redundant methods
                        'HALT': self._halt, 
                        'CMP': (lambda x: self._logic(x, '=')),
                        'CNE': (lambda x: self._logic(x, '<>')),
                        'JMP': self._jmp, 
                        'LOAD': self._load, 
                        'STORE': self._store, 
                        'ADD': (lambda x: self._logic(x, '+')),
                        'SUB': (lambda x: self._logic(x, '-')), 
                        'MULT': lambda x: self._logic(x, '*')
                    }
        
        self.bin_instr_lookup = {
            '0000': 'NOP',
            '0001': 'HALT',
            '0010': 'CMP',
            '0011': 'JMP', # reg conditional
            '0100': 'JMP2', # not reg conditional
            '0101': 'LOAD',
            '0110': 'STORE',
            '0111': 'ADD',
            '1000': 'SUB',
            '1001': 'MULT',
            '1010': 'CNE'
        }

        # used for assigning correct number of arguments in binary decoding
        self.num_args = {
                'CMP': 3,
                'ADD': 3,
                'SUB': 3,
                'MULT': 3,
                'CNE': 3,
                'LOAD': 2,
                'STORE': 2,
                'JMP': 2,
                'JMP2': 1
            }

        # system variables
        self.data_regs = { str(x): 0 for x in range(data_reg_size) }
        self.status_regs = { str(x): 0 for x in range(status_reg_size) }
        self.memory = {}
        self.cache = OrderedDict()
        self.cache_capacity = cache_size
        self.pc = 0
        self.run = True
        self.complexity = 0

    def _fetch(self, addr: str) -> (int):
        '''Attempt to retrieve data from the cache - if not present, add it to
        the cache based on LRU replacement policy, and fetch from memory instead.'''
        if addr in self.cache:
            self.cache.move_to_end(addr) # move item to reflect most recently used
        else:
            self.cache[addr] = self.data_regs.get(addr, 0)
            self.cache.move_to_end(addr)              # move item to reflect most recently used
            if len(self.cache) > self.cache_capacity: # if we are out of capacity in cache;
                self.cache.popitem(last = False)      # drop the least recently used
        return self.cache[addr]

    def _write(self, addr: str, data: int) -> (None):
        '''Write to data registers and cache - our cache is a write-through cache,
        so whenever we write data to a data register, we also write to the cache.'''
        self.data_regs[addr] = data
        if addr in self.cache.keys():
            self.cache[addr] = data

    def _halt(self, *args) -> (None):
        ''' HALT - stops machine'''
        self.run = False
    
    def _jmp(self, args: List[str]) -> (None):
        ''' JMP - resets what next instruction is. Possibly conditional on state of
        a given status register
        Eg: JMP 2 1 == if 1, pc = 2, else pc = pc
        '''
        if len(args) == 1 or self.status_regs[args[1]]:
            self.pc = int(args[0])
        self.complexity += 4

    def _load(self, args: List[str]) -> (None):
        '''LOAD - transfers contents of memory location to data register
        Eg: LOAD 0 1 = mem[0] -> dreg[1]
        '''
        self._write(args[1], self.memory.get(args[0], 0))
        self.complexity += 2

    def _store(self, args: List[str]) -> (None):
        '''STORE - transfers contents of data register to specified memory location
        Eg: STORE 0 1 = dreg[0] -> dreg[1]
        '''
        self.memory[args[1]] = self._fetch(args[0])
        self.complexity += 2

    def _logic(self, args: List[str], mode: str) -> (None):
        '''Deriving from the lambda functions in the instruction dictionary, this
        function performs arithmetic and comparison operations'''
        arg1 = int(args[0][1:]) if args[0][0] == '#' else self._fetch(args[0])
        # use absolute value if # present, otherwise is address so fetch from data register
        arg2 = int(args[1][1:]) if args[1][0] == '#' else self._fetch(args[1])
        result = None
        if mode == '+':
            result = arg1 + arg2
        elif mode == '-':
            result = arg1 - arg2
        elif mode == '*':
            result = arg1 * arg2
        if result is not None:
            self._write(args[2], result)
        elif mode == '=': # need to write to status_register, hence cannot use self._write
            self.status_regs[args[2]] = arg1 == arg2
        elif mode == '<>':
            self.status_regs[args[2]] = arg1 != arg2
        self.complexity += 4

    def parseInputData(self, filename: str ='inputdata.txt') -> (None):
        '''Attempts to read ./inputdata.txt which contains data register locations & values to be put
        in those locations. Catches errors such as incorrect number of arguments and incorrect address type'''
        try:
            with open(filename, 'r') as input_data_file:
                lines = input_data_file.read().splitlines(keepends=False)
            for line in lines:
                if not line: # skip empty lines
                    break
                line_as_arr = line.strip().split(' ') # remove all \n and turn into array
                if len(line_as_arr) != 2: # all lines must contain an address and data, always 2 numbers
                    raise ValidationException(f'{filename}: Lines should contain exactly two numbers: [address] [data]')
                addr, data = line_as_arr
                if int(addr) < len(self.data_regs): # if the register exists
                    if not addr.isnumeric():
                        raise ValidationException(f'{filename}: Address should be a number')
                    self.data_regs[addr] = int(data)
                else:
                    raise ValidationException(f'{filename}: Memory address {addr} not in range: 0-{len(self.data_regs)-1}')
        
        except FileNotFoundError:
            raise Exception("{filename} does not exist, please check the path".format(filename=filename))

    def _decodeBinaryInstruction(self, instr: str) -> (list[str]):
        try:
            split_instr = self._validateBinaryInstruction(instr.strip())
        except ValidationException as e:
            raise ValidationException(f'Instruction validation error: {e}')
        decoded_instr = []
        instr_word, *args = self.bin_instr_lookup[split_instr[0]], split_instr[1], split_instr[2], split_instr[3]

        num_args = self.num_args.get(instr_word, 0)

        args = args[:num_args]

        if instr_word == 'JMP2':
            instr_word = 'JMP'

        decoded_instr = [instr_word] + [str(int(arg, 2)) for arg in args]

        return decoded_instr

    def _validateBinaryInstruction(self, instr: str) -> (list[str]):
        '''Validates the instructions when given in 16bit binary encoding.
        FORMAT:
        [instr][arg1][arg2][dest]
        with each component represented by 4 bits'''
        if len(instr) != 16:
            raise ValidationException('Instructions must be 16 bits in length')
        else:
            # split array into each 4 bit block
            instr, arg1, arg2, dest = [instr[i:i+4] for i in range(0, 16, 4)]
            if instr not in self.bin_instr_lookup.keys():
                raise ValidationException(f'Instruction not recognised: {instr}')
            else:
                try:
                    int(arg1, 2)
                    int(arg2, 2)
                    int(dest, 2)
                except ValueError:
                    raise ValidationException('Arguments must be valid binary strings')
        return [instr, arg1, arg2, dest]

    def _validateInstruction(self, instr: List[str]) -> (None):
        '''This function will validate a given line from program.txt to see if it
        is a valid instruction as per keywords, number of and type of arguments'''
        instr_word = instr[0]
        if len(instr_word) < 3 or len(instr_word) > 5: # all instrs are 3/4/5 chars long
            raise ValidationException(f'{instr_word} is not a valid keyword')
        if instr_word == 'NOP' or instr_word == 'HALT':
            if len(instr) != 1: raise Exception(f'{instr_word} should have 0 arguments')
        elif instr_word in ['ADD', 'SUB', 'CMP', 'MULT', 'CNE']: # instrs with 3 args
            if len(instr) != 4:
                raise ValidationException(f'{instr_word} should have 3 arguments')
            # handle direct values as arguments
            for arg in instr[1:3]: # middle 2 can be int or #int
                try:
                    int(arg)
                except ValueError:
                    if arg[0] != '#' or len(arg) == 1: # cannot be just #, but must start with #
                        raise ValidationException(f'{instr_word} arguments 1 and 2 must be int or #int')
                    try: # anything after # must be an integer
                        int(arg[1:])
                    except ValueError:
                        raise ValidationException(f'{instr_word} # must be followed by integer')
            try:
                int(instr[3]) # final argument is result destination in data reg, so must be int
            except ValueError:
                raise ValidationException(f'{instr_word} final argument must be int')
                    
        elif instr_word == 'LOAD' or instr_word == 'STORE': # instrs with 2 args
            if len(instr) != 3:
                raise ValidationException(f'{instr_word} should have 2 arguments')
            try:
                list(map(int,instr[1:])) # try to convert args to ints from strs
            except ValueError:
                raise ValidationException('Arguments should be integers')
        elif instr_word == 'JMP': # JMP can have 1 or 2 arguments
            if len(instr) < 2 or len(instr) > 3:
                raise ValidationException(f'{instr_word} should have 1 or 2 arguments')
            try:
                list(map(int,instr[1:])) # try to convert args to ints from strs
            except ValueError:
                raise ValidationException('Arguments should be integers')
        else:
            raise ValidationException(f'{instr_word} is not a valid keyword')

    def loadProgramToMemory(self, filename: str ='program.txt') -> (None):
        '''Attempts to read ./program.txt and loads program into memory, where program.txt is a list of
        line-separated instructions'''
        try:
            with open(filename, 'r') as program_file:
                lines = program_file.read().splitlines(keepends=False)
            for line_num, line in enumerate(lines):
                instr_as_arr= []
                if not line.strip():
                    continue
                try:
                    if filename[-3:] == 'txt':
                        instr_as_arr = line.strip().split(' ')
                        self._validateInstruction(instr_as_arr)
                    elif filename[-3:] == 'bin':
                        instr_as_arr = self._decodeBinaryInstruction(line)
                    self.memory[line_num] = instr_as_arr # load instruction into next available memory addr
                except ValidationException as e:
                    raise ValidationException(f'line {line_num+1}: {e}')
                line_num += 1
        except FileNotFoundError:
            raise Exception(f'{filename} does not exist, please check path')

    def execute(self) -> (Tuple[dict[str, int], dict[str, int], dict[int, int], OrderedDict[str, int], int, int]):
        '''Executes the program using the following logic:
        1) Retrieve instruction from memory address specified by Program Counter (pc)
        2) Increment program counter
        3) Decode instruction - fetch any required data from memory
        4) Execute and perform any modifications to PC, e.g, from JMP instruction
        We assume all instructions in memory are valid, but memory address may not be.
        Returns the stateful machine properties.'''
        while self.run:
            if self.pc in self.memory.keys():
                cur_instr = self.memory[self.pc]
                self.pc += 1
                if isinstance(cur_instr, int): # skip any memory locations that aren't instructions
                    continue
                instr = cur_instr[0]
                self.instrs[instr](cur_instr[1:])
            else:
                break
        return (self.status_regs, self.data_regs, self.memory, self.cache, self.pc, self.complexity)


def main():
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.parseInputData('./inputdata.txt')
    myRiscProcessor.loadProgramToMemory('./program.txt')
    status_regs, data_regs, memory, cache, pc, complexity = myRiscProcessor.execute()

    print(
    '### BEGIN STATUS REGISTERS ###\n'
    f'{status_regs}\n'
    '### END STATUS REGISTERS ###\n')

    print('### BEGIN DATA REGISTERS ###\n'
    f'{data_regs}\n'
    '### END DATA REGISTERS ###\n')

    print('### BEGIN CACHE ###\n'
    f'{cache}\n'
    '### END CACHE ###\n')

    print('### BEGIN MEMORY ###\n'
    f'{memory}\n'
    '### END MEMORY ###\n')

    print('### BEING PC ###\n'
    f'{pc}\n'
    '### END PC ###\n')

    print('COMPLEXITY: ', complexity)

if __name__ == '__main__':
    main()