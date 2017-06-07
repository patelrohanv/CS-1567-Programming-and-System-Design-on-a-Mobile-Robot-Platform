#!/usr/bin/env python

import rospy
import math
from std_msgs.msg import Float32

number = 0.0

def callback(data):
    global number
    while True:

	#if the number is greater than the input, subtract from it.
	if number > data.data:
		if math.fabs(data.data - number) < 0.01:
			break
		else:
			number = number - 0.01
	else:
		if math.fabs(data.data - number) < 0.01:
			break
		else:
			number = number + 0.01
	#else if the number is less than the input, add to it.

        if number == data.data:
                break
        rate = rospy.Rate(10)
        rate.sleep()
	print number
    

def listener():
    rospy.init_node("listener", anonymous=True)
    rospy.Subscriber("command", Float32, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
