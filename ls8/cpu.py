"""CPU functionality."""

import sys

program = []


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # creates ram with 256 bytes of memory
        self.pc = 0  # our counter
        self.reg = [0] * 8  # general registry with 8 slots
        self.fl = 0b00000000 
        # instruction code link with shorter name for development sake
        self.instructions = {"LDI": 0b10000010,
                             "HLT": 0b00000001,
                             "PRN": 0b01000111,
                             "MUL": 0b10100010,
                             "ADD": 0b10100000,
                             "SUB": 0b10100001,
                             "POP": 0b01000110,
                             "PUSH": 0b01000101,
                             "CALL": 0b01010000,
                             "RET": 0b00010001,
                             "DIV": 0b10100011,
                            #  sc
                             "JMP": 0b01010100,
                             "CMP": 0b10100111,
                             "JEQ": 0b01010101,
                             "JNE": 0b01010110
                             }  # instruction code link with short name for development sake
        self.SP = 7
        self.reg[7] = 0xf4

    def ram_read(self, ma):
        # ma = Memory Access
        return self.ram[ma]

    def ram_write(self, ma, v):
        # v = value
        self.ram[ma] = v

    def load(self, fileName):
        """Load a program into memory."""
        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        if len(sys.argv) > 1:
            # print(sys.argv)
            program_file = sys.argv[1]
            with open(program_file) as f:
                for line in f:
                    line = line.split('#')
                    line = line[0].strip()
                    if line == '':
                        continue
                    line = int(line, 2)
                    program.append(line)
                # print(program)
        # else:
        #     return

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
            self.pc += 3
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3
    # sc
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000000
            self.pc += 3

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir == self.instructions["HLT"]:
                running = False
                self.pc += 1

            elif ir == self.instructions["LDI"]:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif ir == self.instructions["PRN"]:
                print(self.reg[operand_a])
                self.pc += 2

            elif ir == self.instructions["MUL"]:
                self.alu("MUL", operand_a, operand_b)

            elif ir == self.instructions["ADD"]:
                self.alu("ADD", operand_a, operand_b)

            elif ir == self.instructions["SUB"]:
                self.alu("SUB", operand_a, operand_b)
                
            elif ir == self.instructions["PUSH"]:
                # decrement the stack pointer
                self.reg[self.SP] -= 1
                # copy the value from register into memory
                reg_num = self.ram[self.pc+1]
                value = self.reg[reg_num]  # this is what should be pushed
                address = self.reg[self.SP]
                # store the value on the stack
                self.ram[address] = value
                self.pc += 2
            elif ir == self.instructions["POP"]:
                # copy the value from the address pointed to by 'SP', to the given register
                value = self.ram_read(self.reg[self.SP])
                self.reg[operand_a] = value
                # increment the stack pointer
                self.reg[self.SP] += 1
                self.pc += 2 
            elif ir == self.instructions["CALL"]:
                # set return address
                # decrement stack pointer
                ret_add = self.pc + 2
                self.reg[self.SP] -= 1
                self.ram[self.reg[self.SP]] = ret_add
                # set pc to the value stored in the provided register
                reg_num = self.ram[self.pc + 1]
                dest_add = self.reg[reg_num]

                self.pc = dest_add
            elif ir == self.instructions["RET"]:
                # pop the return address from the top of the stack
                # then set the pc
                ret_add = self.ram[self.reg[self.SP]]
                self.reg[self.SP] += 1

                self.pc = ret_add  
                
            elif ir == self.instructions["CMP"]:
                 self.alu("CMP", operand_a, operand_b)
            elif ir == self.instructions["JMP"]:
                self.pc = self.reg[operand_a]
            elif ir == self.instructions["JEQ"]:
                if self.fl == 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif ir == self.instructions["JNE"]:
                if self.fl & 0b00000001 == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2  
            
            else:
                print(f"Instruction")
                running = False
