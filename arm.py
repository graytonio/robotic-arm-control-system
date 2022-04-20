
from RpiMotorLib import RpiMotorLib
from typing import List, Tuple
import concurrent.futures

class Joint:
    def __init__(self, step_pin: int, dir_pin: int, pos_limit: int, neg_limit: int):
        self.motor = RpiMotorLib.A4988Nema(dir_pin, step_pin, (-1, -1, -1), "A4988")
        self.pos = 0
        self.pos_limit = pos_limit
        self.neg_limit = neg_limit
        
    def get_pos(self):
        return self.pos
    
    def stop(self):
        self.motor.motor_stop()
    
    def set_home(self):
        self.pos = 0

    def go(self, dir: bool, steps: int):
        # Software limits
        if dir and self.pos_limit is not None:
            steps = min(self.get_pos() + steps, self.pos_limit)
        elif not dir and self.neg_limit is not None:
            steps = max(self.get_pos() - steps, self.neg_limit)
        
        self.motor.motor_go(dir, "Full", steps, .01, False, .05)
        self.pos += steps if dir else -steps
        
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
            for action in range(actions):
                executor.submit(self.joints[action[0]], action[1], action[2])