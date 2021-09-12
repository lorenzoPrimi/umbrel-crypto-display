import subprocess
from datetime import datetime
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageColor

try:
    from libs import *
except ImportError as e:
    from ..libs import *

colorFFFFFF = ImageColor.getrgb("#ffffff")


class Script:
    colorgrid = ImageColor.getrgb("#404040")
    colorahead = ImageColor.getrgb("#FFFF40")
    colorbehind = ImageColor.getrgb("#FF0000")
    colormined = ImageColor.getrgb("#40FF40")
    color000000 = ImageColor.getrgb("#000000")
    colorFFFFFF = colorFFFFFF

    def getdateandtime(self):
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def getfont(self, size: int):
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans.ttf"), size)

    def getfont_bold(self, size: int):
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans-Bold.ttf"), size)

    def drawcenteredtext(self, draw, s, fontsize, x, y):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - (sw / 2), y - (sh / 2)), text=s, font=thefont, fill=colorFFFFFF)

    def drawbottomrighttext(self, draw, s, fontsize, x, y):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y - sh), text=s, font=thefont, fill=colorFFFFFF)

    def getcurrentip(self):
        cmd = "hostname -I"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            iplist = cmdoutput.split()
            goodip = "IP Addresses:\n"
            for i in iplist:
                if len(i) <= 15:
                    goodip = goodip + "\n" + i
            return goodip
        except subprocess.CalledProcessError as e:
            print(e)
            return "unknown"

    def createimage(self, width=480, height=320):
        currentip = self.getcurrentip()
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        self.drawcenteredtext(draw, str(currentip), 48, int(width / 2), int(height / 2))
        self.drawbottomrighttext(draw, "as of " + self.getdateandtime(), 12, width, height)
        return im

    def generate_all_images(self, screen_size: Tuple[int, int]):
        (width, height) = screen_size
        yield self.createimage(width=width, height=height)
