# original code from: https://github.com/vicariousdrama/nodeyez/blob/main/scripts/blockheight.py

import json
import subprocess
from typing import Tuple

from PIL import ImageDraw, Image

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):

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

    def generate_all_images(self, screen_size: Tuple[int, int]):
        width, height = screen_size
        currentblock = self.getcurrentblock()
        im = Image.new(mode="RGB", size=screen_size)
        draw = ImageDraw.Draw(im)
        self.drawcenteredtext(draw, str(currentblock), 96, int(width / 2), int(height / 2))
        self.drawbottomrighttext(draw, "as of " + self.getdateandtime(), 12, width, height)
        yield im
