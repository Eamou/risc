# risc
Simple Python RISC processor

### Quickstart
To test the program, you may run ```test.py``` to run all tests and demonstrate that the machine is in a working state.

**By default**, the program looks for two text files called ```program.txt``` and ```inputfile.txt``` in the root folder (e.g, on the same level as ```main.py```).
To run your own program, you may simply create/modify these files. Alternatively, you can look inside the ```algos``` folder to see some pre-written examples.

If you wish to change the files' name/location etc, you can tell the program where to look for your files by modifying 
```main()``` in ```main.py``` - the arguments of ```parseInputData``` and ```loadProgramToMemory```
will be your input data file and program file respectively.

Please ensure the files have the file ending ```.txt```. The program file may also have the ```.bin``` ending if you wish to use the binary encoding of the processor.

### Processor Specification
We have implemented the following basic instructions:
- NOP - does nothing to the state of the machine
- HALT - stops the machine
- CMP - compares the contents of two registers/values, updates a status register if they are equal
- JMP - resets what the next instruction is, possibly dependent on the state of a status register
- LOAD - transfers contents of a memory location to a data register
- STORE - transfers contents of a data register to a memory location
- ADD - adds contents of two specified data registers/values and leaves result in a specified target data register
- SUB - subtracts contents of two specified data registers/values and leaves result in a specified target data register

The machine utilises data registers, status registers and memory to store and execute a program. We use a Program Counter to keep track of
which instruction we are currently executing - this may be considered to be a special purpose data register.

### Modifications / Design Changes
#### Functionality
We quickly identified a need for some instructions, namely arithmetic and comparison instructions, to have capability for accepting direct values
alongside register addresses - for example, ```ADD #0 #1 0``` would mean adding ```data_register[0] <- 0+1``` 
rather than ```data_register[0] <- data_register[0] + data_register[1]```. It is possible to specify direct values for ADD, SUB, CMP and MULT.

#### Additional Arithmetic and Logic Instructions
We have also implemented two additional instructions:
- MULT - multiply the value of two data registers/values and leaves result in a specified target data register
- CNE - compare the value of two data registers/values, updates a status register if they are not equal

#### Testing
We have implemented a test suite, that can be found in ```test.py```, that ensures the processor behaves as expected, given both valid and invalid programs & data.
This test suite was implemented using the Python library ```unittest```, as it allows us to assert Exception throws in our program, which is important for testing
how the processor handles invalid data.

The tests can be easily extended to cover any further programs that may be added - little bespoke code is needed for adding new test cases.

#### Cache
We have implemented a cache for the processor, specifically, a write-through cache that implements a Least Recently Used (LRU) replacement policy. We have set the capacity
for this cache to be an arbitrary value of 4, though this can be changed as desired by simply passing a value to the RISCProcessor class constructor.

To implement the LRU policy, we utilised the OrderedDict data structure. This is a Python dictionary that keeps track of the order in which items were inserted into
the dictionary. This allows us to easily keep track of which items have been used recently by moving them to the start of the dictionary whenever they are used, such that
the least used element is then always the last element in the dictionary. This allows us to implement our LRU policy in constant time, as every operation with OrderedDict
is O(1) thanks to its implementation over a Hash Map.

#### Time/Memory Cost Metric
For this metric, we have assigned a cost to each operation based on how many arithmetic/data-access operations it performs. We then sum the total of all of these
costs over the course of the execution of a program, and this number becomes our metric. This allows one to very easily see when they have optimised their program,
as the Complexity number will be lower if optimisations have been made.

This idea is inspired by the idea of clock cycles in low-level programming. Naturally, as the processor is in Python, there are many many more clock cycles at use
in performing any operations in our processor, but we feel this is a suitable analogue that provides useful feedback for the end user.

#### Linked List Proposal
To implement linked lists in our RISC processor, we propose the following scheme:
*   Each item in the list consists of two elements: the data, and the 'pointer'.
    For convenience we may store these two next in neighbouring contiguous register
    locations.

    Without loss of generality, we may say the first register contains the data, and
    the second the pointer. The traversal algorithm is as follows, being given the
    location of the first item to start:
    1) Read the data at the current register index
    2) Increment our register index by 1
    3) Read the data at the new register index and store as current register index
    4) Go to step 1), unless the new register index indicates the end of the list.

    Naturally, we can store the elements of the list anywhere in memory - list elements
    are not required to be in contiguous blocks of registers.
    In implementation, we should be careful to mind the end of memory where it may be possible
    to 'overrun', where the data is the last available memory element and we hence have
    nowhere to store our 'pointer'. We must similarly be careful when storing data next
    to existing pieces of memory.

### Improvements
We note that the function ```validateInstruction()``` is quite cumbersome to read, though not actually too complex in terms of the actual logic. To aid this, we propose
that we would implement an Instruction class, with subclasses for each particular instruction. From this, we can set up rules for instantiation of these subclasses such that the validation is largely 'outsourced' to the class, improving code readability.
