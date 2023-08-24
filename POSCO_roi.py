import zed
import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm

THRESHOLD = 240

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2 or args[1] not in ['mini', '2i']:
        print("Usage: python POSCO_get_image.py mini (or 2i)")
        exit(0)
    cam_model = args[1] # cam_model: 2i or mini
    cam = zed.ZEDCamera(model=cam_model)
    left, right = cam.get_image()
    cv2.imshow("left", left)
    cv2.setMouseCallback("left", cam.mouse_click_callback)
    key = cv2.waitKey(1)
    while key != ord('q'):
        left, right = cam.get_image()
        cv2.imshow("left", left)
        key = cv2.waitKey(1)

    cam.cam_close()