#!/usr/bin/env python

from subprocess import call
from arm import Arm, Joint
import RPi.GPIO as GPIO

estop_pin = 22
step_pins = (27, 24, 9, 6, 21, 7, 18)
dir_pins = (17, 23, 10, 5, 20, 8, 22)

hand_motor_0 = Joint(step_pin=step_pins[0], dir_pin=dir_pins[0])
hand_motor_1 = Joint(step_pin=step_pins[1], dir_pin=dir_pins[1])

joints = [hand_motor_0, hand_motor_1]

arm = Arm(joints)

def estop_handler(channel):
    print("ESTOP HIT")
    arm.stop()

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(estop_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(estop_pin, GPIO.RISING, callback=estop_handler)
    
    movement = [(0, False, 400), (1, False, 400)]
    arm.concurrent_movement(movement)
    
    GPIO.cleanup()

if __name__ == "__main__":
    main()
