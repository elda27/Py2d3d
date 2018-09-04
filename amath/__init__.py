import numpy as np
import math
from math import cos, sin


def deg2rad(deg):
    return deg * math.pi / 180.0


def rad2deg(rad):
    return rad / math.pi * 180.0


def rotx(t):
    ct = cos(t)
    st = sin(t)
    return np.array([[1,  0,    0],
                     [0,  ct, -st],
                     [0,  st,  ct]], dtype=np.float32)


def roty(t):
    ct = cos(t)
    st = sin(t)

    return np.array([[ct,   0,   st],
                     [0,    1,    0],
                     [-st,  0,   ct]], dtype=np.float32)


def rotz(t):
    ct = cos(t)
    st = sin(t)

    return np.array([[ct,      -st,  0],
                     [st,       ct,  0],
                     [0,    0,  1]], dtype=np.float32)


def concatenate4x4(*matrix_Nx4x4):

    matrix = np.identity(4)
    for m in matrix_Nx4x4:
        matrix = np.matmul(matrix, m)
    return matrix


def constructProjectionMatrix(intrinsic_Nx4x4, extrinsic_Nx4x4):

    ndim = intrinsic_Nx4x4.ndim

    if ndim == 3 and intrinsic_Nx4x4.shape[1:] == (3, 3):
        N = intrinsic_Nx4x4.shape[0]
        matrix = np.zeros((N, 3, 4))
        matrix[:, :3, :3] = intrinsic_Nx4x4
    elif ndim == 2 and intrinsic_Nx4x4.shape == (3, 3):
        matrix = np.zeros((3, 4))
        matrix[:3, :3] = intrinsic_Nx4x4
    else:
        raise ValueError('unexpected shape')

    matrix = np.matmul(matrix, extrinsic_Nx4x4)
    return matrix


def constructProjectionParameter(pm_Nx3x4, image_size, T_Nx4x4=np.eye(4)):

    # check pm_Nx3x4
    ndim = pm_Nx3x4.ndim
    if ndim == 3 and pm_Nx3x4.shape[1:] == (3, 4):
        pass
    elif ndim == 2 and pm_Nx3x4.shape == (3, 4):
        pm_Nx3x4 = np.expand_dims(pm_Nx3x4, axis=0)
    else:
        raise ValueError('unexpected shape')

    N = pm_Nx3x4.shape[0]

    # check T_Nx4x4
    ndim = T_Nx4x4.ndim
    if ndim == 3 and T_Nx4x4.shape[1:] == (4, 4):
        if T_Nx4x4.shape[0] == N:
            pass
        elif T_Nx4x4.shape[0] != 1 and N == 1:
            N = T_Nx4x4.shape[0]
            pm_Nx3x4 = np.repeat(pm_Nx3x4, N, axis=0)
        elif T_Nx4x4.shape[0] == 1 and N != 1:
            T_Nx4x4 = np.repeat(T_Nx4x4, N, axis=0)
        else:
            raise ValueError('unexpected shape')
    elif ndim == 2 and T_Nx4x4.shape == (4, 4):
        T_Nx4x4 = np.expand_dims(T_Nx4x4, axis=0)
        T_Nx4x4 = np.repeat(T_Nx4x4, N, axis=0)
    else:
        raise ValueError('unexpected shape')

    # check image_size
    if isinstance(image_size, list):
        image_size = np.array(image_size)

    ndim = image_size.ndim
    if ndim == 2 and image_size.shape[1] == (2):
        pass
    elif ndim == 1 and image_size.shape[0] == (2):
        image_size = np.expand_dims(image_size, axis=0)
    else:
        raise ValueError('unexpected shape')

    if N != image_size.shape[0] and 1 != image_size.shape[0]:
        raise ValueError('unexpected shape')

    # run construction
    p_Nx12 = np.zeros((N, 12))

    pm_Nx3x4 = np.matmul(pm_Nx3x4, T_Nx4x4)
    rot_Nx3x3 = pm_Nx3x4[:, :3, :3]
    inv_rot_Nx3x3 = np.zeros_like(rot_Nx3x3)
    for i in range(N):
        inv_rot_Nx3x3[i, :, :] = np.linalg.inv(rot_Nx3x3[i, :, :])

    ray_s = pm_Nx3x4[:, :, 3]
    ray_s = np.expand_dims(ray_s, axis=2)
    ray_s = np.matmul(inv_rot_Nx3x3, ray_s)
    ray_s *= -1

    p_Nx12[:, :3] = inv_rot_Nx3x3[:, :, 2]
    p_Nx12[:, 3:6] = inv_rot_Nx3x3[:, :, 0] * np.float32(image_size[:, 0])
    p_Nx12[:, 6:9] = inv_rot_Nx3x3[:, :, 1] * np.float32(image_size[:, 1])
    p_Nx12[:, 9:] = ray_s[:, :, 0]

    return p_Nx12


def convertTransRotTo4x4(transrot_Nx6, is_radians=False):

    if isinstance(transrot_Nx6, list):
        transrot_Nx6 = np.array(transrot_Nx6)

    ndim = transrot_Nx6.ndim

    if ndim == 2 and transrot_Nx6.shape[1] == 6:
        pass
    elif ndim == 1 and transrot_Nx6.shape[0] == 6:
        transrot_Nx6 = np.expand_dims(transrot_Nx6, axis=0)
    else:
        raise ValueError(
            'unexpected shape: ndim is 1 or 2 and first or second shape is 6. Actual:{}'.format(transrot_Nx6))

    N = transrot_Nx6.shape[0]

    angle_rad = transrot_Nx6[:, 3:]
    if not is_radians:
        angle_rad = (np.pi/180.0) * angle_rad

    cos_Nx3 = np.cos(angle_rad)
    sin_Nx3 = np.sin(angle_rad)

    matrix_Nx4x4 = np.zeros((N, 4, 4))
    matrix_Nx4x4[:, 0, 0] = cos_Nx3[:, 1] * cos_Nx3[:, 2]
    matrix_Nx4x4[:, 0, 1] = -cos_Nx3[:, 0] * sin_Nx3[:, 2] + \
        sin_Nx3[:, 0] * sin_Nx3[:, 1] * cos_Nx3[:, 2]
    matrix_Nx4x4[:, 0, 2] = sin_Nx3[:, 0] * sin_Nx3[:, 2] + \
        cos_Nx3[:, 0] * sin_Nx3[:, 1] * cos_Nx3[:, 2]
    matrix_Nx4x4[:, 0, 3] = transrot_Nx6[:, 0]
    matrix_Nx4x4[:, 1, 0] = cos_Nx3[:, 1] * sin_Nx3[:, 2]
    matrix_Nx4x4[:, 1, 1] = cos_Nx3[:, 0] * cos_Nx3[:, 2] + \
        sin_Nx3[:, 0] * sin_Nx3[:, 1] * sin_Nx3[:, 2]
    matrix_Nx4x4[:, 1, 2] = -sin_Nx3[:, 0] * cos_Nx3[:, 2] + \
        cos_Nx3[:, 0] * sin_Nx3[:, 1] * sin_Nx3[:, 2]
    matrix_Nx4x4[:, 1, 3] = transrot_Nx6[:, 1]
    matrix_Nx4x4[:, 2, 0] = -sin_Nx3[:, 1]
    matrix_Nx4x4[:, 2, 1] = sin_Nx3[:, 0] * cos_Nx3[:, 1]
    matrix_Nx4x4[:, 2, 2] = cos_Nx3[:, 0] * cos_Nx3[:, 1]
    matrix_Nx4x4[:, 2, 3] = transrot_Nx6[:, 2]
    matrix_Nx4x4[:, 3, 3] = np.ones((N,))

    if ndim == 1:
        matrix_Nx4x4 = matrix_Nx4x4[0]

    return matrix_Nx4x4


def convert4x4ToTransRot(matrix_Nx4x4, is_radians=False, eps=np.finfo(float).eps):

    ndim = matrix_Nx4x4.ndim

    if ndim == 3 and matrix_Nx4x4.shape[1:] == (4, 4):
        pass
    elif ndim == 2 and matrix_Nx4x4.shape == (4, 4):
        matrix_Nx4x4 = np.expand_dims(matrix_Nx4x4, axis=0)
    else:
        raise ValueError('unexpected shape')

    R_Nx3x3 = matrix_Nx4x4[:, :3, :3]
    rot_Nx3 = convertRot3x3ToRPY(R_Nx3x3, is_radians=is_radians, eps=eps)
    trans_Nx3 = matrix_Nx4x4[:, :3, 3]

    transrot_Nx6 = np.concatenate((trans_Nx3, rot_Nx3), axis=1)

    if ndim == 2:
        transrot_Nx6 = transrot_Nx6[0]

    return transrot_Nx6


def convertRot3x3ToRPY(R_Nx3x3, is_radians=False, eps=np.finfo(float).eps):

    ndim = R_Nx3x3.ndim

    if ndim == 3 and R_Nx3x3.shape[1:] == (3, 3):
        pass
    elif ndim == 2 and R_Nx3x3.shape == (3, 3):
        R_Nx3x3 = np.expand_dims(R_Nx3x3, axis=0)
    else:
        raise ValueError('unexpected shape')

    N = R_Nx3x3.shape[0]
    R_Nx9 = np.reshape(R_Nx3x3, (N, 9), order='C')

    pitch = np.arctan2(-R_Nx9[:, 6],
                       np.sqrt(np.power(R_Nx9[:, 0], 2*np.ones(N,)) + np.power(R_Nx9[:, 3], 2*np.ones(N,))))

    yaw = np.zeros((N,))
    roll = np.zeros((N,))

    index = np.abs(pitch - np.pi/2.0) < eps
    roll[index] = np.arctan2(R_Nx9[index, 1], R_Nx9[index, 4])

    index = np.abs(pitch + np.pi/2.0) < eps
    roll[index] = -np.arctan2(R_Nx9[index, 1], R_Nx9[index, 4])

    index = np.logical_and(np.abs(pitch - np.pi/2.0) >= eps,
                           np.abs(pitch + np.pi/2.0) >= eps)
    yaw[index] = np.arctan2(R_Nx9[index, 3]/np.cos(pitch[index]),
                            R_Nx9[index, 0]/np.cos(pitch[index]))
    roll[index] = np.arctan2(R_Nx9[index, 7]/np.cos(pitch[index]),
                             R_Nx9[index, 8]/np.cos(pitch[index]))

    roll = np.expand_dims(roll,  axis=1)
    pitch = np.expand_dims(pitch, axis=1)
    yaw = np.expand_dims(yaw,   axis=1)

    rot_Nx3 = np.concatenate((roll, pitch, yaw), axis=1)
    if not is_radians:
        rot_Nx3 = 180.0/np.pi * rot_Nx3

    if ndim == 2:
        rot_Nx3 = rot_Nx3[0]

    return rot_Nx3


def matTranslation(vector):
    assert len(vector) == 3
    e = np.eye(4)
    e[3, 0:3] = vector
    return e
