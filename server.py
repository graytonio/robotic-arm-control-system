#!/usr/bin/env python

# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from arm import Arm, Joint
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
import json

__author__ = 'graytonio'

step_pins = (27, 24)
dir_pins = (17, 23)

hand_neg_limit = 1100
hand_pos_limit = 0

hand_motor_0 = Joint(step_pin=step_pins[0], dir_pin=dir_pins[0], neg_limit=-hand_neg_limit, pos_limit=0, name="Hand Joint 1")
hand_motor_1 = Joint(step_pin=step_pins[1], dir_pin=dir_pins[1], neg_limit=-hand_neg_limit, pos_limit=0, name="Hand Joint 2")

joints = [hand_motor_0, hand_motor_1]
arm = Arm(joints)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True, cors_allowed_origins="*")

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def jointPositions():
    while not thread_stop_event.isSet():
        positions = []
        for joint in joints:
            positions.append({"name": joint.get_name(), "pos": joint.get_pos(), "pos_limit": joint.pos_limit, "neg_limit": joint.neg_limit, "id": joints.index(joint)})
            
        print(positions)
        
        socketio.emit('posupdate', {'positions': positions}, namespace='/test')
        socketio.sleep(2)

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(jointPositions)

@socketio.on('movement', namespace="/test")
def move_arm(json):
    print('message received:' + str(json))
    arm.move_joint(json["id"], json["dir"], json["steps"])

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
    
def main():
    socketio.run(app, host="0.0.0.0")

if __name__ == '__main__':
    main()