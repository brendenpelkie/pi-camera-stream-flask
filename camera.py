#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..

import cv2 as cv
#from imutils.video.pivideostream import PiVideoStream
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
import io
from picamera2.outputs import FileOutput
import imutils
import time
from datetime import datetime
import numpy as np
from threading import Condition


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

    def read(self):
        with self.condition:
            self.condition.wait()
            frame = self.frame
            #self.condition.notify_all()
            return frame


class VideoCamera(object):
    def __init__(self, flip = False, file_type  = ".jpg", photo_string= "stream_photo"):
        # self.vs = PiVideoStream(resolution=(1920, 1080), framerate=30).start()
        #self.vs = PiVideoStream().start()
        cam = Picamera2()
        video_config = cam.create_video_configuration(main = {"size":(600,600)})
        cam.configure(video_config)
        #cam.video_configuration.controls.FrameRate = 30
        
        encoder = JpegEncoder()
        buff = StreamingOutput() #io.BytesIO()
        output = FileOutput(buff)
        encoder.output = output

        cam.encoder = encoder
            
        self.cam = cam
        self.buff = buff
        cam.start_encoder()
        cam.start()
        self.flip = flip # Flip frame vertically
        self.file_type = file_type # image type i.e. .jpg
        self.photo_string = photo_string # Name to save the photo
        time.sleep(2.0)
        print('init complete')

    def __del__(self):
        self.cam.stop()
        self.cam.stop_encoder()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        #frame = self.flip_if_needed(self.vs.read())
        #ret, jpeg = cv.imencode(self.file_type, frame)
        #self.previous_frame = jpeg
        return self.buff.read() #getvalue()# jpeg.tobytes()

    # Take a photo, called by camera button
    def take_picture(self):
        frame = self.buff.read()
        ret, image = cv.imencode(self.file_type, frame)
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S") # get current time
        cv.imwrite(str(self.photo_string + "_" + today_date + self.file_type), frame)



