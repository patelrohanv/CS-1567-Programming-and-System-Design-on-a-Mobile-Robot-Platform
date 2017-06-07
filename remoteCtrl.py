#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

pub = rospy.Publisher("kobuki_command", Twist, queue_size=10)
command = Twist()

def joystickCallback(data):
    global pub, command
    print data.buttons[0]
    print data.axes[0]
    print data.axes[1]
    
    negativeBrake = -0.5
    positiveBrake = 0.5
    if data.buttons[8] == 1:
	rospy.signal_shutdown("emergency stop!")
    if data.buttons[2] == 1:
	command.linear.x = 0.0
	command.angular.z = 0.0
    else:
	
    	if data.buttons[1] == 1 and (data.axes[1] <= -0.1 or data.axes[1] >= 0.1):
    		if data.axes[1] >= 0.8:
			#command.linear.x = 0.3
			if positiveBrake == 0.1:
				command.linear.x = 0.0123
			else:
				positiveBrake -= 0.1
				command.linear.x = 0

    		elif data.axes[1] <= -0.8:
			#command.linear.x = -0.3
			if negativeBrake == 0.1:
				command.linear.x = -0.0123
			else:
				negativeBrake += 0.1
				command.linear.x = 0
	else:
		if data.axes[1] >= 0.8:
			command.linear.x = 0.8
    		else:
			command.linear.x = data.axes[1]

    		if data.axes[1] <= -0.8:
			command.linear.x = -0.8
    		else:
			command.linear.x = data.axes[1]


    command.angular.z = data.axes[0]

    pub.publish(command)

def cleanUp():
    global pub, command
    command.linear.x = 0.0
    command.angular.z = 0.0
    pub.publish(command)
    rospy.sleep(1)

def remoteController():
    rospy.init_node("remoteControl", anonymous=True)
    rospy.Subscriber("joy", Joy, joystickCallback)
    rospy.on_shutdown(cleanUp)

    #while pub.get_num_connections() == 0:
    #    pass

    rospy.spin()

if __name__ == '__main__':
    remoteController()
