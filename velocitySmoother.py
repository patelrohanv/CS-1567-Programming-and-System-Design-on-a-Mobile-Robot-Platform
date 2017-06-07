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

def velSmoother():
    global pub, targetCommand, currentCommand
    rospy.init_node("velocitySmoother", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)

    while pub.get_num_connections() == 0:
        pass
	
    while not rospy.is_shutdown():
        # Your code goes here
	#if the number is greater than the input, subtract from it.

	brakeFlag = False
	while True:
		print("same")
		#start if/else - checking for full brake signal
		if currentCommand.linear.x == 0.0123 or currentCommand.linear.x == -0.0123:
			currentCommand.linear.x = 0.0
			currentCommand.angular.z = 0.0	
			targetCommand.linear.x = 0.0
			targetCommand.angular.z = 0.0	
			brakeFlag = True
			continue
		else:
			brakeFlag = False
		#end if/else - checking for full brake signal
		#start if/else
		if currentCommand.angular.z > targetCommand.angular.z:
			if math.fabs(targetCommand.angular.z - currentCommand.angular.z) < 0.01:
				#break
				j = 1
			else:
				currentCommand.angular.z = currentCommand.angular.z- 0.30
		else:
			if math.fabs(targetCommand.angular.z - currentCommand.angular.z) < 0.01:
				#break
				j = 1
			else:
				currentCommand.angular.z = currentCommand.angular.z + 0.30
		#end if/else
		#start if
		if currentCommand.angular.z == targetCommand.angular.z:
                	#break
			j = 1
		#end if
		#start if/else
		if currentCommand.linear.x > targetCommand.linear.x:
			if math.fabs(targetCommand.linear.x - currentCommand.linear.x) < 0.01:
				#break
				j = 1
			else:
				currentCommand.linear.x = currentCommand.linear.x- 0.15
		else:
			if math.fabs(targetCommand.linear.x - currentCommand.linear.x) < 0.01:
				#break
				j = 1
			else:
				currentCommand.linear.x = currentCommand.linear.x + 0.15
		#end if/else
		#start if
		if currentCommand.linear.x == targetCommand.linear.x:
                	#break
			j = 1

		#end if
		#else if the number is less than the input, add to it.
	
		#if statement to try and correct for the robot drifting right	
		if currentCommand.angular.z < 0.00001 and currentCommand.angular.z > -0.00001:
			currentCommand.angular.z = 0
		if currentCommand.linear.x < 0.00001 and currentCommand.linear.x > -0.00001:
			currentCommand.linear.x = 0

        	pub.publish(currentCommand)
		print ("currentCommand.angular: " + str(currentCommand.angular.z))
		print ("currentCommand.linear: " + str(currentCommand.linear.x))
		print ("targetCommand.angular: " + str(targetCommand.angular.z))
		print ("targetCommand.linear: " + str(targetCommand.linear.x))

        	rospy.sleep(0.1)

		if currentCommand.angular.z == 0.0 and currentCommand.linear.x == 0.0 and not brakeFlag:
			print ("breaking out")
			break

if __name__ == '__main__':
    print("start velocity smoother")
    velSmoother()

