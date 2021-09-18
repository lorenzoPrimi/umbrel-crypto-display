# original code from: https://github.com/vicariousdrama/nodeyez/blob/main/scripts/mempool-blocks.py
import json
import locale
import math
import subprocess
from typing import Tuple

from PIL import Image, ImageDraw

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):
    # urlmempool = "http://127.0.0.1:4080/api/v1/fees/mempool-blocks"
    urlmempool = "https://mempool.space/api/v1/fees/mempool-blocks"
    # urlfeerecs = "http://127.0.0.1:4080/api/v1/fees/recommended"
    urlfeerecs = "https://mempool.space/api/v1/fees/recommended"

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def drawmempoolblock(self, draw, x, y, w, h, blockinfo, mpb):
        blocksize = blockinfo["blockSize"]
        blockvsize = blockinfo["blockVSize"]
        transactions = blockinfo["nTx"]
        feeranges = list(blockinfo["feeRange"])
        feelow = feeranges[0]
        feehigh = feeranges[len(feeranges) - 1]
        feemedian = blockinfo["medianFee"]
        depth = int(math.floor(w * .14))
        pad = 2
        blockcolor = self.color("#40C040")
        draw.polygon(xy=((x + pad, y + pad), (x + pad, y + h - pad - depth), (x + pad + depth, y + h - pad),
                         (x + pad + depth, y + pad + depth)), outline=self.color("#202020"), fill=self.color("#404040"))
        draw.polygon(xy=((x + pad, y + pad), (x + pad + depth, y + pad + depth), (x + w - pad, y + pad + depth),
                         (x + w - pad - depth, y + pad)), outline=self.color("#202020"), fill=self.color("#606060"))
        draw.polygon(xy=((x + pad + depth, y + pad + depth), (x + w - pad, y + pad + depth), (x + w - pad, y + h - pad),
                         (x + pad + depth, y + h - pad)), outline=self.color("#202020"), fill=blockcolor)
        centerx = x + depth + (int(math.floor((w - depth) / 2)))
        descriptor = "~" + str(int(math.floor(float(feemedian)))) + " sat/vB"
        self.drawcenteredtext(draw, descriptor, 14, centerx, y + pad + (depth * 2))
        descriptor = str(int(math.floor(float(feelow)))) + " - " + str(int(math.floor(float(feehigh)))) + " sat/vB"
        self.drawcenteredtext(draw, descriptor, 14, centerx, y + pad + (depth * 3))
        descriptor = self.convert_size(int(blocksize))
        self.drawcenteredtext(draw, descriptor, 18, centerx, y + pad + (depth * 4))
        locale.setlocale(locale.LC_ALL, '')
        descriptor = '{:n}'.format(int(transactions)) + " transactions"
        self.drawcenteredtext(draw, descriptor, 14, centerx, y + pad + (depth * 5))
        descriptor = "In ~" + str((mpb + 1) * 10) + " minutes"
        self.drawcenteredtext(draw, descriptor, 14, centerx, y + pad + (depth * 6))

    def createimage(self, width=480, height=320):
        mempoolblocks = self.getmempoolblocks()
        feefastest, feehalfhour, feehour, feeminimum = self.getrecommendedfees()
        bw = width / 3
        padtop = 40
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        mpblist = list(mempoolblocks)
        mpblen = len(mpblist)
        for mpb in range(mpblen):
            if mpb > 2:
                break
            self.drawmempoolblock(draw, (width - ((mpb + 1) * bw)), padtop, bw, bw, mpblist[mpb], mpb)
        self.drawcenteredtext(draw, "Mempool Block Fee Estimates", 24, int(width / 2), int(padtop / 2))
        self.drawcenteredtext(draw, "Next: " + str(feefastest), 20, int(width / 8 * 1), height - padtop)
        self.drawcenteredtext(draw, "30 Min: " + str(feehalfhour), 20, int(width / 8 * 3), height - padtop)
        self.drawcenteredtext(draw, "1 Hr: " + str(feehour), 20, int(width / 8 * 5), height - padtop)
        self.drawcenteredtext(draw, "Minimum: " + str(feeminimum), 20, int(width / 8 * 7), height - padtop)
        self.drawbottomrighttext(draw, "as of " + self.getdateandtime(), 12, width, height)
        return im

    def getmempoolblocks(self):
        cmd = "curl --silent " + self.urlmempool
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
            return j
        except subprocess.CalledProcessError as e:
            cmdoutput = "[]"
            j = json.loads(cmdoutput)
            return j

    def getrecommendedfees(self):
        cmd = "curl --silent " + self.urlfeerecs
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
            return j["fastestFee"], j["halfHourFee"], j["hourFee"], j["minimumFee"]
        except subprocess.CalledProcessError as e:
            return 1, 1, 1, 1

    def generate_all_images(self, screen_size: Tuple[int, int]):
        (width, height) = screen_size
        yield self.createimage(width=width, height=height)
