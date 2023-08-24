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
    cam = zed.ZEDCamera()
    start = time.time()
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.moveWindow("Image", 2560, 0)
    cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    import time
    while True:
        left, right = img = cam.get_image()
        # elapsed_time = time.time() - start
        # min = int(elapsed_time / 60)
        # hour = int(min / 60)
        # sec = round(elapsed_time % 60, 2)
        # min = int(min % 60)
        # cv2.putText(left, "Time elapsed since streaming: {0}s".format(sec), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        # cv2.putText(left, "{0}h {1}m {2}s".format(str(hour), str(min), str(sec)), (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.imshow("Image", left)
        # cv2.imwrite("test_image.png", left)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cam.cam_close()