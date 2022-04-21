from RpiMotorLib import RpiMotorLib
from typing import List, Tuple
import concurrent.futures
import RPi.GPIO as GPIO
import sys
import time

class StopMotorInterrupt(Exception):
    """ Stop the motor """
    pass

class Joint:
    def __init__(self, step_pin: int, dir_pin: int, pos_limit = None, neg_limit = None):
        # self.motor = RpiMotorLib.A4988Nema(dir_pin, step_pin, (-1, -1, -1), "A4988")
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.pos = 0
        self.pos_limit = pos_limit
        self.neg_limit = neg_limit
        self.stop_motor = False
            
    def get_pos(self):
        return self.pos
    
    def stop(self):
        self.stop_motor = True
    
    def set_home(self):
        self.pos = 0
        
    def step(self):
        GPIO.output(self.step_pin, True)
        time.sleep(0.005)
        GPIO.output(self.step_pin, False)
        time.sleep(0.005)

    def go(self, dir: bool, steps: int):
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.output(self.dir_pin, dir)
        
        try:
            time.sleep(0.05)
            for i in range(steps):
                
                if self.stop_motor:
                    raise StopMotorInterrupt
                else:
                    # self.step()
                    if dir and self.pos_limit is not None and self.pos + 1 <= self.pos_limit:
                        self.step()
                        self.pos += 1
                    elif not dir and self.neg_limit is not None and self.pos -1 >= self.neg_limit:
                        self.step()
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
            print("Movement Complete")
        
class Arm:
    def __init__(self, joints: List[Joint]):
        self.joints = joints
        
    def move_joint(self, joint_index, dir, steps):
        self.joints[joint_index].go(dir, steps)
        
    def get_joint_pos(self, joint_index):
        return self.joints[joint_index].get_pos()
    
    def set_home(self):
        for joint in range(self.joints):
            self.joints[joint].set_home()
            
    def stop(self):
        for joint in range(self.joints):
            self.joints[joint].stop()
    
    # Queue Up Concurrent Movements
    # Action format [( joint_index, direction, steps )]
    def concurrent_movement(self, actions: List[Tuple[int, bool, int]]):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for action in actions:
                print(action)
                executor.submit(self.joints[action[0]].go, action[1], action[2])
