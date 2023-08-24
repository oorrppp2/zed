import zed
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import time

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2 or args[1] not in ['mini', '2i']:
        print("Usage: python POSCO_get_image.py mini (or 2i)")
        exit(0)
    cam_model = args[1] # cam_model: 2i or mini
    cam = zed.ZEDCamera(model=cam_model)
    cam.set_camera_setting(cam.EXPOSURE, 0)
    cam.set_camera_setting(cam.GAIN, 0)
    # cv2.waitKey(1000)
    time.sleep(5)
    for i in tqdm(range(40,60)):
        for j in range(40,60):
    # for i in tqdm(range(100)):
        # for j in range(100):
            cam.set_camera_setting(cam.EXPOSURE, i)
            cam.set_camera_setting(cam.GAIN, j)
            time.sleep(0.05)
            left, right = cam.get_image()

            exposure = cam.cam.get_camera_settings(cam.EXPOSURE)
            gain = cam.cam.get_camera_settings(cam.GAIN)

            cv2.imwrite('./images_zed{0}/img_left_exp{1}_gain{2}.png'.format(cam_model, exposure[-1], gain[-1]), left)
            cv2.imwrite('./images_zed{0}/img_right_exp{1}_gain{2}.png'.format(cam_model, exposure[-1], gain[-1]), right)

    cam.cam_close()