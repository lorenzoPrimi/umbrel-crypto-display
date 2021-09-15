# original code from: https://github.com/vicariousdrama/nodeyez/blob/main/scripts/ipaddress.py
import subprocess
from typing import Tuple

from PIL import Image, ImageDraw

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):

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
