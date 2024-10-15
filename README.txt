This is my CHIP8 emulator that I created in python

Must have Python and PyGame installed in order to run

.ch8 files:

ibm.ch8 -> displays the IBM logo, test file to check if the display instruction (DXYN) has been implemented correctly

opcodeTest.ch8 -> displays an OK or NO next to the 1st half of the corresponding instruction. Meant to test specific instructions

key.ch8 -> meant to test keyboard inputs. Select one of the 3 tests by pressing 1, 2, or 3 on your keyboard

Pong.ch8 -> OG pong. Recommended tick rate is 500-800, can be changed at the bottom of CHIP8.py: dt = clock.tick(60) on line 437

spaceInvaders.ch8 -> very rough space invaders. runs very slowly on my emulator.

tetris.ch8 -> normal tetris. recommended rick rate is anything between 60 and 100. works fine aside from a temporary halting of the program whenever the block is rotated or moved left/right because of the way i implemented the instruction

HOW TO RUN CH8 FILES:
run the .py file and a window will pop up asking you to choose a file. Select whichever .ch8 file you want