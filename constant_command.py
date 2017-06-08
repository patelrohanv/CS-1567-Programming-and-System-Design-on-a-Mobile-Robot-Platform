#!/usr/bin/env python

import rospy
import math
from geometry_msgs.msg import Twist


pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size=10)
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

def constantCommand():
    global pub, targetCommand, currentCommand
    rospy.init_node("constant_command", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)

    while pub.get_num_connections() == 0:
        pass
	
    while not rospy.is_shutdown():
	print("same")
	if(currentCommand.linear.x > 0):
		print("same2")
		#break
	if(targetCommand.linear.x > 0):
		print("same3")
		#break
        # Your code goes here
	#if the number is greater than the input, subtract from it.
#	while True:
#		if(currentCommand.linear.x > 0):
#			pub.publish(currentCommand)
#			break
#	if currentCommand.linear.x == 0.0 and currentCommand.angular.z == 0.0:
#		break
	pub.publish(targetCommand)
	print(str(targetCommand))

if __name__ == '__main__':
    constantCommand()

