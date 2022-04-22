#!/usr/bin/env python

from subprocess import call
from arm import Arm, Joint
import RPi.GPIO as GPIO

# Define Pin Assignments
step_pins = (27, 24)
dir_pins = (17, 23)

# Define Hand Limits (Assumes Home is in fully open position)
hand_neg_limit = 0
hand_pos_limit = 1000

# Define helpful constants for directing motion
HAND_DIR_DOWN = True
HAND_DIR_UP = False

# Define "Joint" objects to control individual motors
hand_motor_0 = Joint(step_pin=step_pins[0], dir_pin=dir_pins[0], pos_limit=hand_pos_limit, neg_limit=0)
hand_motor_1 = Joint(step_pin=step_pins[1], dir_pin=dir_pins[1], pos_limit=hand_pos_limit, neg_limit=0)
joints = [hand_motor_0, hand_motor_1]

# Define "Arm" object to allow for synchronous movement
arm = Arm(joints)

def main():
    
    # Setup movement of two motors moving in sync down to lower limit and back
    arm.concurrent_movement([(0, HAND_DIR_DOWN, hand_pos_limit, 5), (1, HAND_DIR_DOWN, hand_pos_limit, 5)])
    arm.concurrent_movement([(0, HAND_DIR_UP, hand_pos_limit, 5), (1, HAND_DIR_UP, hand_pos_limit, 5)])
    
    # Required for GPIO usage
    GPIO.cleanup()

if __name__ == "__main__":
    main()
