# Author: William Ballico
# Date : 26 06 2022
# Program: To facilitate VGA display for low speed microcontrollers
# Notes: The basic plan here is to use the PIO to print out the VGA
#        use PIO to take in commands, and use the clock to check for
#        new command inputs over serial.
#        I also want to note the PIO likely can be running an HD display
#        but the command updates will be very slow, so although you can render
#        HD images, do not expect an equivalent image refresh rate.
#
#Notes on VGA output:
#        For VGA all we really care about are the R G B pins, and the HSync and VSync Pins.
#        Thats 5 pins, with the GPIO we can map a maximum of 5 IO pins with Set and Side Set (exactly the ammount we need).
#        It's worth noting that we are then basically restricted to 7 different colours effectively, but I dont really care for
#        this program because I don't require 64 bit colour or anything like that.
#
#        For the actual program recall this http://tinyvga.com/vga-timing/1280x1024@60Hz  or https://glenwing.github.io/docs/VESA-DMT-1.12.pdf
#        its effectively all you need to know, just write the state machine such that pixels are 
#        Outputted in accordance with the correct timings.
#        Previously I found setHsync -> BackPorch -> Draw -> Front Porch works well.
#        
#        I plan to use 1 StateMachine for Hync, 1 stateMachine for R G B and 1 stateMachine for UART command input
#        
from machine import Pin
import time
from rp2 import PIO, StateMachine, asm_pio

HSYNC_PIN = 5
VSYNC_PIN = 6
VIS_PIN = 3

from machine import Pin
import time
from rp2 import PIO, StateMachine, asm_pio
# for timing we just want to do a 800x600 @ 56Hz timing
# this means each line should run at about 28.44us
# the RP2040 has a max speed of ~125MHz, and so we shoudld be able to fix in about 3500 cycles per pixel
# this is great because the PIO only allows for 32 max instructions anyway, so we can really get the timing quite close to perfect.
@asm_pio(set_init=(rp2.PIO.OUT_LOW,), out_shiftdir=PIO.SHIFT_RIGHT)
# For HSync
# Visible Area = 800 Pixels = 22.222us
# Front Porch = 24 Pixels = 0.66666us
# Sync Pulse = 72 Pixels = 2us
# Back Porch = 128 Pixels = 28.44us
# All up its 1024 Pixels, so Hsync should run at 35156.25Hz = 0.028ms
def HsyncLine():
    wrap_target()
    wait(1, irq, 6) # wait until flag is set to zero before running
    #Sync pulse for 72 pixels
    set(pins, 1)
    set(pins, 0)
    nop() [5]
    #BACK PORCH for 128 Pixels -> Do nothing for 666ns
    nop() [15]
    # VISIBLE AREA for 800 Pixels -> set IRQ to allow writing video for 22.2us and then clear
    irq(5)
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [2]
    # FRONT PORCH For 24 Pixels -> do nothing for a bit
    nop() [2]
    wrap
@asm_pio(set_init=(rp2.PIO.OUT_LOW,), out_shiftdir=PIO.SHIFT_RIGHT)
def VsyncLine():
    wrap_target()
    #Sync pulse for 2 lines
    set(pins, 1)
    nop()
    set(pins, 0)
    #BACK PORCH for 22 lines
    nop() [21]
    # VISIBLE AREA for 600 Lines
    irq(6)
    nop() [30]
    
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    # FRONT PORCH For 1 Line -> do nothing for a bit
    nop() # 697 ops = 17.777ms
    wrap
@asm_pio(set_init=(rp2.PIO.OUT_LOW,), out_shiftdir=PIO.SHIFT_RIGHT)
def VisualLine():
    wrap_target()
    wait(1, irq, 5) # wait until flag is set to zero before running
    set(pins, 1) # set colours on and dothis for 800 pixels
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [1]# 100 ops = 22.222us
    wrap    
#Hsynx 1 Pixel = 36.0MHz, we can go at 8 pixels at a time and so we run at 36.0MHz/8;
#Vsync 1 line = 1024*Pixels = 35156.25 Hz
Vsync_sm = StateMachine(5, VsyncLine,  freq = 39223, out_base=Pin(VIS_PIN))
Visual_sm = StateMachine(2, VisualLine,  freq = (45)*(10**5), out_base=Pin(VSYNC_PIN))
Hsync_sm = StateMachine(0, HsyncLine,  freq = (45)*(10**5), out_base=Pin(HSYNC_PIN))
Vsync_sm.active(1)
Hsync_sm.active(1)
Visual_sm.active(1)

LED = Pin(25, Pin.OUT)
while True:
    LED.value(1)
    time.sleep(0.1)
    LED.value(0)
    time.sleep(0.1)