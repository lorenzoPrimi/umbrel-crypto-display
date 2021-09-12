import json
import math
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

    def drawcenteredtext(self, draw, s, fontsize, x, y, textcolor=colorFFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - (sw / 2), y - (sh / 2)), text=s, font=thefont, fill=textcolor)

    def drawbottomlefttext(self, draw, s, fontsize, x, y, textcolor=colorFFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x, y - sh), text=s, font=thefont, fill=textcolor)

    def drawbottomrighttext(self, draw, s, fontsize, x, y, textcolor=colorFFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y - sh), text=s, font=thefont, fill=textcolor)

    def drawtoplefttext(self, draw, s, fontsize, x, y, textcolor=colorFFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x, y), text=s, font=thefont, fill=textcolor)

    def drawtoprighttext(self, draw, s, fontsize, x, y, textcolor=colorFFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y), text=s, font=thefont, fill=textcolor)

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

    def getepochnum(self, blocknum):
        return int(math.floor(blocknum / 2016))

    def getfirstblockforepoch(self, blocknum):
        epochnum = self.getepochnum(blocknum)
        return int(epochnum * 2016) + 1

    def getcurrenttimeinseconds(self):
        cmd = "date -u +%s"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            return int(cmdoutput)
        except subprocess.CalledProcessError as e:
            print(e)
            return 1

    def getblock(self, blocknum):
        cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "`"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
            return j
        except subprocess.CalledProcessError as e:
            print(e)
            fakejson = "{\"confirmations\": 1, \"time\": " + str(self.getcurrenttimeinseconds) + "\"}"
            return json.loads(fakejson)

    def createimage(self, width=480, height=320):
        currentblock = self.getcurrentblock()
        j = self.getblock(self.getfirstblockforepoch(currentblock))
        blocksmined = int(j["confirmations"])
        timebegan = int(j["time"])
        timenow = self.getcurrenttimeinseconds()
        secondspassed = timenow - timebegan
        expectedmined = int(math.floor(secondspassed / 600))
        if blocksmined == 1:
            expectedmined = 1
        nextadjustment = "0.0"
        if float(expectedmined) > 0 and float(blocksmined) > 0:
            nextadjustment = str(float("%.2f" % (((float(blocksmined) / float(expectedmined)) - 1.0) * 100)))
        adjustcolor = self.colorbehind
        if "-" not in nextadjustment:
            nextadjustment = "+" + nextadjustment
            adjustcolor = self.colormined
        estimateepochend = timebegan + (2016 * 600)
        if float(blocksmined) > 0:
            estimateepochend = int(math.floor((float(secondspassed) / float(blocksmined)) * 2016)) + timebegan
        secondstoepochend = estimateepochend - timenow
        nextepochdesc = ""
        if blocksmined >= 10:
            if secondstoepochend > 86400:
                nextepochdays = math.floor(secondstoepochend / 86400)
                nextepochdesc = nextepochdesc + str(nextepochdays) + " day"
                if nextepochdays > 1:
                    nextepochdesc = nextepochdesc + "s"
                secondstoepochend = secondstoepochend - (nextepochdays * 86400)
            if secondstoepochend > 3600:
                nextepochhours = math.floor(secondstoepochend / 3600)
                if nextepochdesc != "":
                    nextepochdesc = nextepochdesc + ", "
                nextepochdesc = nextepochdesc + str(nextepochhours) + " hour"
                if nextepochhours > 1:
                    nextepochdesc = nextepochdesc + "s"
                secondstoepochend = secondstoepochend - (nextepochhours * 3600)
            if (secondstoepochend > 600) and ("," not in nextepochdesc):
                nextepochminutes = math.floor(secondstoepochend / 60)
                if nextepochdesc != "":
                    nextepochdesc = nextepochdesc + ", "
                nextepochdesc = nextepochdesc + str(nextepochminutes) + " minute"
                if nextepochminutes > 1:
                    nextepochdesc = nextepochdesc + "s"
                secondstoepochend = secondstoepochend - (nextepochminutes * 60)
            else:
                if nextepochdesc == "":
                    "a few minutes"
        else:
            nextepochdesc = "about 2 weeks"

        blockw = int(math.floor(width / 63))
        padleft = int(math.floor((width - (63 * blockw)) / 2))
        padtop = 36
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        for dc in range(63):
            for dr in range(32):
                epochblocknum = ((dr * 63) + dc) + 1
                tlx = (padleft + (dc * blockw))
                tly = (padtop + (dr * blockw))
                brx = tlx + blockw - 2
                bry = tly + blockw - 2
                if epochblocknum <= blocksmined:
                    fillcolor = self.colormined
                    if epochblocknum > expectedmined:
                        fillcolor = self.colorahead
                    draw.rectangle(xy=((tlx, tly), (brx, bry)), fill=fillcolor)
                else:
                    outlinecolor = self.colorgrid
                    if epochblocknum <= expectedmined:
                        outlinecolor = self.colorbehind
                    draw.rectangle(xy=((tlx, tly), (brx, bry)), fill=None, outline=outlinecolor)
        self.drawcenteredtext(draw, "Blocks Mined This Difficulty Epoch", 24, int(width / 2), int(padtop / 2))
        self.drawtoprighttext(draw, "Expected: ", 18, int(width / 4 * 1), height - 56)
        self.drawtoplefttext(draw, str(expectedmined), 18, int(width / 4 * 1), height - 56)
        self.drawtoprighttext(draw, "Mined: ", 18, int(width / 4 * 1), height - 32)
        self.drawtoplefttext(draw, str(blocksmined), 18, int(width / 4 * 1), height - 32)
        self.drawtoprighttext(draw, "Retarget: ", 18, int(width / 10 * 6), height - 56)
        self.drawtoplefttext(draw, str(nextadjustment) + "%", 18, int(width / 10 * 6), height - 56, adjustcolor)
        self.drawtoprighttext(draw, "In: ", 18, int(width / 10 * 6), height - 32)
        self.drawtoplefttext(draw, str(nextepochdesc), 18, int(width / 10 * 6), height - 32)
        self.drawbottomrighttext(draw, "as of " + self.getdateandtime(), 12, width, height)
        return im

    def generate_all_images(self, screen_size: Tuple[int, int]):
        (width, height) = screen_size
        yield self.createimage(width=width, height=height)
