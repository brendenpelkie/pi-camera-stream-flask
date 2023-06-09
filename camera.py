#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..

import cv2 as cv
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import io
import numpy as np
from threading import Condition
import time


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

    def read(self, buff_size = -1):
        # takes buffer size to work with readers but just ignores it
        with self.condition:
            self.condition.wait()
            frame = self.frame
            return frame


class VideoCamera(object):
    def __init__(self):
        cam = Picamera2()
        video_config = cam.create_video_configuration(main = {"size":(600,600)})
        cam.configure(video_config)
                
        encoder = JpegEncoder()
        buff = StreamingOutput()
        output = FileOutput(buff)
        encoder.output = output
        cam.encoder = encoder

        self.cam = cam
        self.buff = buff
        cam.start_encoder()
        cam.start()
        
        time.sleep(2.0)

    def __del__(self):
        self.cam.stop()
        self.cam.stop_encoder()


    def draw_grid(self, frame):
        np_frame = np.fromstring(frame, np.uint8)
        img = cv.imdecode(np_frame, cv.IMREAD_COLOR)
    
        img[:, 300] = [0, 0, 0]
        img[300, :] = [0, 0, 0]
        cv.circle(img, (300, 300), 50, (0, 0, 0), 2)

        return cv.imencode('.jpg', img)[1].tobytes()


    def get_frame(self):
        img = self.buff.read()
        return self.draw_grid(img)
        

    # Take a photo, called by camera button
    def take_picture(self):
        pass



