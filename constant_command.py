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
x = 0.0
y = 0.0

def resetter():
    	pub = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty, 
		queue_size=10)
    	while pub.get_num_connections() == 0:
        	pass
    	pub.publish(Empty())

def odomCallback(data):
	global targetCommand, buttonGreen, pub, x , y
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
			targetCommand.linear.y = 0
			targetCommand.linear.x = 0
			targetCommand.angular.y = 0
			targetCommand.angular.z = 0
			currentCommand = targetCommand
			pub.publish(targetCommand)
			resetter()
			print("thisisx: " + str(x) + "thisislineary:" + str(targetCommand.linear.y))
		else:
			print("continue1")
	elif(targetCommand.linear.y < 0):
		if(x <= targetCommand.linear.y):
			targetCommand.linear.y = 0
			targetCommand.linear.x = 0
			targetCommand.angular.y = 0
			targetCommand.angular.z = 0
			currentCommand = targetCommand
			pub.publish(targetCommand)
			resetter()
			print("same?")
	else:
		targetCommand.linear.y = 0
		targetCommand.linear.x = 0
		pub.publish(targetCommand)
		#print("the final else")
		if(targetCommand.angular.z == 0.0):
			resetter()
	if(targetCommand.angular.y > 0):
		post = 0.0
		if (targetCommand.angular.y > 180):
			print "entered angle over 180"
			post = targetCommand.angular.y - 180
		if(post > 0.0 and degree > -180 and degree < -20):
			print "past 180"
			resetter()
			targetCommand.angular.y = post
		if(degree >= targetCommand.angular.y):
			#buttonGreen = False
			targetCommand.angular.y = 0
			targetCommand.angular.z = 0
			targetCommand.linear.y = 0
			targetCommand.linear.z = 0
			currentCommand = targetCommand
			pub.publish(targetCommand)
			#resetter()
			print("the most same")
	elif(targetCommand.angular.y < 0):
		print("this is target line: " + str(targetCommand.angular.y))
                print("this is current rotate: " + str(degree))
		#print("currentDegree: " + str(degree) + "targetCommand.angular y: " +  str(targetCommand.angular.y))
		post = 0.0
		if (targetCommand.angular.y < -180):
			post = targetCommand.angular.y + 180
			print("what even is this either")
		if (post < 0.0 and degree < 180 and degree > 20):
			print("why are we in here")
			resetter()
			targetCommand.angular.y = post
		if(degree <= targetCommand.angular.y):
			targetCommand.angular.y = 0
			targetCommand.angular.z = 0
			targetCommand.linear.y = 0
			targetCommand.linear.z = 0
			currentCommand = targetCommand
			pub.publish(targetCommand)
			#resetter()
			print("slightly almost mostsame")
	
	# angle y is how much we want to rotate.


    	msg = "(%.6f,%.6f) at %.6f degree." % (x, y, degree)
  	rospy.loginfo(msg)

def updateCommand(data):
    global targetCommand
    targetCommand = data

def cleanUp():
    global currentCommand
    currentCommand.linear.x = 0.0
    currentCommand.linear.y = 0.0
    currentCommand.angular.z = 0.0
    currentCommand.angular.y = 0.0
    pub.publish(currentCommand)
    rospy.sleep(1)

def bumperCallback(data):
    global pub1, led, buttonGreen, targetCommand
    if data.state == 1:
	targetCommand.linear.x = 0
	targetCommand.linear.y = 0
	targetCommand.angular.y = 0
	targetCommand.angular.z = 0
	print("button: " + str(buttonGreen) + "ledBefore:" + str(led))
	buttonGreen = False
	led.value= 3
	currentCommand = targetCommand
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
			targetCommand.angular.y = 0
			currentCommand = targetCommand
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
    global pub, targetCommand, currentCommand, led, pub1,pub2, buttonGreen, x , y
    rospy.init_node("constant_command", anonymous=True)
    rospy.Subscriber("kobuki_command", Twist, updateCommand)
    rospy.on_shutdown(cleanUp)
    rospy.Subscriber('/mobile_base/events/button', ButtonEvent, buttonCallback)
#    rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)
    rospy.Subscriber('/odom', Odometry, odomCallback)
#    rospy.Rate(100)
#    rospy.spin()
    resetter()
    print("same") 
    while pub.get_num_connections() == 0:
	pass
    if buttonGreen == True:
	led.value = 1
	pub1.publish(led)
	#print(str(led))


    while not rospy.is_shutdown():
	if(targetCommand.linear.z == 1.0):
		buttonGreen = False
		led.value = 3
		pub1.publish(led)
		targetCommand.linear.z = 0.0
		print("stillWRong")
	if buttonGreen == True:
		forward = True
		if targetCommand.linear.y < 0.0:
			forward = False
		currentCommand.linear.y = targetCommand.linear.y
		currentCommand.angular.z = targetCommand.angular.z
		currentCommand.angular.y = targetCommand.angular.y
		#this is where i will have to calculate speed.
		# x is global current distance.
		quarterDistance = targetCommand.linear.y / 4.0
		halfDistance = targetCommand.linear.y / 2.0
		threeQuarterDistance = quarterDistance + halfDistance
		quarterSpeed = targetCommand.linear.x * .08
		if (quarterDistance != 0):
			partialSpeed = targetCommand.linear.x * quarterDistance
		
		if (x < targetCommand.linear.y and targetCommand.linear.y > 0.0 and forward):
			if(targetCommand.linear.y != 0):
				if ( x < quarterDistance):
					currentCommand.linear.x += partialSpeed
				elif (x > quarterDistance and x < threeQuarterDistance):
					currentCommand.linear.x = targetCommand.linear.x
				elif ( x > threeQuarterDistance):
					print("currentComandLineax: " +  str(currentCommand.linear.x) + " partialSpeed: " + str(partialSpeed) + " x: " + str(x))
					currentCommand.linear.x -= partialSpeed
		elif (x > targetCommand.linear.y and targetCommand.linear.y < 0.0 and not forward):
			if(targetCommand.linear.y != 0):
				if ( x > quarterDistance):
                                        currentCommand.linear.x += (partialSpeed * -1.0)
                                elif (x < quarterDistance and x > threeQuarterDistance):
                                        currentCommand.linear.x = targetCommand.linear.x
                                elif ( x < threeQuarterDistance):
					print("currentComandLineax: " +  str(currentCommand.linear.x) + " partialSpeed: " + str(partialSpeed) + " x: " + str(x))					
                                        currentCommand.linear.x -= (partialSpeed * -1.0)
		#if(x < (targetCommand.linear.y )):
		#	if(targetCommand.linear.x != 0):
		#		if(x < halfDistance):
		#			currentCommand.linear.x += quarterSpeed
		#		else:
		#			currentCommand.linear.x -= quarterSpeed
		#elif(x > (targetCommand.linear.y)):
		#	if(targetCommand.linear.x != 0):
		#		print("goingbackwards")
		#		if(x < halfDistance):
		#			currentCommand.linear.x += (quarterSpeed * -1.0)
		#		else:
		#			currentCommand.linear.x -= (quarterSpeed * -1.0)
		else:
			targetCommand.linear.x = 0
			targetCommand.linear.y = 0
			currentCommand = targetCommand
		pub.publish(currentCommand)
		#rospy.sleep(0.1)
#		print("currentX: " + str(x))
#		print("currentY: "+  str(y))
#		print("targetCommand.linear.x:" + str(targetCommand.linear.x))
#		print("targetCommand.linear.y: " + str(targetCommand.linear.y))
#		print("currentCommandLinearX: " + str(targetCommand.linear.x))
#		print("currentCommandLinear.y" + str(targetCommand.linear.y))
	else:
		print("shoudlnebethere")
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
