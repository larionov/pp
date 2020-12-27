#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

print(picdir)
print(libdir)
import io
import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import pyrebase
import base64
import os
import subprocess

config = {
    "apiKey": 'AIzaSyDGx9CeWmvb7xPEHrMb3bSH7X3SjvJq5vA',
    "authDomain": 'pp-1-a93b8.firebaseapp.com',
    "projectId": 'pp-1-a93b8',
    "storageBucket": 'pp-1-a93b8.appspot.com',
    "databaseURL": "https://pp-1-a93b8-default-rtdb.firebaseio.com",
    "messagingSenderId": '526689914857',
    "appId": '1:526689914857:web:5cf13dd546f39bfef6c578',
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

logging.basicConfig(level=logging.DEBUG)
try:
    logging.info("epd2in7 Demo")
    epd = epd2in7.EPD()
    '''4Gray display'''
    logging.info("4Gray display--------------------------------")
    prevImage = ""
    while True:
        res = db.child("board").child("0").child("image").get()
        imData = res.val()[22:]
        if imData != prevImage:

            epd.Init_4Gray()
            bytes2 = io.BytesIO(base64.b64decode(imData))

            #display 4Gra bmp
            Himage = Image.open(bytes2).transpose(Image.FLIP_LEFT_RIGHT)

            epd.display_4Gray(epd.getbuffer_4Gray(Himage))
            epd.sleep()

        os.system('fswebcam  --jpeg 80  --set brightness=155 --set gain=150 --quiet --save wc.jpg') #

        storage.child("images/wc.jpg").put("wc.jpg", 'token')

        # with open('wc.jpeg', 'rb') as binary_file:
        #     binary_file_data = binary_file.read()
        #     base64_encoded_data = base64.b64encode(binary_file_data)
        #     base64_message = base64_encoded_data.decode('utf-8')
        #     db.child("wc").child("0").update({"image": "data:image/jpeg;base64," + base64_message})

        #     print(base64_message)


        prevImage = imData
        # p = subprocess.Popen(["fswebcam", "--set", "brightness=155", "--set", "gain=150", "--quiet", "wc.png"])
        # p.wait()

        logging.info("Goto Sleep...")
        time.sleep(10)

    epd.Dev_exit()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
