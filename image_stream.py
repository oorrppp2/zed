import zed
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import time

THRESHOLD = 240

def make_mask(img):
    mask = np.zeros((img.shape[0], img.shape[1]))
    mask[img < THRESHOLD] = 255
    mask = mask.astype(np.uint8)
    return mask

if __name__ == "__main__":
    zed_2i = zed.ZEDCamera(camera_id=0)
    # zed_mini = zed.ZEDCamera(camera_id=1)
    # cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        left_2i, right_2i = zed_2i.get_image()
        _2i = cv2.hconcat([left_2i, right_2i])
        # left_mini, right_mini = zed_mini.get_image()
        # _mini = cv2.hconcat([left_mini, right_mini])
        cv2.imshow("zed_2i", _2i)
        # key = cv2.waitKey(1)
        # time.sleep(0.01)
        # cv2.imshow("zed_mini", _mini)
        key = cv2.waitKey(1)

        if key == ord('q'):
            break
    zed_2i.cam_close()
    # zed_mini.cam_close()