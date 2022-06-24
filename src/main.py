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
from rp2 import PIO, StateMachine, asm_pio

BASE_PIN = 4
PULL_THRESHHOLD = 16
PIN_NUM = 5

@asm_pio(out_init=(rp2.PIO.OUT_LOW,) * PIN_NUM, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh= PULL_THRESHHOLD)
def VGA_Program
    SET PINDIRS, 1
    line = line+1;
    start:
    
    setHsync:
        JMP start
    BackPorch:
        JMP start
    Draw:
        JMP start
    Front Porch:
        JMP start

Hsync_sm = StateMachine(0, VGA_Program,  freq = 108*1e6, out_base=PIN(BASE_PIN))
Hsync_sm.active(1)
# MAIN STUFF HERE
while True:
    #just loop forever for now
