import pygame
import random

def i00E0 (state, dState):
    state['display'].fill(0)
    dState['screen'].fill(dState['black'])
    pygame.display.flip()


def i00EE (state):
    state['PC'] = state['stack'].pop()


def i1NNN (state, l3):
    state['PC'] = l3


def i2NNN (state, l3):
    state['stack'].append(state['PC'])
    state['PC'] = l3


def i3XNN (state, n2, l2):
    if state['V'][n2] == l2:
        state['PC'] += 2


def i4XNN (state, n2, l2):
    if state['V'][n2] != l2:
        state['PC'] += 2


def i5XY0 (state, n2, n3):
    if state['V'][n2] == state['V'][n3]:
        state['PC'] += 2


def i6XNN (state, n2, l2):
    state['V'][n2] = l2


def i7XNN (state, n2, l2):
    state['V'][n2] = (state['V'][n2] + l2) & 0xFF


def i8XY0 (state, n2, n3):
    state['V'][n2] = state['V'][n3]

  
def i8XY1 (state, n2, n3):
    state['V'][n2] = (state['V'][n2] | state['V'][n3])


def i8XY2 (state, n2, n3):
    state['V'][n2] = (state['V'][n2] & state['V'][n3])


def i8XY3 (state, n2, n3):
    state['V'][n2] = (state['V'][n2] ^ state['V'][n3])


def i8XY4 (state, n2, n3):
    if state['V'][n2] + state['V'][n3] > 255:
        state['V'][0xF] = 1
    else:
        state['V'][0xF] = 0
    state['V'][n2] = (state['V'][n2] + state['V'][n3]) & 0xFF


def i8XY5 (state, n2, n3):
    if state['V'][n2] > state['V'][n3]:
        state['V'][0xF] = 1
    else:
        state['V'][0xF] = 0
    state['V'][n2] = (state['V'][n2] - state['V'][n3]) & 0xFF


def i8XY6 (state, n2, n3):
    state['V'][0xF] = state['V'][n2] & 0x1
    state['V'][n2] >>= 1


def i8XY7 (state, n2, n3):
    if state['V'][n3] > state['V'][n2]:
        state['V'][0xF] = 1
    else:
        state['V'][0xF] = 0
    state['V'][n2] = (state['V'][n3] - state['V'][n2]) & 0xFF


def i8XYE (state, n2):
    state['V'][0xF] = (state['V'][n2] & 0x80) >> 7
    state['V'][n2] = (state['V'][n2] << 1) & 0xFF


def i9XY0 (state, n2, n3):
    if state['V'][n2] != state['V'][n3]:
        state['PC'] += 2


def iANNN (state, l3):
    state['I'] = l3


def iBNNN (state, l3):
    state['PC'] = state['V'][0x0] + l3


def iCXNN (state, n2, l2):
    rVal = random.randint(0, 256)
    state['V'][n2] = rVal & l2


def iDXYN (state, dState, n2, n3, n4):
    
    tempX = n2
    tempY = n3

    x = state['V'][tempX]%64
    y = state['V'][tempY]%32
    n = n4

    state['V'][0xF] = 0

    for i in range(n):

        sprite = state['mem'][state['I']+i]

        if type(sprite) == str:
            sprite = sprite[2:]
            sprite = int(sprite, 16)
        
        sprite = bin(sprite)[2:].zfill(8)

        for j in range(len(sprite)):
            if sprite[j] == '1':

                if x+j < 64 and y+1 < 32:
                    if state['display'][y+i][x+j] == 1:
                        state['display'][y+i][x+j] = 0
                        state['V'][0xF] = 1
                    
                    else:
                        state['display'][y+i][x+j] = 1
        
    for i in range(64):
        for j in range(32):
            color = dState['white'] if state['display'][j][i] == 1 else dState['black']
            pygame.draw.rect(dState['screen'], color, (i * dState['scale'], j * dState['scale'], dState['scale'], dState['scale']))

    pygame.display.flip()


def iEX9E (state, hexKey, n2):
    keys = pygame.key.get_pressed()
    if keys[hexKey[state['V'][n2]]]:
        state['PC'] += 2


def iEXA1 (state, hexKey, n2):
    keys = pygame.key.get_pressed()
    if not (keys[hexKey[state['V'][n2]]]):
        state['PC'] += 2


def iFX07 (state, n2):
    state['V'][n2] = state['delay timer']


def iFX0A (state, hexKey, n2):
    pressed = False
    keys = pygame.key.get_pressed()
    temp = None

    for i in hexKey:
        if keys[hexKey[i]]:
            temp = hexKey[i]
            break
    newKeys = pygame.key.get_pressed()
    
    if keys[temp] and (not newKeys[temp]):
        pressed = True
        state['V'][n2] = keys[hexKey[i]]

    if not pressed:
        state['PC'] -= 2


def iFX15 (state, n2):
    state['delay timer'] = n2


def iFX18 (state, n2):
    state['sound timer'] = n2


def iFX1E (state, n2):
    state['I'] += state['V'][n2]


def iFX29 (state, fontLocation, n2):
    state['I'] = fontLocation[state['V'][n2]]


def iFX33 (state, n2):
    bcd = state['V'][n2]
    for i in range(2, -1, -1):
        state['mem'][state['I'] + i] = bcd % 10
        bcd //= 10


def iFX55 (state, n2):
    s = 0
    while s <= n2:
        loc = state['I'] + s
        state['mem'][loc] = state['V'][s]
        s +=1
    
    print(n2)
    print(type(n2))


def iFX65 (state, n2):
    l = 0
    while l <= n2:
        state['V'][l] = state['mem'][state['I']+1]
        l += 1