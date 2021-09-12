import json
import subprocess
from datetime import datetime
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageColor

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script:
    colorFFFFFF = ImageColor.getrgb("#ffffff")

    def getfont(self, size: int):
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans.ttf"), size)

    def getfont_bold(self, size: int):
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans-Bold.ttf"), size)

    def drawcenteredtext(self, draw, s, fontsize, x, y):
        thefont = self.getfont_bold(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - (sw / 2), y - (sh / 2)), text=s, font=thefont, fill=self.colorFFFFFF)

    def drawbottomrighttext(self, draw, s, fontsize, x, y):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y - sh), text=s, font=thefont, fill=self.colorFFFFFF)

    def getcurrentblock(self):
        cmd = "bitcoin-cli getblockchaininfo"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
            blockcurrent = int(j["blocks"])
            return blockcurrent
        except subprocess.CalledProcessError as e:
            print(e)
            return 1

    def getdateandtime(self):
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def generate_all_images(self, screen_size: Tuple[int, int]):
        width, height = screen_size
        currentblock = self.getcurrentblock()
        im = Image.new(mode="RGB", size=screen_size)
        draw = ImageDraw.Draw(im)
        self.drawcenteredtext(draw, str(currentblock), 96, int(width / 2), int(height / 2))
        self.drawbottomrighttext(draw, "as of " + self.getdateandtime(), 12, width, height)
        yield im
