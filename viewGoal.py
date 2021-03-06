#!/usr/bin/env python

import roslib
import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import Led
from kobuki_msgs.msg import ButtonEvent
from kobuki_msgs.msg import BumperEvent
import cv2
import copy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from cmvision.msg import Blobs, Blob
import math
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from std_msgs.msg import Empty


colorImage = Image()
isColorImageReady = False
blobsInfo = Blobs()
isBlobsInfoReady = False
pub = rospy.Publisher('kobuki_command', Twist, queue_size=10)
command = Twist()
bumper = True
pub1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10)
pub2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)
led = Led()
x = 0.0
y = 0.0
degree = 0.0
firstRedBall = 0.0
firstSame = 0.0
firstTimeMoveLeft = 0.0
secondRedBall = 0.0
goalAngle = 0.0
largestLargestPinkBlob = None
largestLargestPinkBlobSize = 0
largestLargestPinkBlobAngle = 0.0
lastBall = 0.0
fin = 0.0

#step number = which step we are trying to solve / angles we need to get.
stepNumber = 0

def resetter():
        pub = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty,
                queue_size=10)
        while pub.get_num_connections() == 0:
                pass
        pub.publish(Empty())

def odomCallback(data):
        global command, bumper, pub, x , y, degree
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
	
	# First step, trying to get the angle from the start position before we move 1.5 meters
	if(stepNumber == 0):
		same = 5
#	msg = "(%.6f,%.6f) at %.6f degree." % (x, y, degree)
#        rospy.loginfo(msg)

def bumperCallback(data):
    global pub, command, bumper, led
    if data.state == 1:
        command.linear.x = 0
        command.linear.y = 0
        command.linear.z = 0
        command.angular.z = 0
        command.angular.y = 0
	bumper = False
	led.value = 3
        pub.publish(command)
	pub1.publish(led)

def buttonCallback(data):
    global pub1, led, buttonGreen, command, bumper
    str = ""
    if data.state != 0:
        if data.button == 0:
                str = str + "Button 0 is "
                if bumper == True:
                        command.linear.x = 0
                        command.linear.y = 0
                        command.angular.z = 0
                        command.angular.y = 0
                        led.value = 3
                        bumper = False
                else:
                        led.value = 1
                        bumper = True
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


def updateColorImage(data):
    global colorImage, isColorImageReady
    colorImage = data
    isColorImageReady = True

def updateBlobsInfo(data):
    global blobsInfo, isBlobsInfoReady
    blobsInfo = data
    isBlobsInfoReady = True

def getLargestPinkBlob(blobsCopy):
        for b in blobsCopy.blobs:
		if (b.name != "BrightPink"):
			continue
                cv2.rectangle(color_image, (b.left, b.top), (b.right, b.bottom), (0,255,0), 2)
                if(largestBlob == None):
                        largestBlob = b
                        largestBlobSize = b.right - b.left
                elif((b.right - b.left) > largestBlobSize):
                        largestBlob = b
	return largestBlob

def getRedBlob(blobsCopy):
	for b in blobsCopy.blobs:
		if (b.name != "Red"):
			continue
		cv2.rectangle(color_image, (b.left, b.top), (b.right, b.bottom), (0,255,0), 2)
		if(largestBlob == None):
			largestBlob = b
			largestBlobSize = b.right - b.left
		elif((b.right - b.left) > largestBlobSize):
			largestBlob = b
	return largestBlob		

def main():
    global colorImage,fin, lastBall, led, isColorImageReady,firstTimeMoveLeft,secondRedBall, blobsInfo, isBlobsInfoReady, pub, bumper,largestLargestPinkBlob,largestLargestPinkBlobSize, largestLargestPinkBlobAngle, command, pub1, x, y, degree, stepNumber, firstRedBall, firstSame, goalAngle
    rospy.init_node('showBlobs', anonymous=True)
    rospy.Subscriber("/blobs", Blobs, updateBlobsInfo)
    rospy.Subscriber("/v4l/camera/image_raw", Image, updateColorImage)
    rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)
    rospy.Subscriber('/mobile_base/events/button', ButtonEvent, buttonCallback)
    bridge = CvBridge()
    cv2.namedWindow("Blob Location")
    rospy.Subscriber('/odom', Odometry, odomCallback)
    secondRotate = 0.0
    resetter()
    while not rospy.is_shutdown() and (not isBlobsInfoReady or not isColorImageReady):
        pass

    while not rospy.is_shutdown():
        try:
	   # command.angular.y = 0.5
 	   # command.angular.z = 10
	   # pub.publish(command)
            color_image = bridge.imgmsg_to_cv2(colorImage, "bgr8")
        except CvBridgeError, e:
            print e
            print "colorImage"
	#secondRotate = 0.0
#	resetter()
	if(bumper != False):
		led.value = 1
		pub1.publish(led)
        	blobsCopy = copy.deepcopy(blobsInfo)
		height = blobsCopy.image_height
		width = blobsCopy.image_width
		lowestMiddleVar = (width/2) - 10
		highestMiddleVar = (width/2) + 10
#		print(blobsCopy)
		largestBlob = None
		largestBlobSize = 0
		largestBlobPink = None
		largestBlobPinkSize = 0

		for b in blobsCopy.blobs:
			cv2.rectangle(color_image, (b.left, b.top), (b.right, b.bottom), (0,255,0), 2)
			if (b.name == "Red"):
				if(largestBlob == None):
					largestBlob = b
					largestBlobSize = b.right - b.left
				elif((b.right - b.left) > largestBlobSize):
					largestBlob = b
			if(b.name == "BrightPink"):
				if(largestBlobPink == None):
					largestBlobPink = b
					largestBlobPinkSize = b.right - b.left
				elif((b.right - b.left) > largestBlobPinkSize):
					largestBlobPink = b
		
			
			#print(str(cv2.rectangle))
		if(firstRedBall == 0.0):
			if(goalAngle != 0.0):
				print("we should be sleeping for 10secs")
				command.linear.x = 0.0
				command.linear.y = 0.0
				command.angular.y = -2.0
				command.angular.z = 60
				rospy.sleep(2.0)
				pub.publish(command)
			if(largestBlob != None):
				print("we are searching again")	
				if(largestBlob.x < lowestMiddleVar):
					errorNumber = lowestMiddleVar - largestBlob.x
					outputNumber = .04 * errorNumber
					if(outputNumber > 1.0):
						outputNumber = 1.0
					command.linear.x = 0.0
					command.linear.y = 0.0
					command.angular.y = 0.2
					command.angular.z = outputNumber
					pub.publish(command)
				elif(largestBlob.x > highestMiddleVar):
			        	errorNumber = largestBlob.x - highestMiddleVar
                                	outputNumber = .04 * errorNumber
					outputNumber = outputNumber * -1.0
                                	if(outputNumber < -1.0):
                                        	outputNumber = -1.0
					command.linear.x = 0.0
					command.linear.y = 0.0
					command.angular.y = -0.2
					command.angular.z = outputNumber
					pub.publish(command)
				elif(largestBlob.x >= lowestMiddleVar and largestBlob.x <= highestMiddleVar):
					command.linear.x = 0.0
					print("we found a red ball")
					command.linear.y = 0.0
					command.angular.y = 0.0
					command.angular.z = 0.0
					pub.publish(command)
					if(secondRedBall != 0.0):
						print("Time to go forward")
						command.linear.x = 0.8
						command.linear.y = 1.0
						command.angular.y = 0.1
						command.angular.z = 0.1
						pub.publish(command)
						rospy.sleep(5.0)
						bumper = False
					firstRedBall = degree
					resetter()
					print(str(largestBlob.x))
					print(str(degree))
				#print(largestBlob)
				#print bumper
			else:
				#print("no large blob")
				#bumper = False
				led.value = 1
				pub1.publish(led) 
				command.linear.x = 0.0
				command.linear.y = 0.0
				command.angular.y = -5.0
				command.angular.z = -0.5
        			pub.publish(command)
		else:
			#if the red ball has already been collected, (first time)
			if(firstSame == 0.0 and secondRotate == 0.0):
				firstRedBall = firstRedBall * -1.0
				rotateAmount = firstRedBall + 90.0
			 	if(rotateAmount > 180.0):
					same = 5
					#rotateAmount - 180.0
				elif(rotateAmount < 180.0):
					same = 5
					#rotateAmount + 180.0
				if(degree < rotateAmount):
					command.angular.y = 20
					command.angular.z = 0.7 
					pub.publish(command)
					#firstSame = 1.0
					rospy.sleep(0.9)
					#print("currentdegree: " + str(degree) + " firstRedBall + 90.0 " + str(firstRedBall + 90.0)) 
				else:
					command.angular.y = 0.0
					command.angular.z = 0.0
					pub.publish(command)
					secondRotate = 1.0
					firstSame = 1.0
			elif(secondRotate == 1.0):
				#print("firstTimemoveleft:" + str(firstTimeMoveLeft))
				if(firstTimeMoveLeft == 0.0):
					if(x < 1.0):
						command.linear.x = 0.3
						command.linear.y = 1.0
						pub.publish(command)
						rospy.sleep(4.0)
						command.linear.x = 0.0
						command.linear.y = 0.0
						pub.publish(command)
						rospy.sleep(3.0)
						command.angular.y = -90.0
						command.angular.z = -0.7
						pub.publish(command)
						rospy.sleep(4.0)
						firstTimeMoveLeft = 1.0
						#command.angular.y = -90.0
                                        	#command.angular.z = -0.7
                                        	#pub.publish(command)
                                        	#rospy.sleep(2.0)
						#resetter()
						#command.angular.y = -90.0
                                        	#command.angular.z = -0.7
                                        	#pub.publish(command)
                                        	#rospy.sleep(1.2)
						resetter()
					else:
						print("x is > 1.0")
					# we now have moved to the left 1 meter.
				else:
					# print("firstRedBall" + str(firstRedBall))
					# print("secondRedBall" + str(secondRedBall))
					 if(secondRedBall == 0.0):
						# find goal
						# find ball
						# subtract ball angle from goal angle
                        			if(largestBlob != None):
                                			if(largestBlob.x < lowestMiddleVar):
                                        			errorNumber2 = lowestMiddleVar - largestBlob.x
                                        			outputNumber2 = .04 * errorNumber2
                                        			if(outputNumber2 > 1.0):
                                                			outputNumber2 = 1.0
                                        			command.linear.x = 0.0
                                        			command.linear.y = 0.0
                                        			command.angular.y = 0.2
                                        			command.angular.z = outputNumber2
                                        			pub.publish(command)
                                			elif(largestBlob.x > highestMiddleVar):
                                        			errorNumber2 = largestBlob.x - highestMiddleVar
                                        			outputNumber2 = .04 * errorNumber2
                                        			outputNumber2 = outputNumber2 * -1.0
                                        			if(outputNumber2 < -1.0):
                                                			outputNumber2 = -1.0
                                        			command.linear.x = 0.0
                                        			command.linear.y = 0.0
                                        			command.angular.y = -0.2
                                        			command.angular.z = outputNumber2
                                        			pub.publish(command)
							elif(largestBlob.x >= lowestMiddleVar and largestBlob.x <= highestMiddleVar):
								command.linear.x = 0.0
								command.linear.y = 0.0
								command.angular.y = 0.0
								command.angular.z = 0.0
								pub.publish(command)
								secondRedBall = degree
								#resetter()
								#getting angle between the goal and ball
			                                        #print("goalAngle" + str(goalAngle))
                                                else:
                                                	#print("no large blob")
                                                        #bumper = False
                                                        led.value = 1
                                                        pub1.publish(led)
                                                        command.linear.x = 0.0
                                                        command.linear.y = 0.0
                                                        command.angular.y = -5.0
                                                        command.angular.z = -0.5
                                                        pub.publish(command)
                                                        # blobs.name
                        		
			                 else:
						#if you got the second red ball, get the goal angle
						#TODO, we need to do a full scan to find the largest pink blob.
						#print("goalAngle:" + str(goalAngle))
						if(goalAngle == 0.0):
                                                	if(largestBlobPink != None):
								lowestMiddleVar = lowestMiddleVar - 20
								highestMiddleVar = highestMiddleVar + 20
								if(largestBlobPink.x >= lowestMiddleVar and largestBlobPink.x <= highestMiddleVar):
									if(largestBlobPinkSize > largestLargestPinkBlobSize):
										largestLargestPinkBlobSize = largestBlobPinkSize
										largestLargestPinkBlobAngle = degree
										#this should end up leaving us with the degree of the goal because its the largest largest
										print("largestlargestPinkDegree: " + str(largestLargestPinkBlobAngle))
										#bumper = False;
									else:
										print("currentDegree: " + str(degree))
									#move it to the left so that we can get all pink blobs.

							        command.linear.x = 0.0
                                                        	command.linear.y = 0.0
                                                        	command.angular.y = 2.0
                                                        	command.angular.z = 0.2
                                                        	pub.publish(command)

			                        	#	if(largestBlobPink.x < lowestMiddleVar):
                        			        #		errorNumber3 = lowestMiddleVar - largestBlobPink.x
                                                	#		outputNumber3 = .04 * errorNumber3
                                                         #       	if(outputNumber3 > 1.0):
                                                          #      		outputNumber3 = 1.0
                                                           #     	command.linear.x = 0.0
                                                           #     	command.linear.y = 0.0
                                                           #   		command.angular.y = 0.2
                                                            #  		command.angular.z = outputNumber3
                                                            #    	pub.publish(command)
                                                        #	elif(largestBlobPink.x > highestMiddleVar):
                                                        #		errorNumber3 = largestBlobPink.x - highestMiddleVar
                                                        #     		outputNumber3 = .04 * errorNumber2
                                                        #      		outputNumber3 = outputNumber3 * -1.0
                                                        #        	if(outputNumber3 < -1.0):
                                                        #        		outputNumber3 = -1.0
                                                        #        	command.linear.x = 0.0
                                                        #       		command.linear.y = 0.0
                                                        #       	command.angular.y = -0.2
                                                        #        	command.angular.z = outputNumber3
                                                        #        	pub.publish(command)
                                                       # 	elif(largestBlobPink.x >= lowestMiddleVar and largestBlobPink.x <= highestMiddleVar):
                                                        #		command.linear.x = 0.0
                                                        #        	command.linear.y = 0.0
                                                        #        	command.angular.y = 0.0
                                                        #        	command.angular.z = 0.0
                                                        #        	pub.publish(command)
                                                        #        	goalAngle = degree
                                                        #        	resetter()
						#			print("we got the goal")
									#end getting goalAngle
							else:
                                				#print("no large blob")
                                				#bumper = False
                                				led.value = 1
                               					pub1.publish(led)
                                				command.linear.x = 0.0
                                				command.linear.y = 0.0
                                				command.angular.y = 0.0
                                				command.angular.z = 0.0
                                				pub.publish(command)
								print("firstRedBall: " + str(firstRedBall))
								print("secondREdBall: " + str(secondRedBall))
								print("finalGoal: " + str(largestLargestPinkBlobAngle))
								firstRedBall = firstRedBall * -1.0
								secondRedBall = secondRedBall * -1.0
								secondRedBall = 90-secondRedBall
								largest = largestLargestPinkBlobAngle * -1.0
								kick = setupKick(1.0, firstRedBall, secondRedBall, largest)
								print(str(setupKick(1.0,firstRedBall,secondRedBall,largest)))
								#recenter the kobuki
								if(kick != 0):
									print("kick: " + str(kick))
									print("degree:" + str(degree))
									print("secondRedBall + FinalGoal:" + str(secondRedBall + largest))
									otherDegree = degree + 20
									otherDegree = 90 - otherDegree
									rospy.sleep(1.0)
									degree = 0.0
									resetter()
									print("degree after reset" + str(degree))
									print("otherDegree: " + str(otherDegree))
									while(degree < otherDegree):
										print("we did a thing")
										command.angular.z = 0.2
										command.angular.y = 2.0
										command.linear.x = 0.0
										command.linear.y = 0.0
										pub.publish(command)
										rospy.sleep(0.2)
					
									kick = kick * -1.0
									kick = kick - 1.0
									#kick = kick - 1.0
									resetter()
									while(x > kick):
										print("this is y: " + str(y))
										print("this is x: " + str(x))
										print("kick: " + str(kick))
										command.linear.x = -0.2
										command.linear.y = -0.2
										command.angular.y = 0.0
										command.angular.z = 0.0
										pub.publish(command)
										rospy.sleep(0.2)
										if(x < kick):
											lastBall = 1.0
											command.linear.x = 0.0
											command.linear.y = 0.0
											command.angular.y = 0.0
											command.angular.z = 0.0
											pub.publish(command)
											rospy.sleep(0.2)
									if(x < kick or lastBall == 1.0):
										   #now we have to look for the ball and hit it in
										  # command.linear.x = 0.0
                                                                                  # command.linear.y = 0.0
                                                                                  # command.angular.y = 2.0
                                                                                  # command.angular.z = 0.2
                                                                                  # pub.publish(command)
                                                                                  # rospy.sleep(5.2)
										   firstRedBall = 0.0
										   if(fin != 1.0):
										   	if(largestBlob != None):
												print("we got a large blob?")
                                								if(largestBlob.x < lowestMiddleVar):
                                        								errorNumber4 = lowestMiddleVar - largestBlob.x
                                        								outputNumber4 = .04 * errorNumber4
                                        								if(outputNumber4 > 1.0):
                                                								outputNumber4 = 1.0
                                        								command.linear.x = 0.0
                                        								command.linear.y = 0.0
                                        								#command.angular.y = 0.2
                                        								#command.angular.z = outputNumber4
                                        								pub.publish(command)
                                								elif(largestBlob.x > highestMiddleVar):
                                        								errorNumber4 = largestBlob.x - highestMiddleVar
                                        								outputNumber4 = .04 * errorNumber4
                                        								outputNumber4 = outputNumber4 * -1.0
                                        								if(outputNumber4 < -1.0):
                                                								outputNumber4 = -1.0
                                        								command.linear.x = 0.0
                                        								command.linear.y = 0.0
                                        								#command.angular.y = -0.2
                                        								#command.angular.z = outputNumber4
                                        								pub.publish(command)
                                								elif(largestBlob.x >= lowestMiddleVar and largestBlob.x <= highestMiddleVar):
                                        								command.linear.x = 1.0
                                        								command.linear.y = 1.0
                                        								command.angular.y = 0.0
                                        								command.angular.z = 0.0
                                        								pub.publish(command)
                                        								resetter()
													fin = 1.0
                                        								print(str(largestBlob.x))
                                        								print(str(degree))
										   	else:
												#turn to find the ball
												print("trying to find the last ball")
												lastBall = 1.0
												command.linear.x = 0.0
                                        							command.linear.y = 0.0
                                        							#command.angular.y = -2.0
                                        							#command.angular.z = -0.4
                                        							pub.publish(command)
												#rospy.sleep(0.5)

									print("x:" + str(x))
									print("kick: " + str(kick))
									command.linear.x = 0.0
                                                                        command.linear.y = 0.0
                                                                        command.angular.y = -2.0
                                                                        command.angular.z = -0.4
                                                                        pub.publish(command)
									rospy.sleep(1.0)

											
	else:
		#print("this is happening")
		command.linear.x = 0.0
		command.linear.y = 0.0
		command.angular.y = 0.0 
		command.angular.z = 0.0
		pub.publish(command)
	cv2.imshow("Color Image", color_image)
        cv2.waitKey(1)
#	print("bumper:" + str(bumper))

### START DOC FOR MATH

# alpha is the angle between zero and the ball when at the starting point
# N is the distance travelled from the starting point
# theta is the angle between zero and the ball after travelling N
# phi is the angle between the ball and goal after travelling N 
# x is the distance that needs to be travelled from the starting point to kick the ball
def getB (N, theta):
        b = N * math.tan(theta)
        return b

def getA (N, theta, phi):
        a = N * math.tan(theta + phi) - N * math.tan(theta)
        return a

def setupKick (N, firstBall, secondBall, goal):
        # convert theta and phi to radians
        alpha = math.radians(firstBall)
        theta = math.radians(secondBall)
        phi = math.radians(goal)

        b = getB(N, theta)
        a = getA(N, theta, phi)
        x = (a+b) / (math.tan(90-alpha))
        return (N + x) #distance that needs to be travelled to kick the ball

### END DOC FOR MATH


if __name__ == '__main__':
    main()
