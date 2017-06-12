#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent

pub = rospy.Publisher('kobuki_command', Twist, queue_size=10)
command = Twist()

# this doesnt work right now becasue our "command" isnt 
# in a while loop waiting for commands from the user.
def bumperCallback(data):
    global pub, command
    if data.state == 1:
	print("samesame")
        command.linear.x = 0
        command.linear.y = 0
        command.angular.z = 0
        pub.publish(command)

def forward():
	rospy.init_node('forward', anonymous=True)
	rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)

	while pub.get_num_connections() == 0:
		#print ("zero connections")
		pass

	command.linear.x = 0.0
	#im using command.linear.y as our "desired distance" variable that is passed in.
	command.linear.y = 0.0
	command.angular.z = 0.9
	pub.publish(command)
#	rospy.sleep(2.0)
#	command.linear.x = -0.3
#	command.angular.z = 0.0
#	pub.publish(command)
#	rospy.sleep(2.0)
#	command.linear.x = 0.0
#	command.angular.z = 0.0
#	pub.publish(command)
#	rospy.sleep(2.0)

if __name__== '__main__':
	forward()
