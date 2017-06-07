#!/usr/bin/env python

import rospy
from kobuki_msgs.msg import Led

def sendLED():
	rospy.init_node('led_sender', anonymous=True)
	pub = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size=10)
	while pub.get_num_connections() == 0:
		pass
	led = Led()
	x = 3
	while x != -1:
		led.value = x
		pub.publish(led)
		x = x - 1
		rospy.sleep(1)

if __name__ == '__main__':
	try:
		sendLED()
	except rospy.ROSInterruptException:
		pass

