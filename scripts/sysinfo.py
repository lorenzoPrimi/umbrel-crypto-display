import math
import subprocess
from typing import Tuple

from PIL import ImageDraw, Image

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):

    def drawicon(self, draw: ImageDraw, icon, x, y, w, h, v=None):
        if icon == "thermometer":
            tw = w / 3
            draw.ellipse(xy=(x, y + ((h - y) / 4 * 3), tw, h), fill=self.color("#C0C0C0"), outline=None, width=1)
            draw.ellipse(xy=(x + ((tw - x) / 4 * 1), y, x + ((tw - x) / 4 * 3), y + ((h - y) / 4 * 1)),
                         fill=self.color("#C0C0C0"), outline=None, width=1)
            draw.rectangle(
                xy=(x + ((tw - x) / 4 * 1), y + ((h - y) / 8 * 1), x + ((tw - x) / 4 * 3), y + ((h - y) / 8 * 7)),
                fill=self.color("#C0C0C0"), outline=None, width=1)
            draw.ellipse(xy=(x + 2, y + 2 + ((h - y) / 4 * 3), tw - 2, h - 2), fill=self.color("#000000"), outline=None,
                         width=1)
            draw.ellipse(xy=(x + 2 + ((tw - x) / 4 * 1), y + 2, x - 2 + ((tw - x) / 4 * 3), y - 2 + ((h - y) / 4 * 1)),
                         fill=self.color("#000000"), outline=None, width=1)
            draw.rectangle(xy=(x + 2 + ((tw - x) / 4 * 1), y + 2 + ((h - y) / 8 * 1), x - 2 + ((tw - x) / 4 * 3),
                               y - 2 + ((h - y) / 8 * 7)), fill=self.color("#000000"), outline=None, width=1)
            barcolor = self.color("#C0FFC0")
            barpos = 3
            if int(v) > 55:
                barcolor = self.color("#FFFF00")
                barpos = 2
            if int(v) > 65:
                barcolor = self.color("#FF0000")
                barpos = 1
            draw.ellipse(xy=(x + 4, y + 4 + (h / 4 * 3), tw - 4, h - 4), fill=barcolor, outline=None, width=1)
            draw.rectangle(xy=(
                x + 4 + ((tw - x) / 4 * 1), y + 4 + (h / 8 * barpos), x - 4 + ((tw - x) / 4 * 3), y - 4 + (h / 8 * 7)),
                fill=barcolor, outline=None, width=1)
            for j in range(8):
                draw.rectangle(xy=(
                    x + 6 + ((tw - x) / 4 * 3), y + (h / 4) + ((h / 2 / 8) * j), x + 26 + ((tw - x) / 4 * 3),
                    y + (h / 4) + ((h / 2 / 8) * j)), fill=self.color("#C0C0C0"), outline=self.color("#C0C0C0"), width=3)
            tt = v + "°"
            ttw, tth = draw.textsize(tt, self.getfont(48))
            ox, oy = self.getfont(48).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text((x + w - ttw, y + (h / 2)), tt, font=self.getfont(48), fill=self.color("#FFFFFF"), stroke_width=1)
            tt = "Temp"
            ttw, tth = draw.textsize(tt, self.getfont(24))
            ox, oy = self.getfont(24).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2) - (ttw / 2), y + ((h / 8) * 1) - (tth / 2)), text=tt, font=self.getfont(24),
                      fill=self.color("#FFFFFF"), stroke_width=1)
        if icon == "piestorage":
            if list(v.split())[5] == "error":
                self.drawicon(draw, "pieerror", x, y, w, h)
                return
            pct = int(list(v.split())[4].replace("%", ""))
            gbf = list(v.split())[3]
            pad = 30
            ox = 3
            oy = 3
            if pct == 50:
                ox = 0
            if pct > 50:
                ox = ox * -1
            sa = 0
            ea = sa + math.floor(pct * 3.6)
            slicecolor = self.color("#C0FFC0")
            textcolor = self.color("#000000")
            if pct > 80:
                slicecolor = self.color("#FFFF00")
                textcolor = self.color("#000000")
            if pct > 90:
                slicecolor = self.color("#FF0000")
                textcolor = self.color("#FFFFFF")
            draw.pieslice(xy=(x + pad + ox, y + pad + oy, x + w + ox - pad, y + h + oy - pad), start=sa, end=ea,
                          fill=slicecolor, outline=self.color("#C0C0C0"), width=2)
            tt = "used"
            ttw, tth = draw.textsize(tt, self.getfont(16))
            ox, oy = self.getfont(16).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2), y + (h / 2) + (tth / 2)), text=tt, font=self.getfont(16), fill=textcolor)
            ox = ox * -1
            oy = oy * -1
            sa = ea
            ea = 360
            textcolor = self.color("#FFFFFF")
            draw.pieslice(xy=(x + pad + ox, y + pad + oy, x + w + ox - pad, y + h + oy - pad), start=sa, end=ea,
                          fill=self.color("#000000"), outline=self.color("#C0C0C0"), width=2)
            tt = "free"
            ttw, tth = draw.textsize(tt, self.getfont(16))
            ox, oy = self.getfont(16).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2), y + (h / 2) - (tth / 2) + oy - pad), text=tt, font=self.getfont(16),
                      fill=textcolor)
            tt = gbf + " free"
            ttw, tth = draw.textsize(tt, self.getfont(20))
            ox, oy = self.getfont(20).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2) - (ttw / 2), y + h - (tth / 2) - 10), text=tt, font=self.getfont(20),
                      fill=self.color("#FFFFFF"))
        if icon == "sdcard":
            self.drawicon(draw, "piestorage", x, y, w, h, v)
            tt = "/dev/root"
            ttw, tth = draw.textsize(tt, self.getfont(24))
            ox, oy = self.getfont(24).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + ((w / 2) - (ttw / 2)) + 1, y + (tth / 2) + 1 - 10), text=tt, font=self.getfont(24),
                      fill=self.color("#000000"), stroke_width=3)
            draw.text(xy=(x + ((w / 2) - (ttw / 2)), y + (tth / 2) - 10), text=tt, font=self.getfont(24),
                      fill=self.color("#FFFFFF"),
                      stroke_width=1)
        if icon == "hdd":
            self.drawicon(draw, "piestorage", x, y, w, h, v)
            tt = "/dev/sda1"
            ttw, tth = draw.textsize(tt, self.getfont(24))
            ox, oy = self.getfont(24).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + ((w / 2) - (ttw / 2)) + 1, y + (tth / 2) + 1 - 10), text=tt, font=self.getfont(24),
                      fill=self.color("#000000"), stroke_width=3)
            draw.text(xy=(x + ((w / 2) - (ttw / 2)), y + (tth / 2) - 10), text=tt, font=self.getfont(24),
                      fill=self.color("#FFFFFF"),
                      stroke_width=1)
        if icon == "cpuload":
            tt = "CPU Load"
            ttw, tth = draw.textsize(tt, self.getfont(24))
            ox, oy = self.getfont(24).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2) - (ttw / 2), y + ((h / 8) * 1) - (tth / 2)), text=tt, font=self.getfont(24),
                      fill=self.color("#FFFFFF"), stroke_width=1)
            tt = "1 min"
            ttw, tth = draw.textsize(tt, self.getfont(16))
            ox, oy = self.getfont(16).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x, y + ((h / 8) * 3) - (tth / 2)), text=tt, font=self.getfont(16), fill=self.color("#FFFFFF"))
            tt = "5 min"
            ttw, tth = draw.textsize(tt, self.getfont(16))
            ox, oy = self.getfont(16).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x, y + ((h / 8) * 5) - (tth / 2)), text=tt, font=self.getfont(16), fill=self.color("#FFFFFF"))
            tt = "15 min"
            ttw, tth = draw.textsize(tt, self.getfont(16))
            ox, oy = self.getfont(16).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x, y + ((h / 8) * 7) - (tth / 2)), text=tt, font=self.getfont(16), fill=self.color("#FFFFFF"))
            for j in range(3):
                draw.rounded_rectangle(
                    xy=(x + ttw + 3, y + ((h / 8) * ((j * 2) + 2)) + 3, x + w, y + ((h / 8) * ((j * 2) + 4)) - 3),
                    radius=4, outline=self.color("#C0C0C0"), width=2)
                ld = list(v.split())[j]
                ldw = int(((x + w) - (x + ttw + 3)) * (float(ld) / float(self.getprocessorcount())))
                barcolor = self.color("#C0FFC0")
                if float(ld) > .50:
                    barcolor = self.color("#FFFF00")
                if float(ld) > .75:
                    barcolor = self.color("#FF0000")
                draw.rounded_rectangle(xy=(x + ttw + 3 + 1, y + ((h / 8) * ((j * 2) + 2)) + 4, x + ttw + 3 + 1 + ldw,
                                           y + ((h / 8) * ((j * 2) + 4)) - 3 - 1), radius=4, fill=barcolor, width=1)
        if icon == "memory":
            l = list(v.split())[0]
            p = list(v.split())[1]
            pad = 20
            draw.arc(xy=(x + pad, y + (pad * 2), x + w - pad, y + h), start=120, end=420, fill=self.color("#C0C0C0"),
                     width=20)
            draw.arc(xy=(x + pad + 2, y + (pad * 2) + 2, x + w - pad - 2, y + h - 2), start=120 + 1, end=420 - 1,
                     fill=self.color("#000000"), width=16)
            arccolor = self.color("#C0FFC0")
            if int(p) == 0:
                p = "1"
            if int(p) > 75:
                arccolor = self.color("#FFFF00")
            if int(p) > 90:
                arccolor = self.color("#FF0000")
            ea = 120 + int((420 - 120) * (float(p) / 100))
            draw.arc(xy=(x + pad + 2, y + (pad * 2) + 2, x + w - pad - 2, y + h - 2), start=120, end=ea, fill=arccolor,
                     width=16)
            tt = l
            ttw, tth = draw.textsize(tt, self.getfont(24))
            ox, oy = self.getfont(24).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2) - (ttw / 2), y + ((h / 8) * 1) - (tth / 2)), text=tt, font=self.getfont(24),
                      fill=self.color("#FFFFFF"), stroke_width=1)
            tt = p + "%"
            ttw, tth = draw.textsize(tt, self.getfont(20))
            ox, oy = self.getfont(20).getoffset(tt)
            ttw += ox
            tth += oy
            draw.text(xy=(x + (w / 2) - (ttw / 2) + 1, y + ((h / 8) * 5) - (tth / 2) + 1), text=tt,
                      font=self.getfont(20),
                      fill=self.color("#000000"))
            draw.text(xy=(x + (w / 2) - (ttw / 2), y + ((h / 8) * 5) - (tth / 2)), text=tt, font=self.getfont(20),
                      fill=self.color("#FFFFFF"))
        if icon == "datetime":
            dt = "as of " + self.getdateandtime()
            dtw, dth = draw.textsize(dt, self.getfont(12))
            ox, oy = self.getfont(12).getoffset(dt)
            dtw += ox
            dth += oy
            draw.text((w - dtw, h - dth), dt, font=self.getfont(12), fill=self.color("#FFFFFF"))

    def createimage(self, width=480, height=320):
        bw = width / 3
        bh = height / 2
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        self.drawicon(draw, "thermometer", 5, 5, bw - 10, bh - 10, v=str(self.gettemp()))
        self.drawicon(draw, "sdcard", 5 + bw, 5, bw - 10, bh - 10, v=str(self.getdrivefree("/dev/root")))
        self.drawicon(draw, "hdd", 5 + bw + bw, 5, bw - 10, bh - 10, v=str(self.getdrivefree("/dev/sda1")))
        self.drawicon(draw, "cpuload", 5, bh + 5, bw, bh - 10, v=str(self.getloadavg()))
        self.drawicon(draw, "memory", 5 + bw, bh + 5, bw, bh - 10, v=str(self.getmemusage("Mem", "RAM")))
        self.drawicon(draw, "memory", 5 + bw + bw, bh + 5, bw, bh - 10, v=str(self.getmemusage("Swap", "Swap")))
        self.drawicon(draw, "datetime", 0, 0, width, height)
        return im

    def gettemp(self):
        cmd = "cat /sys/class/thermal/thermal_zone0/temp"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            temp = int(cmdoutput)
            return math.floor(temp / 1000)
        except subprocess.CalledProcessError as e:
            return -1

    def getdrivefree(self, path):
        cmd = "df -h | grep " + path
        try:
            return subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            return path + " 0G 0G 0G 1% error"

    def getloadavg(self):
        cmd = "cat /proc/loadavg"
        try:
            return subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            return "1.00 1.00 1.00 9 99999"

    def getprocessorcount(self):
        cmd = "cat /proc/cpuinfo | grep processor | wc -l"
        try:
            return int(subprocess.check_output(cmd, shell=True).decode("utf-8"))
        except subprocess.CalledProcessError as e:
            return 4

    def getmemusage(self, memtype, label):
        cmd = "free --mebi | grep " + memtype
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            t = list(cmdoutput.split())[1]
            u = list(cmdoutput.split())[2]
            v = int((float(u) / float(t)) * 100)
            return label + " " + str(v)
        except subprocess.CalledProcessError as e:
            return label + " ?"

    def generate_all_images(self, screen_size: Tuple[int, int]):
        (width, height) = screen_size
        yield self.createimage(width=width, height=height)
