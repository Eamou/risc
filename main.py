
from typing import List


class RISCProcessor:
    def __init__(self, data_reg_size =10, status_reg_size =10, memory_size =10):
        # look-up table for instructions
        self.instrs = { 'NOP': self._nop, 'HALT': self._halt, 'CMP': self._cmp,
        'JMP': self._jmp, 'LOAD': self._load, 'STORE': self._store, 'ADD': self._add,
        'SUB': self._sub }

        # system variables
        self.data_regs = { x: 0 for x in range(data_reg_size) }
        self.status_regs = { x: 0 for x in range(status_reg_size) }
        self.memory = {}
        self.pc = 0
        self.run = True

    def _nop(self, *args: List[int]) -> (None):
        ''' NOP - does nothing to machine state'''
        return

    def _halt(self, *args: List[int]) -> (None):
        ''' HALT - stops machine'''
        self.run = False

    def _cmp(self, registers: List[int]) -> (None):
        ''' CMP - compares contents of two registers, if equal then stores result
        in specified status register. Registers are given as integer addresses
        Eg: CMP 1 2 1
        '''
        d_reg1, d_reg2, s_reg = registers
        if self.data_regs[d_reg1] == self.data_regs[d_reg2]:
            self.status_regs[s_reg] = True
    
    def _jmp(self, args: List[int]) -> (None):
        ''' JMP - resets what next instruction is. Possibly conditional on state of
        a given status register
        Eg: JMP 2 1
        '''
        if len(args) == 1:
            self.pc = args[0]
        else:
            self.pc = args[0] if args[1] else self.pc

    def _load(self, args: List[int]) -> (None):
        '''LOAD - transfers contents of memory location to data register
        Eg: LOAD 1 1
        '''
        self.data_regs[args[1]] = self.memory.get(args[0], 0)

    def _store(self, args: List[int]) -> (None):
        '''STORE - transfers contents of data register to specified memory location
        Eg: STORE 1 1
        '''
        self.memory[args[1]] = self.data_regs[args[0]]

    def _add(self, args: List[int]) -> (None):
        '''ADD - adds contents of two specified data registers and leaves result
        in specified target data register
        Eg: ADD 1 1 1
        '''
        self.data_regs[args[2]] = self.data_regs[args[0]] + self.data_regs[args[1]]

    def _sub(self, args: List[int]) -> (None):
        '''SUB - subtracts first data register from second and leaves result in
        specified target data register
        Eg: SUB 1 1 1
        '''
        self.data_regs[args[2]] = self.data_regs[args[0]] - self.data_regs[args[1]]

    def loadProgramToMemory(self) -> (None):
        '''Attempts to read ./program.txt and loads program into memory whereby program.txt is a list of
        line-separated instructions'''
        programfile = open('program.txt', 'r')
        line_num = 0
        while True:
            line = programfile.readline()
            if not line:
                break
            self.memory[line_num] = line.strip().split(' ')
            line_num += 1
        programfile.close()
        '''TODO:
        * check registers/memory are in range?
        * check valid number of params for each instr
        * declutter (spaces, newline, punctuation etc)
        '''

    def execute(self) -> (None):
        '''Executes the program using the following logic:
        1) Retrieve instruction from memory address specified by Program Counter (pc)
        2) Increment program counter
        3) Decode instruction - fetch any required data from memory
        4) Execute and perform any modifications to PC, e.g, from JMP instruction
        We assume all instructions in memory are valid, but memory address may not be.'''
        while self.run:
            if self.pc in self.memory.keys():
                cur_instr = self.memory[self.pc]
                print(cur_instr)
                self.pc += 1
                instr = cur_instr[0]
                self.instrs[instr](list(map(int, cur_instr[1:]))) # cast addresses to integers from str.
            else:
                break
        print('### BEGIN STATUS REGISTERS ###')
        print(self.status_regs)
        print('### END STATUS REGISTERS ###\n')
        print('### BEGIN DATA REGISTERS ###')
        print(self.data_regs)
        print('### END DATA REGISTERS ###\n')
        print('### BEGIN MEMORY ###')
        print(self.memory)
        print('### END MEMORY ###\n')
        print('### BEING PC ###')
        print(self.pc)
        print('### END PC ###')

def main():
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.loadProgramToMemory()
    myRiscProcessor.execute()

if __name__ == '__main__':
    main()