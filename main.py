
class RISCProcessor:
    def __init__(self):
        self.data_regs = {}
        self.status_regs = {}
        self.memory = {}
        self.pc = 0

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

    def execute(self) -> (None):
        '''Executes the program using the following logic:
        1) Retrieve instruction from memory address specified by Program Counter (pc)
        2) Increment program counter
        3) Decode instruction - fetch any required data from memory
        4) Execute and perform any modifications to PC, e.g, from JMP instruction
        We assume all instructions in memory are valid, but memory address may not be.'''
        while True:
            cur_instr = self.memory[self.pc]
            self.pc += 1
            instr = cur_instr[0]
            break

def main():
    myRiscProcessor = RISCProcessor()
    myRiscProcessor.loadProgramToMemory()
    print(myRiscProcessor.memory)
    myRiscProcessor.execute()

if __name__ == '__main__':
    main()