#!/usr/bin/env python

import rospy
from kobuki_msgs.msg import Led
from kobuki_msgs.msg import ButtonEvent
from kobuki_msgs.msg import BumperEvent
from std_msgs.msg import Empty
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

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
targetCommand.linear.y = 0.0
targetCommand.angular.z = 0.0

def resetter():
    	pub = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty, 
		queue_size=10)
    	while pub.get_num_connections() == 0:
        	pass
    	pub.publish(Empty())

def odomCallback(data):
	global targetCommand, buttonGreen, pub
 	   # Convert quaternion to degree
	q = [data.pose.pose.orientation.x,
        	data.pose.pose.orientation.y,
         	data.pose.pose.orientation.z,
         	data.pose.pose.orientation.w]
    	roll, pitch, yaw = euler_from_quaternion(q)
    	# roll, pitch, and yaw are in radian
    	degree = yaw * 180 / math.pi
    	x = data.pose.pose.position.x
    	y = data.pose.pose.position.y

	if(targetCommand.linear.y > 0):
    		if(x >= targetCommand.linear.y):
			buttonGreen = False
			targetCommand.linear.x = 0
			pub.publish(targetCommand)
			print("thisisx: " + str(x) + "thisislineary:" + str(targetCommand.linear.y))
	elif(targetCommand.linear.y < 0):
		if(x <= targetCommand.linear.y):
			buttonGreen = False
			targetCommand.linear.x = 0
			pub.publish(targetCommand)
			print("same?")	


    	msg = "(%.6f,%.6f) at %.6f degree." % (x, y, degree)
  	rospy.loginfo(msg)

def updateCommand(data):
    global targetCommand
    targetCommand = data

def cleanUp():
    global currentCommand
    currentCommand.linear.x = 0.0
    currentCommand.angular.z = 0.0
    pub.publish(currentCommand)
    rospy.sleep(1)

def bumperCallback(data):
    global pub1, led, buttonGreen, targetCommand
    if data.state == 1:
	targetCommand.linear.x = 0
	targetCommand.linear.y = 0
	targetCommand.angular.z = 0
	print("button: " + str(buttonGreen) + "ledBefore:" + str(led))
	buttonGreen = False
	led.value= 3
	pub1.publish(led)

def buttonCallback(data):
    global pub1, led, buttonGreen, targetCommand
    str = ""
    if data.state != 0:
    	if data.button == 0:
        	str = str + "Button 0 is "
		if buttonGreen == True:
			targetCommand.linear.x = 0
			targetCommand.linear.y = 0
			targetCommand.angular.z = 0
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
    global pub, targetCommand, currentCommand, led, pub1, buttonGreen
    rospy.init_node("constant_command", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)
    rospy.Subscriber('/mobile_base/events/button', ButtonEvent, buttonCallback)
#    rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)
    rospy.Subscriber('/odom', Odometry, odomCallback)
#    rospy.spin()
    resetter()
    print("same") 
    while pub.get_num_connections() == 0:
	pass

    if buttonGreen == True:
	led.value = 1
	pub1.publish(led)
	print(str(led))

    while not rospy.is_shutdown():
	if buttonGreen == True:
		pub.publish(targetCommand)
		if (targetCommand.linear.x != 0.0):
			print(str(targetCommand))
	else:
		tempCommand = targetCommand
		tempCommand.linear.x = 0.0	
		tempCommand.linear.y = 0.0
		tempCommand.angular.z = 0.0
		pub.publish(tempCommand)
#		print(str(tempCommand))
	rospy.sleep(0.1)

if __name__ == '__main__':
# we will prob need to run this reset before we do anything.
#	resetter()    
#        odomExample()
	constantCommand()
