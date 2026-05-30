from Transformations import *
from math import cos, sin, pi, atan
import numpy as np

def rotation_matrix_x(alpha):
    c = cos(alpha * pi/180)
    s = sin(alpha * pi/180)
    matrix = np.array([[1, 0, 0],
                       [0, c,-s],
                       [0, s, c]])
    return matrix

def rotation_matrix_y(alpha):
    c = cos(alpha * pi/180)
    s = sin(alpha * pi/180)
    matrix = np.array([[ c, 0, s],
                       [ 0, 1, 0],
                       [-s, 0, c]])
    return matrix

def rotation_matrix_z(alpha):
    c = cos(alpha * pi/180)
    s = sin(alpha * pi/180)
    matrix = np.array([[c,-s, 0],
                       [s, c, 0],
                       [0, 0, 1]])
    return matrix

def rotation_matrix(alpha ,axis):
    if axis == 'x':
        return rotation_matrix_x(alpha)
    if axis == 'y':
        return rotation_matrix_y(alpha)
    if axis == 'z':
        return rotation_matrix_z(alpha)


def update_scale(poinst1, poinst2):
    valu1 = poinst1[0].RPos_y - poinst1[1].RPos_y
    valu2 = poinst2[0].RPos_y - poinst2[1].RPos_y
    if abs(valu1) < 1 or abs(valu2) < 1:
        return 1
    return valu1/valu2

def update_rpos(ImgPos_array_X, ImgPos_array_Y, cam, size):
    Rpos = [[0],[0],[0],[0]]
    for i in range(4):
        new_point = point()
        new_point.Cvt2RPos(ImgPos_array_X[i],ImgPos_array_Y[i], cam, size)
        Rpos[i] = new_point
    return Rpos

def Get_Joint_Position(ImgPos_array_X1, ImgPos_array_Y1, ImgPos_array_X2,ImgPos_array_Y2, size):
    Rpos1 = [[0],[0],[0],[0]]
    Rpos2 = [[0],[0],[0],[0]]
    Positions = [[0],[0],[0],[0]]

    Rpos1 = update_rpos(ImgPos_array_X1, ImgPos_array_Y1, 0, size)
    Rpos2 = update_rpos(ImgPos_array_X2, ImgPos_array_Y2, 1, size)
    Scale = update_scale(Rpos1, Rpos2)

    for i in range(4):
        tmp = position()
        tmp.relative_to(Rpos1[i],Rpos2[i], Scale)
        Positions[i] = tmp
    return Positions, Scale

def Get_Joint_Angle(Vetor_d, Vetor_k,):
    if Vetor_k > 0 and Vetor_d >= 0:
        return atan(Vetor_d/Vetor_k) * (180/pi)
    elif Vetor_k < 0:
        return 90
    elif Vetor_d < 0:
        return 0
    return 0

def Get_Joint_Angles(Positions):
    print('===================')
    Vetor_R0 = Vetor()
    Vetor_R0.cvt2Vetor(Positions[1], Positions[2])

    alpha_1 = Get_Joint_Angle(Vetor_R0.Vetor_z, Vetor_R0.Vetor_y)

    pos = np.array(Vetor_R0.Vector2Array())
    Rot_V1_2 = rotation_matrix_x(-1 * alpha_1) @ pos

    Vetor_R1 = Vetor()
    Vetor_R1.Array2Vector(Rot_V1_2.reshape(-1, 1))

    alpha_2 = Get_Joint_Angle(Vetor_R1.Vetor_x, Vetor_R1.Vetor_y)
    print(Vetor_R1.Vetor_z)

    return [alpha_1, alpha_2]

