import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import requests


class PlayerImage:

    def __init__(self):
        pass

    def convertTime(self, millisecond, type):

        if type == 'second':
            second = str(int((millisecond / 1000) % 60))
            if len(second) == 1:
                return '0' + second
            else:
                return second

        elif type == 'minutes':
            return str(int((millisecond / (1000 * 60)) % 60))

    def createPlayerImage(self, image_uri, progress_ms, duration_ms, name, artist):

        response = requests.get(image_uri)

        #Blend image preview and black with opacity 50%
        background = Image.open('black.jpg')
        foreground = Image.open(BytesIO(response.content))
        blended = Image.blend(background, foreground, alpha=0.5)

        #Draw white background rectangle
        xy = [(0, 640), (640, 625)]
        draw = ImageDraw.Draw(blended)
        draw.rectangle(xy, fill=(255, 255, 255))

        #Draw percentage bar
        percentage = progress_ms / duration_ms * 100
        ratio = 640 * (percentage / 100)
        xy = [(0, 640), (ratio , 625)]
        draw.rectangle(xy, fill=(233, 195, 70))

        fnt_name = ImageFont.truetype('fonts/AppleSDGothicNeoB.ttf', 36)
        fnt_artist = ImageFont.truetype('fonts/AppleSDGothicNeoUL.ttf', 36)
        fnt_time = ImageFont.truetype('fonts/AppleSDGothicNeoUL.ttf', 24)

        #Draw name of music and artist
        draw.text((20, 516), name, font=fnt_name)
        draw.text((21, 550), artist, font=fnt_artist, fill=(233, 195, 70))

        # Draw progress and duration of music
        progress_time = self.convertTime(progress_ms, 'minutes') + ':' + self.convertTime(progress_ms, 'second')
        duration_time = self.convertTime(duration_ms, 'minutes') + ':' + self.convertTime(duration_ms, 'second')
        draw.text((2, 595), progress_time, font=fnt_time)
        draw.text((595, 595), duration_time, font=fnt_time)

        return blended

