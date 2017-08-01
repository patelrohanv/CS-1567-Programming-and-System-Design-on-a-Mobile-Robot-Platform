#!/usr/bin/env python
import roslib
#roslib.load_manifest('rosopencv')
import sys
import rospy
import cv2
import math
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import Led
from kobuki_msgs.msg import ButtonEvent
from kobuki_msgs.msg import BumperEvent
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from cmvision.msg import Blobs, Blob
from struct import unpack
import copy

blobsInfo = Blobs()
isBlobsInfoReady = False
depthImage = Image()
isDepthImageReady = False
colorImage = Image()
isColorImageReady = False
xLocation = 320
yLocation = 240
pub = rospy.Publisher('kobuki_command', Twist, queue_size=10)
command = Twist()
bumper = True
pub1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10)
pub2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)
led = Led()
turnInfo = 0.0
checkCorner = False

def mouseClick(event, x, y, flags, param):
    global xLocation, yLocation
    if event == cv2.EVENT_LBUTTONDOWN:
        xLocation = x
        yLocation = y

def updateDepthImage(data):
    global depthImage, isDepthImageReady
    depthImage = data
    isDepthImageReady = True

def updateColorImage(data):
    global colorImage, isColorImageReady
    colorImage = data
    isColorImageReady = True

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
    global pub, pub1, led, buttonGreen, command, bumper
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

def isNaN(num):
    return num != num

def main():
    global depthImage, isDepthImageReady, colorImage, isColorImageReady, xLocation, yLocation, blobsInfo, isBlobsInfoReady, turnInfo, checkCorner
    rospy.init_node('depth_example', anonymous=True)
    #rospy.init_node('showBlobs', anonymous=True)
    rospy.Subscriber("/blobs", Blobs, updateBlobsInfo)
    rospy.Subscriber("/camera/depth/image", Image, updateDepthImage, queue_size=10)
    rospy.Subscriber("/camera/rgb/image_color", Image, updateColorImage, queue_size=10)
    bridge = CvBridge()
    cv2.namedWindow("Color Image")
    cv2.setMouseCallback("Color Image", mouseClick)

    #depthImage, isDepthImageReady
    while not isDepthImageReady:
	pass

    while not rospy.is_shutdown():
	#step is the array of bytes
        step = depthImage.step
        midX = 320
        midY = 240
        #multiply 240 by the step to get the row of pixles down to the middle.
        # 320*4 so that we can go over 320 pixles but there are 4 bytes
        #middle
        offset = (240 * step) + (320 * 4)
        offsetBegining = (240*step) + (80*4)
        offsetEnd = (240*step) + (560*4)
        #We have to use 4 bytes to get the pixel depth. thats why its +1,2,3.
	(dist,) = unpack('f', depthImage.data[offset] + depthImage.data[offset+1] + depthImage.data[offset+2] + depthImage.data[offset+3])
        #print "Distance: %f" % dist

	(distBegin,) = unpack('f', depthImage.data[offsetBegining] + depthImage.data[offsetBegining+1] + depthImage.data[offsetBegining+2]  + depthImage.data[offsetBegining+3])
	#print "distanceBegining: %f" % distBegin

	(distEnd,) = unpack('f', depthImage.data[offsetEnd] + depthImage.data[offsetEnd+1] + depthImage.data[offsetEnd+2] + depthImage.data[offsetEnd+3])
	#print "distangeEnd: %f" % distEnd

        distDiff = distBegin - distEnd
        distAbs = math.fabs(distDiff)
        # this is the treshold of difference between the left and right side distances.
	distanceThresh = 0.3


	#print("distancediff:" + str(distDiff))
	#print("distanceDifferenceAbs:" + str(distAbs))
	#print("distancebegin" + str(distBegin))
	#print("distanceEnd" + str(distEnd))
	print("disance mid  " + str(dist))
	if(isNaN(distEnd) == True and isNaN(distBegin) == False):
		#turn left
		command.angular.z = 0.6
		command.angular.y = 45
		command.linear.x = 0.1
		command.linear.y = 0.1
		pub.publish(command)
	elif(isNaN(distEnd) == False and isNaN(distBegin) == True):
		#turn right
		command.angular.z = -0.6
		command.angular.y = -45
		command.linear.x = 0.1
		command.linear.y = 0.1
		pub.publish(command)	

	
        # if the distance is large, we need to check which is larger and then move accordingly.        
	else:
		if((dist > 1.2)  or isNaN(dist) ):
			command.linear.x = 0.2
			command.linear.y = 0.2
			command.angular.y = 0.0
			command.angular.z = 0.0
			pub.publish(command)
		elif(not checkCorner):
			checkCorner = True
			command.angular.y = -180
			command.angular.z = 0.5
			command.linear.x = 0.0
			command.linear.y = 0.0
			pub.publish(command)
			rospy.sleep(2)
		elif(checkCorner):
			checkCorner = False
			command.angular.y = 90 
			command.angular.z = 0.5
			command.linear.x = 0.0
			command.linear.y = 0.0
			pub.publish(command)
			rospy.sleep(2)

    cv2.destoryAllWindows()

 
if __name__ == '__main__':
    main()
