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
        command.angular.z = 0
        pub.publish(command)

def forward(one, two, three):
	rospy.init_node('forward', anonymous=True)
	rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, bumperCallback)

	while pub.get_num_connections() == 0:
		#print ("zero connections")
		pass
	if(one.lower() == "f"):
		command.linear.x = float(two)
		command.linear.y = float(three)
		command.angular.z = 0.0
		command.angular.y = 0.0
	elif(one.lower() == "b"):
		command.linear.x = float(two) * -1
		command.linear.y = float(three) * -1
		command.angular.z = 0.0
		command.angular.y = 0.0
	elif(one.lower() == "r"):
		command.angular.z = float(two)
		command.angular.y = float(three) - 5.0
		command.linear.x = 0.0
		command.linear.y = 0.0
	elif(one.lower() == "l"):
		command.angular.z = float(two) * -1
		command.angular.y = (float(three) * -1) + 5.0
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
	mode = ''
	while(mode != '!q'):
		mode = input('Select Mode (1 for single, 2 for multiple, \':q\' to quit): ')
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
			matrix = [[],[]]
			cmd = raw_input('Enter a series of commands and press Enter to execute: ')
			c = cmd.split(', ')
			for j in c:
				commands = j.split()
				print commands
				matrix[i][0] = commands[0]
				matrix[i][1] = commands[1]
				matrix[i][2] = commands[2]
				i += 1
			#call method with params
			for x in range (0, len(matrix)):
				forward(matrix[x][0], matrix[x][1], matrix[x][2])
		elif(mode != '!q'):
			print("Not a valid command")
			continue
