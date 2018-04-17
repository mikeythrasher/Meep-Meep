#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# meep-meep_motorcontrol.py
# Controls 2 DCMotors for directional control
# Modified by mikeythrasher
# 2018-04-09
#

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import subprocess
import sys

import aiy.assistant.auth_helpers
import aiy.audio
import aiy.voicehat
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

import RPi.GPIO as GPIO

from gpiozero import PWMOutputDevice

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)

motor1 = PWMOutputDevice(4)

motor2 = PWMOutputDevice(17)

motor3 = PWMOutputDevice(27)

motor4 = PWMOutputDevice(22)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

def forward_full():
    aiy.audio.say('Moving Forward. Full Speed')
    motor1.value = 1
    motor2.value = 1
    GPIO.output(26,False)
    GPIO.output(6,False)
    GPIO.output(13,True)

def right_turn():
    aiy.audio.say('Turning Right')
    motor1.value = 0.5
    motor2.value = 0
    GPIO.output(26,False)
    GPIO.output(6,True)
    GPIO.output(13,False)

def left_turn():
    aiy.audio.say('Turning Left')
    motor1.value = 0
    motor2.value = 0.5
    GPIO.output(26,False)
    GPIO.output(6,True)
    GPIO.output(13,False)

def back_up():
    aiy.audio.say('Backing up')
    motor3.value = 1
    motor4.value = 1
    GPIO.output(26,True)
    GPIO.output(6,False)
    GPIO.output(13,False)

def motor_off():
    aiy.audio.say('Stopping Now')
    motor1.value = 0
    motor2.value = 0
    motor3.value = 0
    motor4.value = 0
    GPIO.output(26,True)
    GPIO.output(6,False)
    GPIO.output(13,False)

def motor_on_half():
    aiy.audio.say('Moving Forward. Half speed')
    motor1.value = 0.5
    motor2.value = 0.5
    GPIO.output(26,False)
    GPIO.output(6,True)
    GPIO.output(13,False)

def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def shit_nigga():
    aiy.audio.say('Shiiit nigga, you tell me!')


def process_event(assistant, event):
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" (or "Hey, Google") then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'move forward':
            assistant.stop_conversation()
            forward_full()
        elif text == 'speed up':
            assistant.stop_conversation()
            forward_full()
        elif text == 'turn right':
            assistant.stop_conversation()
            right_turn()
        elif text == 'turn left':
            assistant.stop_conversation()
            left_turn()
        elif text == 'back up':
            assistant.stop_conversation()
            back_up()
        elif text == 'stop moving':
            assistant.stop_conversation()
            motor_off()
        elif text == 'go slow':
            assistant.stop_conversation()
            motor_on_half()
        elif text == 'slow down':
            assistant.stop_conversation()
            motor_on_half()
        elif text == 'where the hoes at':
            assistant.stop_conversation()
            shit_nigga()
  

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials, "polynomial-sum-199321-voice-kit") as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
