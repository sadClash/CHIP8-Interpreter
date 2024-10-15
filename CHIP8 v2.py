import pygame
import random
import os
import opcodes
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import winsound

# Initialize Tkinter Root
root = Tk()
root.withdraw()

#Pygame initialization
dState = {
    'scale' : 40,
    'screen' : None,
    'clock' : None,
    'running' : True,
    'white' : (255, 255, 255),
    'black' : (0, 0, 0),
    'dt' : 0
}
pygame.init()
dState['screen'] = pygame.display.set_mode((64*dState['scale'], 32*dState['scale']), pygame.RESIZABLE)
dState['clock'] = pygame.time.Clock()

# State Dictionary
state = {

    # Initialize sound
    'frequency' : 500,
    'duration' : 100,

    # Initialize display buffer
    'display' : np.zeros((32, 64)),

    # Initialize memory
    'mem' : [0]*4096,

    # Initialize Stack
    'stack' : [],

    # Initialize general, program counter, and index registers
    'V' : [0]*16,
    'PC' : 0x200,
    'I' : 0,

    # Initialize sound and delay timer
    'delay timer' : 0,
    'sound timer' : 0
}

# Initialize Fonts
fonts = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

# Load fonts into memory
i = 0
while i < len(fonts):
    state['mem'][0x050 + i] = hex(fonts[i])
    i+=1

# Initialize Dictionary for font addresses
fontLocation = {
    0x0 : 0x050,
    0x1 : 0x055,
    0x2 : 0x05A,
    0x3 : 0x05F,
    0x4 : 0x064,
    0x5 : 0x069,
    0x6 : 0x06E,
    0x7 : 0x073,
    0x8 : 0x078,
    0x9 : 0x07D,
    0xA : 0x082,
    0xB : 0x087,
    0xC : 0x08C,
    0xD : 0x091,
    0xE : 0x096,
    0xF : 0x09B
}

# Initialize hex digit to keyboard dictionary
hexKey = {
    1 : pygame.K_1,
    2 : pygame.K_2,
    3 : pygame.K_3,
    12 : pygame.K_4,
    4 : pygame.K_q,
    5 : pygame.K_w,
    6 : pygame.K_e,
    13 : pygame.K_r,
    7 : pygame.K_a,
    8 : pygame.K_s,
    9 : pygame.K_d,
    14 : pygame.K_f,
    10 : pygame.K_z,
    0 : pygame.K_x,
    11 : pygame.K_c,
    15 : pygame.K_v
}

# Open the ROM and store data in memory
filename = askopenfilename()
binary = open(filename, "rb").read()
i = 0
while i < len(binary):
    state['mem'][0x200 + i] = (binary[i])
    i+=1

# create main emulator loop

    # decode opcodes and run respective instruction
while dState['running']:
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dState['running'] = False

    # Pulls 2 bytes from memory and joins them to form the opcode
    h1 = state['mem'][state['PC']]
    h2 = state['mem'][state['PC'] + 1]
    opcode = (h1 << 8) | h2
    
    # Decoding
    n1 = (opcode & 0xF000) >> 12    # nibble 1
    n2 = (opcode & 0x0F00) >> 8     # nibble 2
    n3 = (opcode & 0x00F0) >> 4     # nibble 3
    n4 = (opcode & 0x000F)          # nibble 4
    l2 = (opcode & 0x00FF)          # lower 2 nibbles
    l3 = (opcode & 0x0FFF)          # lower 3 nibbles

    # Increment program counter by 2 to fetch next instruction
    state['PC'] +=2

    # Check if instruction starts with '00'

    match n1:
        case 0x0:
            match opcode:
                case 0x00E0:
                    opcodes.i00E0(state, dState) # 00E0 (clear screen)
                case 0x00EE:
                    opcodes.i00EE(state) # 00EE (return from subroutine, pop stack and set to PC)
                case _:
                    print("Unknown Opcode: " + opcode)
        case 0x1:
            opcodes.i1NNN(state, l3) # 1NNN (jump to address NNN, set PC to NNN)
        case 0x2:
            opcodes.i2NNN(state, l3) # 2NNN (call subroutine, first push PC to stack, then set PC to NNN)
        case 0x3:
            opcodes.i3XNN(state, n2, l2) # 3XNN (skip if V[X] == NN)
        case 0x4:
            opcodes.i4XNN(state, n2, l2) # 4XNN (skip if V[X] != NN)
        case 0x5:
            opcodes.i5XY0(state, n2, n3) # 5XY0 (Skip if V[X] == V[Y])
        case 0x6:
            opcodes.i6XNN(state, n2, l2) # 6XNN (set register V[X] to NN)
        case 0x7: 
            opcodes.i7XNN(state, n2, l2) # 7XNN (add NN to V[X])
        case 0x8:
            match n4:
                case 0x0:
                    opcodes.i8XY0(state, n2, n3) # 8XY0 (set V[X] to value of V[Y])
                case 0x1:
                    opcodes.i8XY1(state, n2, n3) # 8XY1 (bitwise OR of V[X] and V[Y] is stored in V[X])
                case 0x2:
                    opcodes.i8XY2(state, n2, n3) # 8XY2 (bitwise AND of V[X] and V[Y] is stored in V[X])
                case 0x3:
                    opcodes.i8XY3(state, n2, n3) # 8XY3 (bitwise XOR of V[X] and V[Y] is stored in V[X])
                case 0x4:
                    opcodes.i8XY4(state, n2, n3) # 8XY4 (Sum of V[X] and V[Y] is stored in V[X])
                case 0x5:
                    opcodes.i8XY5(state, n2, n3) # 8XY5 (Difference of V[X] - V[Y] is stored in V[X])
                case 0x6:
                    opcodes.i8XY6(state, n2, n3) # 8XY6 (Shift V[X] 1 bit to the right)
                case 0x6:
                    opcodes.i8XY7(state, n2, n3) # 8XY7 (Difference of V[Y] - V[X] is stored in V[X])
                case 0xE:
                    opcodes.i8XYE(state, n2) # 8XYE (Shift V[X] 1 bit to the left)
                case _:
                    print("Unknown Opcode: " + opcode)
        case 0x9:
            opcodes.i9XY0(state, n2, n3) # 9XY0 (Skip if V[X] != V[Y])
        case 0xA:
            opcodes.iANNN(state, l3) # ANNN (set register I to NNN)
        case 0xB:
            opcodes.iBNNN(state, l3) # BNNN (Jump with offset, PC = V[0x0] + NNN)
        case 0xC:
            opcodes.iCXNN(state, n2, l2) # CXNN (Perform bitwise AND with a random number from 0-255, AND it with NN and store it in V[X])
        case 0xD:
            opcodes.iDXYN(state, dState, n2, n3, n4) # DXYN (draw)
        case 0xE:
            match l2:
                case 0x9E:
                    opcodes.iEX9E(state, hexKey, n2) # EX9E (Skip/Increment PC by 2 if value in V[X] is pressed, does not wait for input)
                case 0xA1:
                    opcodes.iEXA1(state, hexKey, n2) # EXA1 (Skip/Increment PC by 2 if value in V[X] is not pressed, does not wait for input)
                case _:
                    print("Unknown Opcode: " + opcode)
        case 0xF:
            match l2:
                case 0x07:
                    opcodes.iFX07(state, n2) # FX07 (Set V[X] to current value of the delay timer)
                case 0x0A:
                    opcodes.iFX0A(state, hexKey, n2)  # FX0A (Wait for a key input, decrement PC while waiting, delay/sound timer should still be decreased no matter what)
                case 0x15:
                    opcodes.iFX15(state, n2) # FX15 (Set delay timer to value in V[X])
                case 0x18:
                    opcodes.iFX18(state, n2) # FX18 (Set sound timer to value in V[X]) 
                case 0x1E:
                    opcodes.iFX1E(state, n2) # FX1E (Increment index register 'I' by value in V[X])
                case 0x29:
                    opcodes.iFX29(state, fontLocation, n2) # FX29 (Set index register to address of hex character stored at V[X])
                case 0x33:
                    opcodes.iFX33(state, n2) # FX33 (BCD Conversion)
                case 0x55:
                    opcodes.iFX55(state, n2) # FX55 (Store)
                case 0x65:
                    opcodes.iFX65(state, n2) # FX65 (Load)
                case _:
                    print("Unknown Opcode: " + opcode)
        case _:
            print("Unknown Opcode: " + opcode)


    if state['sound timer'] > 0:
        state['sound timer'] -= 1
        #winsound.Beep(frequency, duration)
    if state['delay timer'] > 0:
        state['delay timer'] -= 1

    dState['dt'] = dState['clock'].tick(60)


pygame.quit()
#os.system('cls')