#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist

def forward():
	rospy.init_node('forward', anonymous=True)
	pub = rospy.Publisher('kobuki_command', Twist, queue_size=10)
	command = Twist()

	while pub.get_num_connections() == 0:
		#print ("zero connections")
		pass

	command.linear.x = 0.3
	command.angular.z = 0.0
	pub.publish(command)
	rospy.sleep(1.5)
	command.linear.x = -0.3
	command.angular.z = 0.0
	pub.publish(command)
	rospy.sleep(1.5)

if __name__== '__main__':
	forward()
