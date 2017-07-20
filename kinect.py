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
isDepthImageReady = False;
colorImage = Image()
isColorImageReady = False;
xLocation = 320
yLocation = 240
pub = rospy.Publisher('kobuki_command', Twist, queue_size=10)
command = Twist()
bumper = True
pub1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10)
pub2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size=10)
led = Led()

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

def main():
    global depthImage, isDepthImageReady, colorImage, isColorImageReady, xLocation, yLocation, blobsInfo, isBlobsInfoReady
    rospy.init_node('image_converter', anonymous=True)
    #rospy.init_node('showBlobs', anonymous=True)
    rospy.Subscriber("/blobs", Blobs, updateBlobsInfo)
    rospy.Subscriber("/camera/depth/image", Image, updateDepthImage, queue_size=10)
    rospy.Subscriber("/camera/rgb/image_color", Image, updateColorImage, queue_size=10)
    bridge = CvBridge()
    cv2.namedWindow("Color Image")
    cv2.setMouseCallback("Color Image", mouseClick)

    while not isColorImageReady:
	print("were passing colorImage")
        pass

    while not isDepthImageReady:
	print("were passing depthImage")
        pass


    while not rospy.is_shutdown():
        try:
            depth = bridge.imgmsg_to_cv2(depthImage, desired_encoding="passthrough")
        except CvBridgeError, e:
            print e
            print "depthImage"

        try:
            color_image = bridge.imgmsg_to_cv2(colorImage, "bgr8")
        except CvBridgeError, e:
            print e
            print "colorImage"
        
	blobsCopy = copy.deepcopy(blobsInfo)
	height = blobsCopy.image_height
	width = blobsCopy.image_width
	lowestMiddleVar = (width/2) - 50
	highestMiddleVar = (width/2) + 50
	largestBlob = None
	largestBlobSize = 0
        depthValue = depth.item(yLocation,xLocation,0)
	for b in blobsCopy.blobs:
		if b.name !=  "LightBlue":
			print("largestBlob is not bright green")
			continue
		cv2.rectangle(color_image, (b.left, b.top), (b.right, b.bottom), (0,255,0), 2)
		if(largestBlob == None):
			largestBlob = b
			largestBlobSize = b.right - b.left
		elif((b.right - b.left) > largestBlobSize):
			largestBlob = b
	if (largestBlob != None):
		xLocation = largestBlob.x
		yLocation = largestBlob.y
	else:
		print "No largest blob"
		command.linear.x = 0.0
		command.linear.y = 0.0
		command.angular.y = 0.0
		command.angular.z = 0.0
		pub.publish(command)
		continue
        print "Depth at (%i,%i) is %f." % (xLocation,yLocation,depthValue)
	print color_image

	command.linear.x = 0.4
	command.linear.y = 0.3
	if(depthValue < 0.5 or math.isnan(depthValue)):
		command.linear.x = 0.0
		command.linear.y = 0.0
	elif(depthValue > 1.1):
		#speed up
		command.linear.x += 0.2
	elif(depthValue < 0.9):
		#slow down
		command.linear.x -= 0.2
	
	if(xLocation < lowestMiddleVar):
		 print("largestblob is bright green")
                 errorNumber = lowestMiddleVar - largestBlob.x
                 outputNumber = .04 * errorNumber
                 if(outputNumber > 1.0):
                 	outputNumber = 1.0
                 command.angular.y = 0.2
                 command.angular.z = outputNumber
	elif(xLocation > highestMiddleVar):
         	errorNumber = largestBlob.x - highestMiddleVar
                outputNumber = .04 * errorNumber
                outputNumber = outputNumber * -1.0
                if(outputNumber < -1.0):
                	outputNumber = -1.0
                command.angular.y = -0.2
                command.angular.z = outputNumber
        elif(xLocation >= lowestMiddleVar and xLocation <= highestMiddleVar):                                
                command.angular.y = 0.0
                command.angular.z = 0.0
	else:
		command.angular.y = 0.0
		command.angular.z = 0.0

	pub.publish(command)
        depthStr = "%.2f" % depthValue

        cv2.rectangle(color_image, (xLocation-10,yLocation-10), (xLocation+10,yLocation+10), (0,255,0), 2)
        cv2.putText(color_image, depthStr, (xLocation+15,yLocation+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        cv2.imshow("Color Image", color_image)
        cv2.waitKey(1)

    cv2.destroyAllWindows()


 
if __name__ == '__main__':
    main()
