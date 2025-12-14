from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import cv2
import numpy as np
import math
import sys

# 設定要偵測的 ArUco 字典
ARUCO_DICT_TYPE = cv2.aruco.DICT_4X4_50
# 設定標籤的實際邊長 (單位: 公分)
MARKER_SIZE = 5.0 

def get_approx_camera_matrix(width, height):
    center_x = width / 2.0
    center_y = height / 2.0
    focal_length = width 
    camera_matrix = np.array([
        [focal_length, 0, center_x],
        [0, focal_length, center_y],
        [0, 0, 1]
    ], dtype="double")
    dist_coeffs = np.zeros((4, 1))
    return camera_matrix, dist_coeffs

def euler_from_rvec(rvec):
    rmat, _ = cv2.Rodrigues(rvec)
    sy = math.sqrt(rmat[0, 0] * rmat[0, 0] + rmat[1, 0] * rmat[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(rmat[2, 1], rmat[2, 2])
        y = math.atan2(-rmat[2, 0], sy)
        z = math.atan2(rmat[1, 0], rmat[0, 0])
    else:
        x = math.atan2(-rmat[1, 2], rmat[1, 1])
        y = math.atan2(-rmat[2, 0], sy)
        z = 0
    return np.degrees(x), np.degrees(y), np.degrees(z)

def main():
    print("camera on...")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 2. 初始化 ArUco 字典
    aruco_dict = cv2.aruco.Dictionary_get(ARUCO_DICT_TYPE)
    parameters = cv2.aruco.DetectorParameters_create()

    # 3. 定義標記的 3D 世界座標
    half = MARKER_SIZE / 2.0
    obj_points = np.array([
        [-half, half, 0],
        [half, half, 0],
        [half, -half, 0],
        [-half, -half, 0]
    ], dtype=np.float32)

    print("press q to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取畫面")
            break

        h, w = frame.shape[:2]
        cam_matrix, dist_coeffs = get_approx_camera_matrix(w, h)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for i in range(len(ids)):
                marker_corners = corners[i][0]
                
                # SolvePnP
                success, rvec, tvec = cv2.solvePnP(obj_points, marker_corners, cam_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

                if success:
                    if hasattr(cv2, 'drawFrameAxes'):
                        cv2.drawFrameAxes(frame, cam_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
                    else:
                        cv2.aruco.drawAxis(frame, cam_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
                    
                    pitch, yaw, roll = euler_from_rvec(rvec)

                    if i == 0:
                        info = f"ID:{ids[i][0]} P:{pitch:.1f} Y:{yaw:.1f} R:{roll:.1f}"
                        cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
                        cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        sys.stdout.write(f"\rID: {ids[i][0]} | P: {pitch:.1f}, Y: {yaw:.1f}, R: {roll:.1f}   ")
                        sys.stdout.flush()

        cv2.imshow('ArUco Pose Estimation', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()