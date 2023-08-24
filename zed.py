import cv2
import os
import pyzed.sl as sl
import numpy as np
import matplotlib.pyplot as plt
import time

class ZEDCamera():
    def __init__(self, model='2i'):
        print("Initializing...")
        init = sl.InitParameters()
        for i in range(2):
            init.set_from_camera_id(i)
            init.camera_resolution = sl.RESOLUTION.HD1080
            # init.camera_resolution = sl.RESOLUTION.HD720
            self.cam = sl.Camera()
            if not self.cam.is_opened():
                print("Opening ZED Camera...")
            status = self.cam.open(init)
            if status != sl.ERROR_CODE.SUCCESS:
                print(repr(status))
                exit()

            self.camera_information = self.cam.get_camera_information()
            self.cam_model = str(self.camera_information.camera_model).rstrip()
            if model == '2i' and self.cam_model == 'ZED 2i':
                print("Start ZED 2i")
                break
            elif model == 'mini' and self.cam_model == 'ZED-M':
                print("Start ZED mini")
                break

            self.cam_close()

        self.runtime = sl.RuntimeParameters()
        
        self.save_folder = './roi_images'
        file_list = os.listdir(self.save_folder)
        index_set = set([])
        if len(file_list) > 0:
            for fn in file_list:
                index_set.add(int(fn.split('.')[0].split('_')[-1]))
            print(index_set)
            self.start_index = sorted(index_set)[-1]+1
        else:
            self.start_index = 0
        self.click_count = 0

        # for ZED SDK < 4.0
        # image_size = self.cam.get_camera_information().camera_resolution

        # for ZED SDK > 4.0
        image_size = self.camera_information.camera_configuration.resolution
        self.W, self.H = image_size.width, image_size.height
        self.roi = sl.Rect()
        self.select_in_progress = False
        self.origin_rect = (-1,-1 )

        self.mat_left = sl.Mat(self.W, self.H)
        self.mat_right = sl.Mat(self.W, self.H)

        self.BRIGHTNESS = sl.VIDEO_SETTINGS.BRIGHTNESS
        self.CONTRAST = sl.VIDEO_SETTINGS.CONTRAST
        self.EXPOSURE = sl.VIDEO_SETTINGS.EXPOSURE
        self.GAIN = sl.VIDEO_SETTINGS.GAIN
        self.GAMMA = sl.VIDEO_SETTINGS.GAMMA
        self.HUE = sl.VIDEO_SETTINGS.HUE
        self.SATURATION = sl.VIDEO_SETTINGS.SATURATION
        self.SHARPNESS = sl.VIDEO_SETTINGS.SHARPNESS
        self.WHITEBALANCE_TEMPERATURE = sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE
        self.SETTINGS = [self.BRIGHTNESS, self.CONTRAST, self.EXPOSURE, self.GAIN, self.GAMMA,
                         self.HUE, self.SATURATION, self.SHARPNESS, self.WHITEBALANCE_TEMPERATURE]

        
        self.init_camera_parameter()
        # time.sleep(5)
        # self.fix_camera_parameter()
        # time.sleep(5)

    def init_camera_parameter(self):
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.GAMMA, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.HUE, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS, -1)
        self.cam.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE, -1)
        print("Camera parameters are initialized!")

    def set_camera_setting(self, setting, value):
        self.cam.set_camera_settings(setting, value)

    def fix_camera_parameter(self):
        for SETTING in self.SETTINGS:
            if SETTING == self.GAIN or SETTING == self.EXPOSURE:
                continue
            value = self.cam.get_camera_settings(SETTING)
            self.cam.set_camera_settings(SETTING, value)

    def get_image(self):
        err = self.cam.grab(self.runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            self.cam.retrieve_image(self.mat_left, sl.VIEW.LEFT)
            left_image = self.mat_left.get_data()
            self.cam.retrieve_image(self.mat_right, sl.VIEW.RIGHT)
            right_image = self.mat_right.get_data()
            return left_image, right_image
        else:
            image = np.zeros((self.W, self.H))
            return image, image
    

    # Function that handles mouse events when interacting with the OpenCV window.
    def mouse_click_callback(self, event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.origin_rect = (x, y)
            self.select_in_progress = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.select_in_progress = False
            self.set_cam_roi()

            time.sleep(3)
            # save left, right images and corresponding camera parameters
            left, right = self.get_image()
            cv2.imwrite('{0}/image_left_{1}.png'.format(self.save_folder, self.start_index), left)
            cv2.imwrite('{0}/image_right_{1}.png'.format(self.save_folder, self.start_index), right)
            roi = cv2.rectangle(left, (self.roi.x, self.roi.y), (self.roi.x+self.roi.width, self.roi.y+self.roi.height), (0,0,255,255), 2)
            cv2.imwrite('{0}/image_roi_{1}.png'.format(self.save_folder, self.start_index), roi)
            cam_param_str = ''
            for SETTING in self.SETTINGS:
                value = self.cam.get_camera_settings(SETTING)
                cam_param_str += '{0}: {1}\n'.format(SETTING, value)
            cam_param_str += 'ROI (x,y,w,h): {0}'.format((self.roi.x, self.roi.y, self.roi.width, self.roi.height))
            param_file = open('{0}/cam_param_{1}.txt'.format(self.save_folder, self.start_index), 'w')
            param_file.write(cam_param_str)
            param_file.close()
            self.start_index += 1

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.select_in_progress = False
            self.roi = sl.Rect(0,0,0,0)
            self.cam.set_camera_settings_roi(sl.VIDEO_SETTINGS.AEC_AGC_ROI,self.roi,sl.SIDE.BOTH,True)

        if self.select_in_progress:
            self.roi.x = min(x,self.origin_rect[0])
            self.roi.y = min(y,self.origin_rect[1])
            self.roi.width = abs(x-self.origin_rect[0])+1
            self.roi.height = abs(y-self.origin_rect[1])+1

    
    # def mouse_click_callback(self, event, x, y, flags, param):
    #     if event == cv2.EVENT_FLAG_LBUTTON and self.roi[0] == 0 and self.roi[1] == 0 and self.click_count == 0:
    #         self.roi[0] = x
    #         self.roi[1] = y
    #         self.click_count += 1
    #     elif event == cv2.EVENT_FLAG_LBUTTON and self.roi[0] != 0 and self.roi[1] != 0 and self.click_count == 1:
    #         self.roi[2] = x - self.roi[0]
    #         self.roi[3] = y - self.roi[1]
    #     # elif event == cv2.EVENT_FLAG_LBUTTON and not (0 in self.roi):
    #         self.set_cam_roi(self.roi)
    #         self.click_count += 1
    #     elif event == cv2.EVENT_FLAG_LBUTTON and self.click_count == 2:
    #         # save left, right images and corresponding camera parameters
    #         left, right = self.get_image()
    #         cv2.imwrite('{0}/image_left_{1}.png'.format(self.save_folder, self.start_index), left)
    #         cv2.imwrite('{0}/image_right_{1}.png'.format(self.save_folder, self.start_index), right)
    #         roi = cv2.rectangle(left, (self.roi[0], self.roi[1]), (self.roi[0]+self.roi[2], self.roi[1]+self.roi[3]), (0,0,255,255), 2)
    #         cv2.imwrite('{0}/image_roi_{1}.png'.format(self.save_folder, self.start_index), roi)
    #         cam_param_str = ''
    #         for SETTING in self.SETTINGS:
    #             value = self.cam.get_camera_settings(SETTING)
    #             cam_param_str += '{0}: {1}\n'.format(SETTING, value)
    #         cam_param_str += 'ROI (x,y,w,h): {0}'.format(self.roi)
    #         param_file = open('{0}/cam_param_{1}.txt'.format(self.save_folder, self.start_index), 'w')
    #         param_file.write(cam_param_str)
    #         param_file.close()
    #         self.roi = [0,0,0,0]
    #         self.start_index += 1
    #         self.click_count = 0
    #         print("Saved!")
    #     elif event == cv2.EVENT_FLAG_RBUTTON:
    #         self.init_camera_parameter()
    #         self.roi = [0,0,0,0]
    #         self.click_count = 0
            

    def set_cam_roi(self):   # roi = [xmin, ymin, width, height]
        # roi_rect = sl.Rect(roi[0], roi[1], roi[2], roi[3])
        self.cam.set_camera_settings_roi(sl.VIDEO_SETTINGS.AEC_AGC_ROI, self.roi, eye=sl.SIDE.BOTH)

        roi_ = sl.Rect()
        _ = self.cam.get_camera_settings_roi(sl.VIDEO_SETTINGS.AEC_AGC_ROI, roi_, sl.SIDE.BOTH)
        # time.sleep(3)
        print("Current ROI for AEC_AGC: " + str(roi_.x) + " " + str(roi_.y)+ " " + str(roi_.width) + " " + str(roi_.height))
    
    def cam_close(self):
        self.cam.close()
        print("\nFINISH")

if __name__ == "__main__":
    cam = ZEDCamera()
    img = cam.get_image()
    print(cam.cam.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC))
    print(cam.cam.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI))
    # cv2.imwrite("./data/img.png", img)
    cam.cam_close()