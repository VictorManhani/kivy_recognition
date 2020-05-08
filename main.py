__author__ = 'Victor G. Manhani'

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
Window.size = [500, 500]

import cv2
import datetime

class CamApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = {
            'eye_tree_eyeglasses': 'haarcascade_eye_tree_eyeglasses.xml',
            'eye': 'haarcascade_eye.xml',
            'frontalcatface_extended': 'haarcascade_frontalcatface_extended.xml',
            'frontalcatface': 'haarcascade_frontalcatface.xml',
            'frontalface_alt_tree': 'haarcascade_frontalface_alt_tree.xml',
            'frontalface_alt': 'haarcascade_frontalface_alt.xml',
            'frontalface_alt2': 'haarcascade_frontalface_alt2.xml',
            'frontalface_default': 'haarcascade_frontalface_default.xml',
            'fullbody': 'haarcascade_fullbody.xml',
            'lefteye_2splits': 'haarcascade_lefteye_2splits.xml',
            'licence_plate_rus_16stages': 'haarcascade_licence_plate_rus_16stages.xml',
            'lowerbody': 'haarcascade_lowerbody.xml',
            'profileface': 'haarcascade_profileface.xml',
            'righteye_2splits': 'haarcascade_righteye_2splits.xml',
            'righteye_2splits': 'haarcascade_righteye_2splits.xml',
            'russian_plate_number': 'haarcascade_russian_plate_number.xml',
            'smile': 'haarcascade_smile.xml',
            'upperbody': 'haarcascade_upperbody.xml',
            'none': None,
        }
        Clock.schedule_once(self.pre_start)

    def pre_start(self, evt):
        self.type.values = self.options.keys()

    # Initialize the detection and choose your mode
    def start(self):
        result = self.options[self.type.text]
        if result == None:
            self.evt = Clock.schedule_interval(self.update, 1.0/33.0)
        else:
            self.faceCascade = cv2.CascadeClassifier(f"hearcascade/{result}")
            self.evt = Clock.schedule_interval(self.change_recognition, 1.0/33.0)

    def build(self):
        layout = Builder.load_string("""
BoxLayout:
    orientation: 'vertical'
    Image:
        id: img
        size_hint: [1, .9]
    BoxLayout:
        size_hint: [1, .1]
	    Spinner:
            id: type
	        text: 'none'
            size_hint_x: .5
	        on_text:
	            app.stop()
                app.start()
        ToggleButton:
            id: start_pause
            text: '%s' % 'stop' if self.state == 'normal' else 'start'
            size_hint_x: .25
            on_state:
                if self.state == 'normal': app.start()
                else: app.stop()
        Button:
            text: 'take a picture'
            size_hint_x: .25
            on_release:
                app.take_picture() 
""")
        # get the interesting variable
        self.img1 = layout.ids.img
        self.type = layout.ids.type
        
        # get the video capture
        self.capture = cv2.VideoCapture(0)
        # start the capture with determined option
        self.start()
        # return root widget
        return layout

    def stop(self):
        Clock.unschedule(self.evt)

    def change_recognition(self, evt):
        ret, frame = self.capture.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1
        
    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        
        # Show the cv2 screen
        # cv2.imshow("CV2 Image", frame)
        
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

    def take_picture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        output = 'output'
        now = datetime.datetime.now()
        filename = "%s/%02d.%02d.%02d-%02d-%02d-%02d.png" % (
            output, now.year, now.month, now.day, now.hour, now.minute, now.second
        )
        camera = self.img1
        camera.export_to_png(filename)

if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
