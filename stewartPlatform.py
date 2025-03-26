import math
import numpy as np

# https://www.opensimgear.org/calculators/stewart-platform/
class StewartPlatform:
    """
    Stewart Plattform class to calculate the length of each leg of the Stewart Plattform
    """
    debug = False
    base_points = []
    plattform_points = []
    r = 10 # length of 
    l = 20 # length of leg

    def __init__(self, base_radius: int, base_angle: list, plattform_radius: int, plattform_angle: list, debug: bool = False):
        """
        Initialize the Stewart Plattform with base and plattform points

        :param base_radius: radius of the base (mm)
        :param base_angle: list of angle of the base (degree)
        :param plattform_radius: radius of the plattform (mm)
        :param plattform_angle: list of angle of the plattform (degree)
        """
        
        base_points = []
        for angle in base_angle:
            angle_rad = math.radians(angle)
            Bi = [base_radius*math.cos(angle_rad), base_radius*math.sin(angle_rad), 0]
            base_points.append(Bi)
            # print("Bi: ", Bi)
        self.base_points = base_points

        plattform_points = []
        for angle in plattform_angle:
            angle_rad = math.radians(angle)
            Pi = [plattform_radius*math.cos(angle_rad), plattform_radius*math.sin(angle_rad), 0]
            plattform_points.append(Pi)
            # print("Pi: ", Pi)
        self.plattform_points = plattform_points

    def calculate(self, x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
        """
        Calculate the length of each leg of the Stewart Plattform

        :param x: translation in x direction (mm)
        :param y: translation in y direction (mm)
        :param z: translation in z direction (mm)
        :param alpha: rotation around x axis (degree)
        :param beta: rotation around y axis (degree)
        :param gamma: rotation around z axis (degree)
        :return: list of leg length\n
        """
        if (x < 0 or y < 0 or z < 0):
            print("x, y, z should be positive")
            return None
        elif (x > 200 or y > 200 or z > 200):
            print("x, y, z should be less than 200")
            return None
        elif (alpha < -45 or alpha > 45):
            print(f"alpha should be between -45 and 45 (provided: {alpha})")
            return None
        elif (beta < -45 or beta > 45):
            print(f"beta should be between -45 and 45 (provided: {beta})")
            return None
        elif (gamma < -45 or gamma > 45):
            print(f"gamma should be between -45 and 45 (provided: {gamma})")
            return None

        # Calculate translation vector
        t = [x, y, z]
        # print("translation vector: ", t)

        alpha = math.radians(alpha)
        beta = math.radians(beta)
        gamma = math.radians(gamma)

        # Calculate rotation matrix
        # roll
        Rx = np.array([[1, 0, 0], 
                       [0, math.cos(alpha), -math.sin(alpha)], 
                       [0, math.sin(alpha), math.cos(alpha)]])
        # print("Rx: \n", Rx, "\n")
        # pitch
        Ry = np.array([[math.cos(beta), 0, math.sin(beta)], 
                       [0, 1, 0], 
                       [-math.sin(beta), 0, math.cos(beta)]])
        # print("Ry: \n", Ry, "\n")
        
        # yaw
        Rz = np.array([[math.cos(gamma), -math.sin(gamma), 0], 
                       [math.sin(gamma), math.cos(gamma), 0], 
                       [0, 0, 1]])
        # print("Rz: \n", Rz, "\n")

        # R = Rz @ Ry @ Rx
        R = np.dot(Rz, np.dot(Ry, Rx))
        if self.debug:
            print("rotation matrix: \n", R, "\n")

        # transform plattform points
        Pb = []

        for i in range(6):
            Pb.append(np.dot(R, self.plattform_points[i]) + t)
        
        if self.debug:
            print("plattform points: \n", Pb, "\n")

        # calculate leg length
        v = []

        for i in range(6):
            v.append(Pb[i] - self.base_points[i])
        
        # print("vector: \n", v, "\n")
        
        # calculate leg length
        l = []
        for i in range(6):
            l.append(np.linalg.norm(v[i]))

        return l
    
    def getAngles(self, servo_arm_length: int, fix_leg_length: int, leg_length_list: list):
        """
        Calculate the servo angles based on the leg lengths

        :param servo_arm_length: length of the servo arm (mm)
        :param fix_leg_length: length of the fixed leg (mm)
        :param leg_length_list: list of leg lengths (mm)
        :return: list of servo angles (degree)
        """

        # length of servo arm
        r = servo_arm_length

        # length of fix leg length
        l = fix_leg_length
        
        # a list of all angles
        angles = []

        for L in leg_length_list:
            # Check if the leg length is within the value range
            if not (abs(r - l) <= L <= (r + l)):
                raise ValueError(f"Beinlänge {L} liegt außerhalb des zulässigen Bereichs. Erlaubt: {abs(r - l)} <= L <= {r + l}")            
            
            # Calculate cos_theta to check if value is between -1 and 1
            # cos_theta = (math.pow(r, 2) + math.pow(L, 2) - math.pow(l, 2)) / (2 * r * L)
            cos_theta = (L - math.sqrt(math.pow(l, 2) - math.pow(r, 2))) / r
            if cos_theta < -1 or cos_theta > 1:
                raise ValueError(f"Ungültiger Winkel für L={L}, r={r}, l={l}: cos_theta={cos_theta}")
            
            # Get the final degree and add it to list
            theta = math.degrees(math.asin(cos_theta))
            angles.append(theta)
        
        # return a list of all angels
        return angles
