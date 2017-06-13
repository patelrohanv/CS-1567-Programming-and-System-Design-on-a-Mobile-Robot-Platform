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

# x = 0, z = 0.9 makes it turn linear.
# x = 0.2, z = 0.9, makes it turn and move forward
# 

	command.linear.x = -0.3
	#im using command.linear.y as our "desired distance" variable that is passed in.
#	command.linear.y = 0.5
#	command.angular.y = 85.0
#	command.angular.z = 0.9
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
	mode = ''
#while(mode != '!q'):
#  mode = input('Select Mode (1 for single, 2 for multiple, \':q\' to quit): ')
#  if(mode == 1):
#    command = input('Enter a command and press Enter to execute: ')
    #split input into direction, angle, and distance
#    commands = command.split()
#    direction = commands[0]
#    distance = commands[1]
#    angle = commands[2]
    #call method with params
#  if (mode == 2):
#    print("Enter \':q\' to quit")
#    command = ''
#    i = 0
#    matrix[0][0] = ''
#    while (command != ':q'):
#      command = input('Enter a command or \':q\' to quit: ')
      #split input into direction, angle, and distance
#      commands = command.split()
#      matrix[i][0] = commands[0]
#      matrix[i][1] = commands[1]
#      matrix[i][2] = commands[2]
#      i += 1
    #call method with params
forward()
