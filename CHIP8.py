import pygame
import random
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import winsound

# Initialize Tkinter Root
root = Tk()
root.withdraw()

# Pygame display initialization
pygame.init()
SCALE = 40
screen = pygame.display.set_mode((64*SCALE,32*SCALE), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
dt = 0

# Initialize Sound
frequency = 500
duration = 100

# Initialize memory
mem = [0]*4096

# Initialize display buffer
rows = 32
columns = 64
display = [[0 for i in range(columns)] for j in range(rows)]

# Create Stack
stack = []

# Initialize general, program counter, and index registers
V = [0]*16
PC = 0x200
I = 0

# Initialize Font and Load into Memory
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

i = 0
while i < len(fonts):
    mem[0x050 + i] = hex(fonts[i])
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

#Initialize sound and delay timer
delayTimer = 0
soundTimer = 0

# Open the ROM and store data in memory

filename = askopenfilename()
binary = open(filename, "rb").read()
i = 0
while i < len(binary):
    mem[0x200+i] = (binary[i])
    i+=1


# create main emulator loop

    # decode opcodes and run respective instruction
while running:
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Pulls 2 bytes from memory and joins them to form the opcode
    nibble1 = mem[PC]
    nibble2 = mem[PC+1]
    opcode = (nibble1 << 8) | nibble2
    hopcode = format(opcode, '04x')

    # Increment program counter by 2 to fetch next instruction
    PC +=2
   
    # OPCODE DECODING #

    n1 = hopcode[0]         # 1st hex value         | A---
    n2 = hopcode[1]         # 2nd hex value         | -A--
    n3 = hopcode[2]         # 3rd hex value         | --A-
    n4 = hopcode[3]         # 4th hex value         | ---A
    byte1 = hopcode[:2]     # 1st 2 hex values      | AA--
    byte2 = hopcode[2:]     # Last 2 hex values     | --AA
    last3 = hopcode[1:]     # Last 3 hex values     | -AAA



    # Check if instruction starts with '00'
    if byte1 == "00":

        # 00E0 (clear screen)
        if byte2 == "e0":
            display = [[0 for i in range(columns)] for j in range(rows)]
            screen.fill(BLACK)
            pygame.display.flip()
        
        # 00EE (return from subroutine, pop stack and set to PC)
        elif byte2 == "ee":
            PC = stack.pop()


    # 1NNN (jump to address NNN, set PC to NNN)    
    elif n1 == '1':
        #print("Jump Instruction: " + hopcode)
        PC = int(last3,16)


    # 2NNN (call subroutine, first push PC to stack, then set PC to NNN)
    elif n1 == '2':
        stack.append(PC)
        PC = int(last3, 16)
    

    # 3XNN (skip if V[X] = NN)
    elif n1 == '3':
        temp = int(n2, 16)
        if V[temp] == int(byte2, 16):
            PC += 2

    
    # 4XNN (Skip if V[X] != NN)
    elif n1 == '4':
        temp = int(n2, 16)
        if V[temp] != int(byte2, 16):
            PC += 2


    # 5XY0 (Skip if V[X] = V[Y])
    elif n1 == '5':
        temp1 = int(n2, 16)
        temp2 = int(n3, 16)
        if V[temp1] == V[temp2]:
            PC += 2


    # 6XNN (set register V[X] to NN)
    elif n1 == '6':
        temp = int(n2, 16)
        V[temp] = int(byte2, 16)


    # 7XNN (add NN to V[X])
    elif n1 == '7':
        temp = int(n2, 16)
        V[temp] = (V[temp] + int(byte2, 16)) & 0xFF


    # Check if instruction starts with '8'
    elif n1 == '8':
        temp1 = int(n2, 16)
        temp2 = int(n3, 16)
        
        # 8XY0 (set V[X] to value of V[Y])
        if n4 == '0':
            V[temp1] = V[temp2]
        
        # 8XY1 (bitwise OR of V[X] and V[Y] is stored in V[X])
        if n4 == '1':
            V[temp1] = V[temp1] | V[temp2]
        
        # 8XY2 (bitwise AND of V[X] and V[Y] is stored in V[X])
        if n4 == '2':
            V[temp1] = V[temp1] & V[temp2]

        # 8XY3 (bitwise XOR of V[X] and V[Y] is stored in V[X])
        if n4 == '3':
            V[temp1] = V[temp1] ^ V[temp2]

        # 8XY4 (Sum of V[X] and V[Y] is stored in V[X])
        if n4 == '4':
            if V[temp1] + V[temp2] > 255:
                V[0xF] = 1
            else:
                V[0xF] = 0
            V[temp1] = (V[temp1] + V[temp2]) & 0xFF

        # 8XY5 (Difference of V[X] - V[Y] is stored in V[X])
        if n4 == '5':    
            if V[temp1] > V[temp2]:
                V[0xF] = 1
            else:
                V[0xF] = 0
            V[temp1] = (V[temp1] - V[temp2]) & 0xFF

        # 8XY6 (Shift V[X] 1 bit to the right)
        if n4 == '6':
            temp = int(n2, 16)
            V[0xF] = V[temp] & 0x1
            V[temp] >>= 1

        # 8XY7 (Difference of V[Y] - V[X] is stored in V[X])
        if n4 == '7':
            if V[temp2] > V[temp1]:
                V[0xF] = 1
            else:
                V[0xF] = 0
            V[temp1] = (V[temp2] - V[temp1]) & 0xFF
        
        # 8XYE (Shift V[X] 1 bit to the left)
        if n4 == 'e':
            temp = int(n2, 16)
            V[0xF] = (V[temp] & 0x80) >> 7
            V[temp] = (V[temp] << 1) & 0xFF


    # 9XY0 (Skip if V[X] != V[Y])
    elif n1 == '9':
        temp1 = int(n2, 16)
        temp2 = int(n3, 16)
        if V[temp1] != V[temp2]:
            PC += 2


    # ANNN (set register I to NNN)
    elif n1 == 'a':
        I = int(last3, 16)

    
    # BNNN (Jump with offset, PC = V[0x0] + NNN)
    elif n1 == 'b':
        PC = V[0x0] + int(last3, 16)


    # CXNN (Perform bitwise AND with a random number from 0-255 and store it in V[X])
    elif n1 == 'c':
        rVal = random.randint(0,256)
        temp = int(n2, 16)
        V[temp] = rVal & int(byte2, 16)


    # DXYN (draw)
    elif n1 == 'd':

        # Grab x and y registers from instruction
        tempX = int(n2, 16)
        tempY = int(n3, 16)

        # Initialize X/Y coordinate and N-Bytes
        x = V[tempX]%64
        y = V[tempY]%32
        n = int(n4, 16)

        # Set V[0xF] flag to 0
        V[0xF] = 0

        for i in range(n):
            
            sprite = mem[I+i]

            if type(sprite) == str:
                sprite = sprite[2:]
                sprite = int(sprite, 16)


            sprite = bin(sprite)[2:].zfill(8)
            

            for j in range(len(sprite)):
                if sprite[j] == '1':

                    if x+j < 64 and y+i < 32:
                        if display[y+i][x+j] == 1:
                            display[y+i][x+j] = 0
                            V[0xF] = 1
                            
                        else:
                            display[y+i][x+j] = 1
        
        for i in range(64):
            for j in range(32):
                color = WHITE if display[j][i] == 1 else BLACK
                pygame.draw.rect(screen, color, (i * SCALE, j * SCALE, SCALE, SCALE))

        pygame.display.flip()


    # Check if instruction starts with 'E'
    elif n1 == 'e':

        # EX9E (Skip/Increment PC by 2 if value in V[X] is pressed, does not wait for input)
        if byte2 == '9e':
            temp = int(n2, 16)
            keys = pygame.key.get_pressed()
            if keys[hexKey[V[temp]]]:
                PC += 2

        # EXA1 (Skip/Increment PC by 2 if value in V[X] is not pressed, does not wait for input)
        elif byte2 == 'a1':
            temp = int(n2, 16)
            keys = pygame.key.get_pressed()
            if not (keys[hexKey[V[temp]]]):
                PC += 2


    # Check if instruction starts with 'F'
    elif n1 == 'f':

        # FX07 (Set V[X] to current value of the delay timer)
        if byte2 == '07':
            temp = int(n2, 16)
            V[temp] = delayTimer
        
        # FX0A (Wait for a key input, decrement PC while waiting, delay/sound timer should still be decreased no matter what)
        elif byte2 == '0a':
            wait = True
            up = True
            temp = int(n2, 16)
            keys = pygame.key.get_pressed()
            for i in hexKey:
                if keys[hexKey[i]]:
                    V[temp] = i
                    #while up:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYUP:
                            if event.key == hexKey[i]:
                                wait = False
                                up = False
                    break
            if wait and up == True:
                PC -= 2

        # FX15 (Set delay timer to value in V[X])
        elif byte2 == '15':
            temp = int(n2, 16)
            delayTimer = V[temp]
        
        # FX18 (Set sound timer to value in V[X])
        elif byte2 == '18':
            temp = int(n2, 16)
            soundTimer = V[temp]

        # FX1E (Increment index register 'I' by value in V[X])
        elif byte2 == '1e':
            temp = int(n2, 16)
            I += V[temp]
        
        # FX29 (Set index register to address of hex character stored at V[X])
        elif byte2 == '29':
            temp = int(n2, 16)
            I = fontLocation[V[temp]]
        
        # FX33 (BCD Conversion)
        elif byte2 == '33':
            temp = int(n2, 16)
            bcd = V[temp]
            for i in range(2, -1, -1):
                mem[I + i] = bcd % 10
                bcd //= 10
        
        # FX55 (Store)
        elif byte2 == '55':
            s = 0
            while s <= int(n2, 16):
                mem[I+s] = V[s]
                s += 1
        
        elif byte2 == '65':
            l = 0
            while l <= int(n2, 16):
                V[l] = mem[I+l]
                l += 1


    if soundTimer > 0:
        soundTimer -= 1
        #winsound.Beep(frequency, duration)
    if delayTimer > 0:
        delayTimer -= 1

    dt = clock.tick(80)


pygame.quit()
os.system('cls')