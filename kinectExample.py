#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from struct import *
import math

depthData = Image();
isDepthReady = False;

def depthCallback(data):
    global depthData, isDepthReady
    depthData = data
    isDepthReady = True

def main():
    global depthData, isDepthReady
    rospy.init_node('depth_example', anonymous=True)
    rospy.Subscriber("/camera/depth/image", Image, depthCallback, queue_size=10)

    while not isDepthReady:
        pass

    while not rospy.is_shutdown():
	#step is the array of bytes
        step = depthData.step
        midX = 320
        midY = 240
	#multiply 240 by the step to get the row of pixles down to the middle.
	# 320*4 so that we can go over 320 pixles but there are 4 bytes
	#middle
        offset = (240 * step) + (320 * 4)
	offsetBegining = (240*step) + (0*4)
	offsetEnd = (240*step) + (640*4)
	#We have to use 4 bytes to get the pixel depth. thats why its +1,2,3.
        (dist,) = unpack('f', depthData.data[offset] + depthData.data[offset+1] + depthData.data[offset+2] + depthData.data[offset+3])
        #print "Distance: %f" % dist

	(distBegin,) = unpack('f', depthData.data[offsetBegining] + depthData.data[offsetBegining+1] + depthData.data[offsetBegining+2] + depthData.data[offsetBegining+3])
	#print "distanceBegining: %f" % distBegin

	(distEnd,) = unpack('f', depthData.data[offsetEnd] + depthData.data[offsetEnd+1] + depthData.data[offsetEnd+2] + depthData.data[offsetEnd+3])
	#print "distangeEnd: %f" % distEnd

	distDiff = distBegin - distEnd
	distAbs = math.fabs(distDiff)
	# this is the treshold of difference between the left and right side distances.
	distanceThresh = 0.2

	# if the distance is large, we need to check which is larger and then move accordingly.
	if (distAbs > distanceThresh):
		# we might need a nan before we get in here
		print("The difference is: " + str(distAbs))

	

if __name__ == '__main__':
    main()
