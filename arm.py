from typing import List, Tuple
import concurrent.futures
import RPi.GPIO as GPIO
import sys
import time

def map(input, in_min, in_max, out_min, out_max):
    return (input - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class StopMotorInterrupt(Exception):
    """ Stop the motor """
    pass

class Joint:
    def __init__(self, step_pin: int, dir_pin: int, pos_limit = None, neg_limit = None, name = "Joint"):
        GPIO.setmode(GPIO.BCM)
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.pos = 0
        self.pos_limit = pos_limit
        self.neg_limit = neg_limit
        self.stop_motor = False
        self.name = name
            
    def get_pos(self):
        return self.pos
    
    def get_name(self):
        return self.name
    
    def stop(self):
        self.stop_motor = True
    
    def set_home(self):
        self.pos = 0
        
    def step(self, speed = 1):
        real_speed = map(speed, 1, 10, 0.001, 0.0005)
        GPIO.output(self.step_pin, True)
        time.sleep(real_speed)
        GPIO.output(self.step_pin, False)
        time.sleep(real_speed)

    def go(self, dir: bool, steps: int, speed = 1):
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.output(self.dir_pin, dir)
        
        try:
            time.sleep(0.05)
            for i in range(steps):
                
                if self.stop_motor:
                    raise StopMotorInterrupt
                else:
                    if dir and self.pos_limit is not None and self.pos + 1 <= self.pos_limit:
                        self.step(speed)
                        self.pos += 1
                    elif not dir and self.neg_limit is not None and self.pos -1 >= self.neg_limit:
                        self.step(speed)
                        self.pos -= 1
                    print("Step {}".format(i), end="\r", flush=True)
            
        except KeyboardInterrupt:
            print("User Keyboard Interrupt")
        except StopMotorInterrupt:
            print("E-Stop Interrupt")
        except Exception as motor_error:
            print(sys.exc_info()[0])
            print(motor_error)
            print("Unexpected Error")
        finally:
            GPIO.output(self.step_pin, False)
            GPIO.output(self.dir_pin, False)
            print("Movement Complete: {} steps".format(steps))
        
class Arm:
    def __init__(self, joints: List[Joint]):
        self.joints = joints
        
    def move_joint(self, joint_index, dir, steps, speed = 1):
        self.joints[joint_index].go(dir, steps, speed)
        
    def get_joint_pos(self, joint_index):
        return self.joints[joint_index].get_pos()
    
    def set_home(self):
        for joint in range(self.joints):
            self.joints[joint].set_home()
            
    def stop(self):
        for joint in range(self.joints):
            self.joints[joint].stop()
    
    # Queue Up Concurrent Movements
    # Action format [( joint_index, direction, steps, speed )]
    def concurrent_movement(self, actions: List[Tuple[int, bool, int]]):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for action in actions:
                executor.submit(self.joints[action[0]].go, action[1], action[2], action[3])
