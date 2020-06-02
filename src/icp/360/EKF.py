#!/usr/bin/env python

import sys
import rospy
from sensor_msgs.msg import PointCloud
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
import numpy as np
from scipy.spatial import KDTree
import random
import matplotlib.pyplot as plt

from class_icp import Align2D
from class_retrive_data import retrive_data


class EKF(object):

    def __init__(self, u_t_1, u_t):




        self.u_t_1  = np.array([[u_t_1[0,2]],
                                [u_t_1[1,2]],
                                [np.arccos(u_t_1[0,0])]])

        self.u_t    =  np.array([[u_t[0,2]],
                                 [u_t[1,2]],
                                 [np.arccos(u_t[0,0])]])


        self.sig        = 50*np.eye(3)
        self.mu         = np.array([0.,0.,0.])

        self.mu_bar     = []
        self.sig_bar    = np.array([[0,0,0]])

        self.C          = np.eye(3)     # obersavtion model
        self.R          = 50*np.eye(3)     # noise of the motion
        self.Q          = 50*np.eye(3)     # noise of the observation







    def prediction(self):


        delta_x     = np.squeeze(self.u_t_1[0] - self.u_t[0])
        delta_y     = np.squeeze(self.u_t_1[1] - self.u_t[1])
        delta_theta = np.squeeze(self.u_t_1[2] - self.u_t[2])


        A = np.eye(3)

        B = np.array([[-np.cos(self.u_t[2][0]), np.sin(self.u_t[2][0]),0],
                      [np.sin(self.u_t[2][0]) , np.cos(self.u_t[2][0]),0],
                      [0,0,1]])

        self.mu_bar     = self.u_t_1
        #self.mu_bar     = np.dot(A,self.u_t_1) + np.dot(B,self.u_t)
        self.sig_bar    = np.dot(np.dot(A,self.sig),A.T) + self.R
        #print(self.sig_bar)







    def correction(self,observation):

        z  = np.array([[observation[0,2]],
                      [observation[1,2]],
                      [np.arccos(observation[0,0])]])




        K          = np.dot(self.sig_bar,np.dot(self.C.T,np.linalg.inv(np.dot(np.dot(self.C,self.sig_bar),self.C.T) + self.Q)))
        #print(self.mu)

        self.mu    = self.mu_bar + np.dot(K,(z - np.dot(self.C,self.mu_bar)))

        #self.sig   = (np.eye(3) - K * self.C)* self.sig_bar
        #print(self.mu_bar)
        print(self.mu)






if __name__ == '__main__':

    rospy.init_node('EKF', anonymous=True) 	# initiate the node

    data = retrive_data()   # create the class to retrive the data

    rospy.sleep(5)          # wait for the topics to be initialized





    while not rospy.is_shutdown():

        T       = data.initial_guess()      # initial guess of the transform
        source  = data.return_source_pc()   # PointCloud of the source scan
        target  = data.return_target_pc()   # PointCloud of the target scan

        #print(source)
        #print(source)


        ICP = Align2D(source,target,T)      # create object for ICP algo

        T_corrected = ICP.transform         # retrive the right transform matrix

        #del ICP                             # delete the object

        init_T = np.array([[0,1,0],
                           [1,0,0],
                           [0,0,1]])

        #print(T_corrected)
        #print(" ")
        #print(init_T)
        ekf = EKF(init_T,T)
        ekf.prediction()
        ekf.correction(T_corrected)
        #print("ok so far !")
