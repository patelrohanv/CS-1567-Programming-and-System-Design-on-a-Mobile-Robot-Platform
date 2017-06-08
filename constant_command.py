#!/usr/bin/env python

import rospy
from kobuki_msgs.msg import Led
from kobuki_msgs.msg import ButtonEvent
import math
from geometry_msgs.msg import Twist


pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size=10)
pub1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10)
pub2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)
led = Led()
buttonGreen = True
currentCommand = Twist()
currentCommand.linear.x = 0.0
currentCommand.angular.z = 0.0
targetCommand = Twist()
targetCommand.linear.x = 0.0
targetCommand.angular.z = 0.0

def updateCommand(data):
    global targetCommand
    targetCommand = data

def cleanUp():
    global currentCommand
    currentCommand.linear.x = 0.0
    currentCommand.angular.z = 0.0
    pub.publish(currentCommand)
    rospy.sleep(1)

def buttonCallback(data):
    global pub1, led, buttonGreen
    str = ""
    if data.state != 0:
    	if data.button == 0:
        	str = str + "Button 0 is "
		if buttonGreen == True:
			targetCommand.linear.x = 0
			led.value = 3
			buttonGreen = False
		else:
			led.value = 1
			buttonGreen = True
		pub1.publish(led)
    	elif data.button == 1:
        	str = str + "Button 1 is "
    	else:
        	str = str + "Button 2 is "

    	if data.state == 0:
        	str = str + "released."
    	else:
        	str = str + "pressed."
    	rospy.loginfo(str)

def constantCommand():
    global pub, targetCommand, currentCommand, led, pub1
    rospy.init_node("constant_command", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)
    rospy.Subscriber('/mobile_base/events/button', ButtonEvent, buttonCallback)
    rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)

    if buttonGreen == True:
   	led.value = 1
    	pub1.publish(led)
    	print(str(led))
        

    while pub.get_num_connections() == 0:
        pass
	
    while not rospy.is_shutdown():
	if buttonGreen == True:
		pub.publish(targetCommand)
		print(str(targetCommand))
	else:
		tempCommand = targetCommand
		tempCommand.linear.x = 0.0	
		tempCommand.angular.z = 0.0
		pub.publish(tempCommand)
		print(str(tempCommand))

if __name__ == '__main__':
    constantCommand()
