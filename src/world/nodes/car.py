#!/usr/bin/env python
from __future__ import division

import roslib; roslib.load_manifest('world')
import rospy as rp

import numpy as np

import sys

import random
import math

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class CarNode:
  def __init__(self, name, model):
    self.cbMotor = rp.Subscriber('/{}/velocity'.format(name), Twist, self.motorCallback, queue_size = 1)
    self.pbMotor = rp.Publisher('/robot_{}/cmd_vel'.format(model), Twist, queue_size = 1)
    self.cbLaser = rp.Subscriber('/robot_{}/base_scan'.format(model), LaserScan, self.laserCallback, queue_size = 1)
    self.pbLaser = rp.Publisher('/{}/scan'.format(name), LaserScan, queue_size = 1)

    self.motorNoise = rp.get_param('/motor_noise')
    self.laserNoise = rp.get_param('/laser_noise')

    rp.spin()

  def laserCallback(self, msg):
    tmp = list(msg.ranges)

    for ii in range(len(tmp)):
      if tmp[ii] < 5.0:
        tmp[ii] = random.gauss(tmp[ii], self.laserNoise)

    msg.ranges = tmp
    
    self.pbLaser.publish(msg)

  def motorCallback(self, msg):
    sp = msg.linear.x
    sp = sp if sp < 4.0 else 4.0

    tu = msg.angular.z
    tu = tu if tu < 6.28 else 6.28

    msg.linear.x = random.gauss(sp, math.sqrt(tu*tu + sp*sp) / 6.0)
    msg.linear.y = 0
    msg.linear.z = 0

    msg.angular.x = 0
    msg.angular.y = 0
    msg.angular.z = random.gauss(tu, math.sqrt(tu*tu + sp*sp) / 6.0)

    self.pbMotor.publish(msg)

if __name__ == '__main__':
  
  if len(sys.argv) < 3:
    raise RuntimeException('Need to provide an ID and name for CarNode')
  else:

    name = sys.argv[1]
    model = int(sys.argv[2])

  rp.init_node(name)

  try:
    car = CarNode(name, model)
  except rp.ROSInterruptException:
    pass
