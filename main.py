import os
from collections import namedtuple

AppStruct = namedtuple('AppStruct', "Value Length Address")
# define OPTAB
OPERATIONTABEL = {  # mnemonic : opcode
    "ADD": "18", "ADDF": "58", "ADDR": "90", "AND": "40", "CLEAR": "B4",
    "COMP": "28", "COMPF": "88", "COMPR": "A0", "DIV": "24", "DIVF": "64",
    "DIVR": "9C", "FIX": "C4", "FLOAT": "C0", "HIO": "F4", "J": "3C", "JEQ": "30",
    "JGT": "34", "JLT": "38", "JSUB": "48", "LDA": "00", "LDB": "68", "LDCH": "50", "LDF": "70",
    "LDL": "08", "LDS": "6C", "LDT": "74", "LDX": "04", "LPS": "D0", "MUL": "20", "MULF": "60", "MULR": "98",
    "STL": "14", "STS": "7C", "STSW": "E8", "STT": "84", "STX": "10", "SUB": "1C", "SUBF": "5C",
    "SUBR": "94", "SVC": "B0", "TD": "E0", "TIO": "F8", "TIX": "2C", "TIXR": "B8", "WD": "DC",
    "NORM": "C8", "OR": "44", "RD": "D8", "RMO": "AC", "RSUB": "4C", "SHIFTL": "A4", "SHIFTR": "A8",
    "SIO": "F0", "SSK": "EC", "STA": "0C", "STB": "78", "STCH": "54", "STF": "80", "STI": "D4"
}
# define the directives
DIRECTIVES = ['START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE']

ErrFlag = False
try:
    inputFile = open("sic.txt", "r")  # read sic file
except:
    print("The file: " + " does not exist, please check the name correctly.")
    ErrFlag = True
outputFile = open("intermediate.mdt", "w")  # create output file
listFile = open("list.txt", "w")  # write to list file
objectFile = open("obj.txt", "w")  # write to object file

while ErrFlag:
    break

Lines = inputFile.readlines()  # read the input file line by line
# define each column as a list
LOCCOUNTER = list()
LABEL = list()
OPCODE = list()
OPERAND = list()
LITERAL = {}  # {key, value}
SYMBOL = {}
ERRORS = []
jump = False
noOfLiterals = 0
index = 0
LOCATION = int("0000", base=16)
progName = Lines[0][0:9].strip()
first_line = Lines[0]
byteLen = 0
isJump = False
isLiteral = False
isIndexed = False
objText = ""
listText = ""
ObjectCodesArray = []
LocctrArray = []

if first_line[11:19].strip() == 'START':
    LOCATION = int(first_line[21:38].strip(), base=16)
    # add first line to intermediateFile
    baseLoc = LOCATION
    LOCCOUNTER.append(hex(baseLoc))
    LABEL.append(first_line[0:9])
    OPCODE.append(first_line[11:19])
    OPERAND.append(first_line[21:38].strip())
else:
    LOCATION = int("0000", base=16)
    baseLoc = LOCATION

start_location = baseLoc

for lineIndex, line in enumerate(Lines):
    tempLocCtr = baseLoc
    if lineIndex == 0: continue

    if line.strip()[0] != '.':
        _LABEL = line[0:9].strip()
        _OPCODE = line[11:19].strip()
        _OPERAND = line[21:38].strip()

        if _LABEL != '':
            if _LABEL in SYMBOL:
                ERRORS.append('ERROR-Line:' + str(lineIndex) + ' : duplicate symbol')
                ErrFlag = True
            elif (_LABEL != ''):
                # insert {LABEL,baseLoc} into SYMTAB
                SYMBOL[_LABEL] = baseLoc

        # search OPTAB for opcode
        if (_OPCODE in OPERATIONTABEL):
            baseLoc = baseLoc + 3
        elif (_OPCODE == 'WORD'):
            baseLoc += 3
        elif (_OPCODE == 'RESW') and (_OPERAND != ''):
            baseLoc += 3 * int(_OPERAND)
        elif (_OPCODE == 'RESB') and (_OPERAND != ''):
            baseLoc += int(_OPERAND)
        elif (_OPCODE == 'BYTE'):
            if (_OPERAND[0] == 'C'):
                # -3 ==> to ignore the three characters ==> (C'')
                byteLen = len(_OPERAND) - 3
                baseLoc += byteLen
            elif _OPERAND[0] == 'X':
                byteLen = (int((len(_OPERAND) - 3) / 2))  # it will increase one byte to the baseLoc
                baseLoc += byteLen
                # LTORG && END Processing
        elif (_OPCODE == 'LTORG' or _OPCODE == 'END'):
            LABEL.append(_LABEL)
            OPCODE.append(_OPCODE)
            OPERAND.append(_OPERAND)
            LOCCOUNTER.append("      ")
            displacement = 0
            totalDisplacement = 0
            for _literal in LITERAL:

                if (LITERAL[_literal].Address == '0000'):
                    LITERAL[_literal] = AppStruct(LITERAL[_literal].Value, LITERAL[_literal].Length,
                                                  hex(tempLocCtr + displacement))

                    LABEL.append("")
                    OPCODE.append("")
                    OPERAND.append(_literal)
                    LOCCOUNTER.append(str(hex(tempLocCtr + displacement)))
                    displacement += int(LITERAL[_literal].Length)
                    totalDisplacement += displacement
                    baseLoc += displacement
        else:
            ERRORS.append('ERROR at line ' + str(lineIndex) + ': invalid operation code : ' + _OPCODE)
            errorFlag = True

        if (_OPERAND != ''):
            # =C'-----' literal
            if (_OPERAND[0:2] == '=C'):

                name = _OPERAND
                value = ''
                for char in _OPERAND[3:len(_OPERAND) - 1]:
                    asc = hex(ord(char))  # ASCII value
                    value = value + str(asc[2:])
                # -4 is to ignore the four characters ==> (=C'')
                length = len(_OPERAND) - 4
                newLiteral = AppStruct(value, length, '0000')
                LITERAL[name] = newLiteral



            elif (_OPERAND[0:2] == '=X'):

                name = _OPERAND
                value = _OPERAND[3:len(_OPERAND) - 1]
                length = 1
                newLiteral = AppStruct(value, length, '0000')
                LITERAL[name] = newLiteral
                # LOCCTR += length

                # write line to intermediate readFile, remove comment

        if (_OPCODE != 'LTORG' and _OPCODE != 'END'):  # END,LTORG lines have been written above
            LOCCOUNTER.append(hex(tempLocCtr))
            LABEL.append(_LABEL)
            OPCODE.append(_OPCODE)
            OPERAND.append(_OPERAND)

ProgramLength = baseLoc - start_location - 1 + 1
print("\nProgram Name: " + str(progName) + "\n" + "Program Length: " + str(hex(ProgramLength)[2:]).upper() + " H\n")
print('\n\n         SYMTAB')
print('_________________________\n|  LABEL   |  LOCATION  |\n|-----------------------|')
for lineNumber, Label in enumerate(SYMBOL):
    print("|  " + Label.ljust(7) + " |   " + str(hex(SYMBOL[Label])).upper()[2:] + ' H   |')
print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n\n')

listLength = len(LOCCOUNTER)
for item in range(listLength):
    ll = str(LOCCOUNTER[item].upper()[2:]) + "   " + str(LABEL[item].ljust(10)) + "   " + str(
        OPCODE[item].ljust(10)) + "   " + str(OPERAND[item].ljust(10)) + "\n"
    outputFile.write(str(ll))

outputFile.close()

# ********************************************************************************************************************
# Pass 2
intermediateFile = open("intermediate.mdt", "r")
contents = intermediateFile.readlines()

objText = "H^" + progName.ljust(6) + "^" + str(hex(start_location))[2:].zfill(6) + "^" + hex(ProgramLength)[2:].zfill(
    6).upper() + "\n"  # +

objectCode = ""
for lineNumber, line in enumerate(contents):
    opcode1 = line[20:32].strip()
    label1 = line[7:19].strip()
    operand1 = line[33:].strip()
    location1 = line[0:4].strip()

    if (isJump and (opcode1 != 'RESW' and opcode1 != 'RESB')):
        # this means that the jump has reached its end
        isJump = False
        ObjectCodesArray.append('JumpEndsAt' + location1)  # (special jump item)
        LocctrArray.append('JumpHere')
    if (opcode1 == ''):
        objectCode = str(LITERAL[operand1][0])
    elif opcode1 in OPERATIONTABEL:
        _Opcode = OPERATIONTABEL[opcode1]

        if (operand1 == ''):
            operandValue = "0000"
        elif (operand1 in SYMBOL):
            operandValue = str(hex(SYMBOL[operand1])[2:])
        elif (operand1 in LITERAL):
            isLiteral = True
            operandValue = LITERAL[operand1][2][2:]
        elif (operand1[len(operand1) - 2:] == ',X'):
            isIndexed = True
            oplen = len(operand1) - 2
            tempOperand = operand1[:oplen]
            if (tempOperand in SYMBOL):
                modifiedOperand = int(hex(SYMBOL[tempOperand]), base=16)
                # since it is in indexed format
                # when we set the value of x (in the operand) to become 1,
                # we actually add 8 to the first byte (1000 0000 0000 0000)
                # so we add 8000 (in hex) to the total number
                # 32768 decimal is equal to 8000 in hexadeciaml
                modifiedOperand += 32768
                operandValue = hex(modifiedOperand)[2:]


        else:  # error invalid operand
            ERRORS.append("ERROR-at Loc " + location1 + ": invalid operand: " + operand1)
        if (isLiteral or isIndexed):
            oop = str(_Opcode)
            objectCode = oop + str(operandValue).upper()
        else:
            objectCode = (_Opcode + operandValue.zfill(4)).upper()

    elif opcode1 == "RESW" or opcode1 == "RESB":
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        isJump = True  # begin or continue the current jump
        continue
    elif (opcode1 == "START"):
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "BYTE"):
        if (operand1[0] == 'X'):
            operandValue = operand1[2:len(operand1) - 1]
        elif (operand1[0] == 'C'):
            operandValue = ""
            # Calculate the value between the two parentheses C'---'
            for char in operand1[2:len(operand1) - 1]:
                asc = hex(ord(char))  # ASCII value
                operandValue = operandValue + str(asc[2:])  # to hex
                # print(operand_value)

        else:
            ERRORS.append("ERROR-at Loc " + location1 + ": the BYTE instruction should have either C or X")

        objectCode = operandValue
    elif (opcode1 == "WORD"):
        operandValue = hex(int(operand1))[2:]
        objectCode = operandValue.zfill(6)
    elif (opcode1 == "END"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "LTORG"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 in LITERAL):
        objectCode = str(LITERAL[opcode1][0])
    else:
        # error invalid instruction
        ERRORS.append("ERROR-at Loc " + location1 + ": invalid instruction: " + opcode1)

    ObjectCodesArray.append(objectCode)
    LocctrArray.append(location1)

    if (opcode1 in LITERAL):
        # line = line[:5] + "*" + line[6:] # adds a star at the start of the literal line (as in the textbook)
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"
    else:
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"

listFile.write(listText)

while (len(ObjectCodesArray) > 0):
    lineLength = 30
    newLine = "T^" + LocctrArray[0].zfill(6)
    # While there are Object codes remaining
    while (len(ObjectCodesArray) > 0 and len(ObjectCodesArray[0]) / 2 <= lineLength and ObjectCodesArray[0][
                                                                                        0:10] != "JumpEndsAt"):  # Check for Special jumps Items
        lineLength -= len(ObjectCodesArray[0]) / 2
        objCod = "^" + ObjectCodesArray.pop(0)
        LocctrArray.pop(0)
        newLine = newLine + objCod

    # Delete the Special List Item ("JumpEndsAtXXXX"),("Jumphere")
    if (len(ObjectCodesArray) > 0 and ObjectCodesArray[0][0:10] == "JumpEndsAt"):
        ObjectCodesArray.pop(0)
        LocctrArray.pop(0)
    # Jump
    newLine = newLine[0:9].upper() + "" + hex(int(30 - lineLength))[2:].zfill(2).upper() + newLine[8:]
    objText += newLine + "\n"

objText += "E^" + str(hex(start_location))[2:].zfill(6)
objectFile.write(objText)

listFile.close()
objectFile.close()

if len(ERRORS):
    for error in ERRORS:
        print(error)
    ERRORS.clear()