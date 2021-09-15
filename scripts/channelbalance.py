# original code from: https://github.com/vicariousdrama/nodeyez/blob/main/scripts/channelbalance.py

import json
import math
import subprocess
from typing import Tuple

from PIL import Image, ImageDraw
from PIL import ImageColor

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):
    colorBackground = ImageColor.getrgb("#000000")
    colorBarOutline = ImageColor.getrgb("#770044")
    colorBarFilled = ImageColor.getrgb("#aa3377")
    pubkey_alias = {'pubkey': 'alias'}

    def getnodeinfo(self, pubkey):
        cmd = f"lncli getnodeinfo --pub_key {pubkey} --include_channels 2>&1"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            cmdoutput = "{\"node\":{\"alias\":\"" + pubkey + "\",\"pub_key\":\"" + pubkey + "\",\"addresses\":[{\"network\":\"tcp\",\"addr\":\"0.0.0.0:65535\"}]}}"
        j = json.loads(cmdoutput)
        return j

    def getnodealias(self, nodeinfo):
        return nodeinfo["node"]["alias"]

    def getnodechannels(self):
        cmd = "lncli listchannels 2>&1"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            cmdoutput = '{\"channels\": []}'
        j = json.loads(cmdoutput)
        return j

    def getdefaultaliasfrompubkey(self, pubkey):
        return pubkey[0:10]

    def getnodealiasfrompubkey(self, pubkey):
        # alias = self.getdefaultaliasfrompubkey(pubkey)
        if pubkey in self.pubkey_alias.keys():
            alias = self.pubkey_alias[pubkey]
            if len(alias) < 1:
                alias = self.getdefaultaliasfrompubkey(pubkey)
        else:
            nodeinfo = self.getnodeinfo(pubkey)
            alias = self.getnodealias(nodeinfo)
            self.pubkey_alias[pubkey] = alias
        return alias

    def createimage(self, channels, firstidx, lastidx, pagenum, pagesize, width=480, height=320):
        padding = 4
        outlinewidth = 2
        padtop = 40
        padbottom = 40
        aliaswidth = width / 3
        dataheight = int(math.floor((height - (padtop + padbottom)) / pagesize))
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        # Header
        self.drawcenteredtext(draw, "Lightning Channel Balances", 24, int(width / 2), int(padtop / 2))
        # Channel info
        linesdrawn = 0
        for channelidx in range(firstidx, (lastidx + 1)):
            linesdrawn = linesdrawn + 1
            currentchannel = channels[channelidx]
            remote_pubkey = currentchannel["remote_pubkey"]
            capacity = int(currentchannel["capacity"])
            local_balance = int(currentchannel["local_balance"])
            # remote_balance = int(currentchannel["remote_balance"])
            # commit_fee = int(currentchannel["commit_fee"])
            alias = self.getnodealiasfrompubkey(remote_pubkey)
            datarowbottom = padtop + (linesdrawn * dataheight)
            datarowtop = datarowbottom - dataheight
            self.drawbottomlefttext(draw, alias, 16, 0, datarowbottom)
            draw.rounded_rectangle(xy=(aliaswidth, datarowtop + padding, width, datarowbottom), radius=4,
                                   fill=self.colorBackground, outline=self.colorBarOutline, width=outlinewidth)
            percentage = float(local_balance) / float(capacity)
            barwidth = int(math.floor(float(width - aliaswidth) * percentage))
            draw.rounded_rectangle(xy=(
                aliaswidth + outlinewidth, datarowtop + padding + outlinewidth, aliaswidth + outlinewidth + barwidth,
                datarowbottom - outlinewidth), radius=4, fill=self.colorBarFilled)
        draw.rectangle(xy=(aliaswidth - padding, padtop, aliaswidth - 1, height - padbottom), fill=self.colorBackground)
        # Page Info
        channelcount = len(channels)
        pages = int(math.ceil(float(channelcount) / float(pagesize)))
        paging = str(pagenum) + "/" + str(pages)
        self.drawbottomlefttext(draw, paging, 24, 0, height)
        # Date and Time
        dt = f"as of {self.getdateandtime()}"
        self.drawbottomrighttext(draw, dt, 12, width, height)
        return im

    def generate_all_images(self, screen_size: Tuple[int, int]):
        channels = self.getnodechannels()
        channels = channels["channels"]
        channelcount = len(channels)
        pagesize = 8
        pages = int(math.ceil(float(channelcount) / float(pagesize)))
        for pagenum in range(1, (pages + 1)):
            firstidx = ((pagenum - 1) * pagesize)
            lastidx = (pagenum * pagesize) - 1
            if lastidx > channelcount - 1:
                lastidx = channelcount - 1
            yield self.createimage(channels, firstidx, lastidx, pagenum, pagesize)
