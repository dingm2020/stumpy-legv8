import sys
import re
import os
import fileinput

arg1 = []  # <type 'list'>: [0, 0, 0, 0, 0, 1, 1, 10, 10, 0, 3, 4, 152, 4, 10, 1, 0, 112, 0]
arg2 = []  # <type 'list'>: [0, 1, 1, 0, 1, 0, 10, 3, 4, 5, 0, 5, 0, 5, 6, 1, 1, 0, 0]
arg3 = []  # <type 'list'>: [0, 10, 264, 0, 264, 48, 2, 172, 216, 260, 8, 6, 0, 6, 172, -1, 264, 0, 0]
arg1Str = []  # <type 'list'>: ['', '\tR1', '\tR1', '', '\tR1', '\tR1', '\tR10', '\tR3', '\tR4', .....]
arg2Str = []  # <type 'list'>: ['', ', R0', ', 264', '', ', 264', ', #48', ', R1', ', 172', ', 216', ...]'
arg3Str = []  # <type 'list'>: ['', ', #10', '(R0)', '', '(R0)', '', ', #2', '(R10)', '(R10)', '(R0)',...]
mem = []  # <type 'list'>: [-1, -2, -3, 1, 2, 3, 0, 0, 5, -5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
binMem = []  # <type 'list'>: ['11111111111111111111111111111111', '11111111111111111111111111111110', ...] opcode = []
opcode = []
opcodeStr = []
instructions = []
instrSpaced = []
registers = []
numInstr = 0
numData = 0

# masks
rnMask = 0x3e0  # 1st argument ARM Rn
rmMask = 0x1F0000  # second argument ARM Rm
rdMask = 0x1F  # destination ARM Rd
imMask = 0x3FFC00  # ARM I immediate
shmtMask = 0xFC00  # ARM shamt
addrMask = 0x1FF000  # ARM address for id and st
addr2Mask = 0xFFFFE0  # addr for CB format
imsftMask = 0x600000  # shift for IM formatw
imdataMask = 0x1FFFE0  # data for IM type

# input/output file paths
input = "input"
output = "NOTWORKING"

def binToSpacedR(s):
    spaced = s[0:11] + " " + s[11:16] + " " + s[16:22] + " " + s[22: 27]
    spaced += " " + s[27:32]
    return spaced


def binToSpacedD(s):
    spaced = s[0:11] + " " + s[11:20] + " " + s[20:22] + " " + s[22:27]
    spaced += " " + s[27:32]
    return spaced

def binToSpacedI(s):
    spaced = s[0:11] + " " + s[11: 22] + " " + s[22:27] + " " + s[27:32]
    return spaced

def binToSpacedB(s):
    return s[0:6] + " " + s[6:32]

def binToSpacedCB(s):
    return s[0:8] + " " + s[8:27] + " " + s[27: 32]

def binToSpacedIM(s):
    return s[ 0:9 ] + " " + s[ 9:11 ] + " " + s[ 11:27 ] + " " + s[ 27:32 ]

def binToSpacedBreak(s):
    return s[ 0:8 ] + " " + s[ 8:11 ] + " " + s[ 11:16 ] + " " + s[ 16:21 ] + " " + s[ 21:26 ] + " " + s[ 26:32 ]

def binToSpacedInt(s):
    return s[ 0:32 ]

def binToDecimalPos(s):

    flipped = s[::-1]
    value = 0
    i = 0

    #print 'bitstring: ' + s
    #print 'flipped: ' + flipped

    for char in flipped:
       # print 'value is: ' + str(value) + ' when i is: ' + str(i)
        if (char == '1'):
            value += 2**(i)
        i += 1

    return value

def binToDecimalNeg(s):

    s += '1'

    flipped = s[::-1]
    value = 0
    i = -1


    for char in flipped:
        if (char == '0'):
            value += 2**i
        i += 1

    value = -value - 1

    return value

def binToDecimal(s):
    if (s[0] == '1'):
        return binToDecimalNeg(s)
    else:
        return binToDecimalPos(s)


def parseInt(str):
    return int(re.sub('[^0-9]', '', str))


# project 1
class Disassembler:

    output = "NOTWORKING"

    global opcodeStr
    global arg1
    global arg2
    global arg3
    global arg1Str
    global arg2Str
    global arg3Str
    global mem
    global binMem
    global opcode
    global numInstr
    global numData

    def __init__(self):
        self.setup()
        self.disassemble()
        self.formatOutput()

# gets the arguments and read in input -> stores input in instructions
    def setup(self):
        global output
        global input
        # get file names
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                input = sys.argv[i + 1]
            if (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                output = sys.argv[i + 1]

        # open file for reading
        with open(input, 'r') as fin:
            for line in fin:
                instructions.append(line)

    def disassemble(self):
        i = -1
        j = -1
        broken = True

        for instr in instructions:

            i += 1

            mem.append(str(96 + (i * 4))) # memory location
            opcode.append(int(instr, base=2) >> 21)

            if( opcode[i] == 1112 ):  # if opcode = 1112 -> ADD
                opcodeStr.append("\tADD")        # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1624 ):           # SUB = 1624
                opcodeStr.append("\tSUB")        # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] >= 1160 and opcode[i] <= 1161 ):   # ADDI => 1160 - 1161
                opcodeStr.append("\tADDI")                     # I Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & imMask) >> 10)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimal(instr[10:22])))

                instrSpaced.append(binToSpacedI(instr))

            elif( opcode[i] >= 1672 and opcode[i] <= 1673 ): # SUBI => 1672 - 1673
                opcodeStr.append("\tSUBI")                     # I Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & imMask) >> 10)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimal(instr[10:22])))

                instrSpaced.append(binToSpacedI(instr))

            elif( opcode[i] == 1104 ): # AND => 1104
                opcodeStr.append("\tAND")  # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1360 ): # ORR => 1360
                opcodeStr.append("\tORR")  # R Format

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1872 ): # EOR => 1872
                opcodeStr.append("\tEOR")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)
                arg2.append((int(instr, base=2) & rmMask) >> 16)
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1690 ): # LSR => 1690
                opcodeStr.append("\tLSR")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # arg1 is R1
                arg2.append((int(instr, base=2) & shmtMask) >> 10)  # arg2 is shamt
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # arg3 is R0

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1691 ): # LSL => 1691
                opcodeStr.append("\tLSL")  # R TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # arg1 is R1
                arg2.append((int(instr, base=2) & shmtMask) >> 10)  # arg2 is shamt
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # arg3 is R0

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))

                instrSpaced.append(binToSpacedR(instr))

            elif( opcode[i] == 1984 ): # STUR => 1984
                opcodeStr.append("\tSTUR") # D TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # R2
                arg2.append((int(instr, base=2) & rmMask) >> 12)  # address
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # R1

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", [R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimal(instr[12:20])) + "]")

                instrSpaced.append(binToSpacedD(instr))

            elif( opcode[i] == 1986 ): # LDUR => 1986
                opcodeStr.append("\tLDUR") # D TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & rnMask) >> 5)  # R2
                arg2.append((int(instr, base=2) & rmMask) >> 16)  # address
                arg3.append((int(instr, base=2) & rdMask) >> 0)  # R1

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", [R" + str(arg1[i]))
                arg3Str.append(", #" + str(binToDecimal(instr[12:20])) + "]")

                instrSpaced.append(binToSpacedD(instr))

            elif( opcode[i] >= 160 and opcode[i] <= 191 ):  # B => 160 - 191
                opcodeStr.append("\tB") # B TYPE INSTRUCTION

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append("\t#" + str(binToDecimal(instr[6:32])))
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedB(instr))

            elif( opcode[i] >= 1440 and opcode[i] <= 1447 ):  # CBZ => 1440 - 1447
                opcodeStr.append("\tCBZ") # CB TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & addr2Mask) >> 5)
                arg2.append((int(instr, base=2) & rdMask) >> 0)
                arg3.append('')

                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(binToDecimal(instr[8:27])))
                arg3Str.append('')

                instrSpaced.append(binToSpacedCB(instr))

            elif( opcode[i] >= 1448 and opcode[i] <= 1455 ):  # CBNZ => 1448 - 1455
                opcodeStr.append("\tCBNZ") # CB TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & addr2Mask) >> 5)
                arg2.append((int(instr, base=2) & rdMask) >> 0)
                arg3.append('')

                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(binToDecimal(instr[8:27])))
                arg3Str.append('')

                instrSpaced.append(binToSpacedCB(instr))

            elif( opcode[i] >= 1684 and opcode[i] <= 1687 ):
                opcodeStr.append("\tMOVZ") # IM TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & imdataMask) >> 5)
                arg2.append(16*((int(instr, base=2) & imsftMask) >> 21))
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg1[i]))
                arg3Str.append(", LSL " + str(arg2[i]))

                instrSpaced.append(binToSpacedIM(instr))

            elif( opcode[i] >= 1940 and opcode[i] <= 1943 ):
                opcodeStr.append("\tMOVK") # IM TYPE INSTRUCTION

                arg1.append((int(instr, base=2) & imdataMask) >> 5)
                arg2.append(16*((int(instr, base=2) & imsftMask) >> 21))
                arg3.append((int(instr, base=2) & rdMask) >> 0)

                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg1[i]))
                arg3Str.append(", LSL " + str(arg2[i]))

                instrSpaced.append(binToSpacedIM(instr))

            elif( opcode[i] == 2038 ): # BREAK => 2038

                self.numInstr = i

                opcodeStr.append("\tBREAK")

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append('')
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedBreak(instr))

            elif (broken):
                j += 1
                binMem.append((int(instr, base=2) >> 31 ) & 0x1)

                opcodeStr.append("\t" + str(binToDecimal(instr)))

                arg1.append('')
                arg2.append('')
                arg3.append('')

                arg1Str.append('')
                arg2Str.append('')
                arg3Str.append('')

                instrSpaced.append(binToSpacedInt(instr))

        self.numInstr = i - j
        self.numData = j

    def formatOutput(self):
        with open(output, 'w') as myFile:
            i = 0
            for opcode in opcodeStr:
                writeData = instrSpaced[i] + "\t" + mem[i] + ' ' + opcode + arg1Str[i] + arg2Str[i] + arg3Str[i] + '\n'
                # print writeData
                myFile.write(writeData)
                i += 1

    def malloc(self, wordCount):
        for i in range(self.numInstr, wordCount):
            opcodeStr.append('0')

class Pipeline (Disassembler):
    global registers
    global numInstr
    registers = [0 for i in xrange(32)]

    def __init__(self):  # override init

        # disassemble
        Disassembler.__init__(self)  # super.init

        pc = 0
        i = 0

        # use PC to supply instruction address to instruction memory
        # use fetched register operands
            #to compute memory address (load or store)
            #to compute arithmetic (alu)
            #to compare to zero (branch)

        #if ALU
            #value written to register
        #if Load/Store
            #value from ALU result used as address

        #result form ALU or Memory is written back into register file


        with open(output, 'w') as myFile:
            while (True):  # loop for number of instructions
                i += 1
                writeData = ''

                writeData += '\n--------------------\n'
                writeData += 'cycle ' + str(i) + ': ' + str(mem[pc])
                writeData += '\t' + opcodeStr[pc]
                writeData += '   \t' + arg1Str[pc] + '\t' + arg2Str[pc].replace(',', '') + '\t' + arg3Str[pc].replace(
                    ',', '')

                if (opcode[pc] == 0):  # NO OP

                    a1 = arg1Str[pc]
                    a2 = arg1Str[pc]
                    a3 = arg1Str[pc]

                    registers[a1] = 0x0
                    registers[a2] = 0x0
                    registers[a3] = 0x0

                if (opcode[pc] == 1112):  # ADD

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = registers[a2] + registers[a3]

                elif (opcode[pc] == 1624):  # SUB

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = registers[a2] - registers[a3]

                elif (opcode[pc] >= 1160 and opcode[pc] <= 1161):  # ADDI

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    if (not '-' in arg3Str[pc]):
                        registers[a1] = registers[a2] + a3
                    else:
                        registers[a1] = registers[a2] - a3

                elif (opcode[pc] >= 1672 and opcode[pc] <= 1673):  # SUBI

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    if (not '-' in arg3Str[pc]):
                        registers[a1] = registers[a2] - a3
                    else:
                        registers[a1] = registers[a2] + a3

                elif (opcode[pc] == 1104):  # AND

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = a2 & a3


                elif (opcode[pc] == 1360):  # ORR

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = a2 | a3

                elif (opcode[pc] == 1872):  # EOR

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = a2 ^ a3

                elif (opcode[pc] == 1690):  # LSR

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = a2 >> a3

                elif (opcode[pc] == 1691):  # LSL

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])
                    a3 = parseInt(arg3Str[pc])

                    registers[a1] = a2 << a3


                elif (opcode[pc] >= 160 and opcode[pc] <= 191):  # B

                    a1 = parseInt(arg1Str[pc])
                    # print '\n' + "Arg1 = " + arg1Str[i] + ' when i = ' + str(i)
                    # test = "i went from " + str(pc) + " to "
                    if (not '-' in arg1Str[pc]):  # positive
                        pc += a1 - 1
                    else:
                        pc -= (a1 + 1)
                # print test + str(i)

                elif (opcode[pc] >= 1440 and opcode[pc] <= 1447):  # CBZ

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])

                    if (a1 == 0):
                        if (not '-' in arg2Str[pc]):  # positive
                            pc += a2 - 1
                        else:
                            pc -= (a2 + 1)

                elif (opcode[pc] >= 1448 and opcode[pc] <= 1455):  # CBNZ

                    a1 = parseInt(arg1Str[pc])
                    a2 = parseInt(arg2Str[pc])

                    if (a1 != 0):
                        if (not '-' in arg2Str[pc]):  # positive
                            pc += a2 - 1
                        else:
                            pc -= (a2 + 1)

                elif (opcode[pc] >= 1684 and opcode[pc] <= 1687):  # MOVZ

                    a1 = parseInt(arg1Str[pc])  # register
                    a2 = parseInt(arg2Str[pc])  # value
                    a3 = parseInt(arg3Str[pc])  # shift amount

                    registers[a1] = a2 << a3

                elif (opcode[pc] >= 1940 and opcode[pc] <= 1943):  # MOVK

                    a1 = parseInt(arg1Str[pc])  # register
                    a2 = parseInt(arg2Str[pc])  # value
                    a3 = parseInt(arg3Str[pc])  # shift amount

                    registers[a1] = registers[a1] | (a2 << a3)

                elif (opcode[pc] == 1984):  # STUR

                    a1 = parseInt(arg1Str[pc])  # register1
                    a2 = parseInt(arg2Str[pc])  # register2
                    a3 = parseInt(arg3Str[pc])  # value

                #### My way of trying to mimic allocating memory like what happens when data fills with 0s after he stores 200 in mem[360] for the example output ###
                # Does NOT work
                #       print '\n a3: ' + str(a3) + '\n\n'
                #
                #       last = mem[mem.count(mem)]
                #       print last
                #       for i in range(0, registers[registers[a2] + a3 - last]):
                #           mem.append(last + i    `* 4)

                elif (opcode[pc] == 1986):  # LDUR

                    a1 = parseInt(arg1Str[pc])  # register1
                    a2 = parseInt(arg2Str[pc])  # register2
                    a3 = parseInt(arg3Str[pc])  # value

                elif (opcode[pc] == 2038):  # BREAK
                    return

                # print registers (4x8)
                writeData += '\n\nRegisters:'
                index = 0
                for x in range(0, 4):
                    writeData += '\nr'
                    writeData += '' if x * 8 > 9 else '0'  # single digit numbers have a 0 in front
                    writeData += str(x * 8) + ':'
                    for y in range(0, 8):
                        writeData += '\t' + str(registers[index])
                        index += 1

                print writeData
                writeData += '\n\nData:'
                for x in range(0, self.numData):
                    if (x % 8 == 0):
                        writeData += '\n' + str(mem[self.numInstr + x]) + ":"  # new line
                    writeData += opcodeStr[self.numInstr + x]

                print writeData
                myFile.write(writeData)

                pc += 1

class state:
    global data

class combinational:
    global arg1
    global arg2

    def operate(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def wite(self, address):
        pass

class pc(state):
    #supply instruction address to instruction memory
    data = 96

class preIssueBuffer(state):
    data = [0,0,0,0]

class alu(combinational):

    def moveInstruction(self):
        # the instruction is moved from the pre-ALU buffer to the post-ALU buffer
        pass

class issueUnit(combinational):

    def issueInstruction(self):
        pass

#Write back unit
class WBU(combinational):
    #fetch contents of post-ALU and post-MEM
    #update register file
    pass




if __name__ == "__main__":
    sim = Pipeline()
