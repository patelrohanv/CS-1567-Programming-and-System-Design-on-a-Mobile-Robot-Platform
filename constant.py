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
        command.linear.x = 0
        command.linear.y = 0
	command.linear.z = 1.0
        command.angular.z = 0
	command.angular.y = 0
        pub.publish(command)

def forward(one, two, three):
	command.linear.z = 0.0
	while pub.get_num_connections() == 0:
		#print ("zero connections")
		pass
	if(one.lower() == "f"):
		command.linear.x = float(two)
		command.linear.y = float(three) - 0.05
		command.angular.z = 0.0
		command.angular.y = 0.0
	elif(one.lower() == "b"):
		command.linear.x = float(two) * -1
		command.linear.y = (float(three) * -1) + 0.05
		command.angular.z = 0.0
		command.angular.y = 0.0
	elif(one.lower() == "r"):
		command.angular.z = float(two)
		command.angular.y = float(three) - 2.0
		command.linear.x = 0.0
		command.linear.y = 0.0
	elif(one.lower() == "l"):
		command.angular.z = float(two) * -1
		command.angular.y = (float(three) * -1) + 2.0
		command.linear.x = 0.0
		command.linear.y = 0.0
	pub.publish(command)
	rospy.sleep(2.0)
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
        rospy.init_node('forward', anonymous=True)
        rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)
	mode = ''
	while(mode != 3):
		mode = input('Select Mode (1 for single, 2 for multiple, 3  to quit): ')
		if(mode == 1):
			cmd = raw_input('Enter a command and press Enter to execute: ')
			#split input into direction, angle, and distance
			commands = cmd.split()
			one = commands[0]
			two = commands[1]
			three = commands[2]
			#call method with params
			forward(one, two, three)
		elif(mode == 2):
			i = 0
			cmd = raw_input('Enter a series of commands and press Enter to execute: ')
			c = cmd.split(', ')
			matrix = []
			for j in c:
				commands = j.split()
				forward(commands[0], commands[1], commands[2])
		elif(mode != 3):
			print("Not a valid command")
			continue
