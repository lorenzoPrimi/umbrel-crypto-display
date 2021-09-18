import math
import os
from typing import Tuple

from PIL import ImageDraw, Image

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iScriptImageGenerator):

    def _draw_text(self, draw, tt, x, y, w, h, font_size=24):
        font = self.getfont(font_size)
        ttw, tth = draw.textsize(tt, font)
        ox, oy = font.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(
            xy=(
                x + (w / 2) - (ttw / 2),
                y + ((h / 8) * 1) - (tth / 2)
            ),
            text=tt,
            font=font,
            fill=self.color("#FFFFFF"),
            stroke_width=1
        )

    def drawicon_thermometer(self, draw: ImageDraw, x, y, w, h):
        v = self.gettemp()
        tw = w / 3
        draw.ellipse(
            xy=(
                x, y + ((h - y) / 4 * 3),
                tw, h
            ),
            fill=self.color("#C0C0C0"),
            outline=None,
            width=1
        )
        draw.ellipse(
            xy=(
                x + ((tw - x) / 4 * 1),
                y,
                x + ((tw - x) / 4 * 3),
                y + ((h - y) / 4 * 1)
            ),
            fill=self.color("#C0C0C0"),
            outline=None,
            width=1
        )
        draw.rectangle(
            xy=(
                x + ((tw - x) / 4 * 1),
                y + ((h - y) / 8 * 1),
                x + ((tw - x) / 4 * 3),
                y + ((h - y) / 8 * 7)
            ),
            fill=self.color("#C0C0C0"),
            outline=None,
            width=1
        )
        draw.ellipse(
            xy=(
                x + 2,
                y + 2 + ((h - y) / 4 * 3),
                tw - 2,
                h - 2
            ),
            fill=self.color("#000000"),
            outline=None,
            width=1
        )
        draw.ellipse(
            xy=(
                x + 2 + ((tw - x) / 4 * 1),
                y + 2, x - 2 + ((tw - x) / 4 * 3),
                y - 2 + ((h - y) / 4 * 1)
            ),
            fill=self.color("#000000"),
            outline=None,
            width=1
        )
        draw.rectangle(
            xy=(
                x + 2 + ((tw - x) / 4 * 1),
                y + 2 + ((h - y) / 8 * 1),
                x - 2 + ((tw - x) / 4 * 3),
                y - 2 + ((h - y) / 8 * 7)
            ),
            fill=self.color("#000000"),
            outline=None,
            width=1
        )
        barcolor = self.color("#C0FFC0")
        barpos = 3
        if int(v) > 55:
            barcolor = self.color("#FFFF00")
            barpos = 2
        if int(v) > 65:
            barcolor = self.color("#FF0000")
            barpos = 1
        draw.ellipse(
            xy=(
                x + 4,
                y + 4 + (h / 4 * 3),
                tw - 4,
                h - 4
            ),
            fill=barcolor,
            outline=None,
            width=1
        )
        draw.rectangle(
            xy=(
                x + 4 + ((tw - x) / 4 * 1),
                y + 4 + (h / 8 * barpos),
                x - 4 + ((tw - x) / 4 * 3),
                y - 4 + (h / 8 * 7)
            ),
            fill=barcolor,
            outline=None,
            width=1
        )
        for j in range(8):
            draw.rectangle(
                xy=(
                    x + 6 + ((tw - x) / 4 * 3),
                    y + (h / 4) + ((h / 2 / 8) * j),
                    x + 26 + ((tw - x) / 4 * 3),
                    y + (h / 4) + ((h / 2 / 8) * j)
                ),
                fill=self.color("#C0C0C0"),
                outline=self.color("#C0C0C0"),
                width=3
            )
        tt = f"{v}°"
        font = self.getfont(48)
        ttw, tth = draw.textsize(tt, font)
        ox, oy = font.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(
            (x + w - ttw, y + (h / 2)),
            tt,
            font=font,
            fill=self.color("#FFFFFF"),
            stroke_width=1
        )
        tt = "Temp"
        self._draw_text(draw, tt, x, y, w, h)

    def drawicon_piestorage(self, draw: ImageDraw, x: int, y: int, w: int, h: int, volume):
        try:
            data = self.getdrivefree(volume)
        except:
            self.drawicon(draw, "pieerror", x, y, w, h)
            return

        if hasattr(data, "percent"):
            pct = int(data.percent)
        else:
            pct = int(data.used / data.total * 100)

        gbf = data.free // (2 ** 30)
        pad = 30
        ox = 0
        oy = 0
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
        tt = f"{gbf}Gb free"
        ttw, tth = draw.textsize(tt, self.getfont(20))
        ox, oy = self.getfont(20).getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x + (w / 2) - (ttw / 2), y + h - (tth / 2) - 10), text=tt, font=self.getfont(20),
                  fill=self.color("#FFFFFF"))

    def drawicon(self, draw: ImageDraw, icon, x, y, w, h, v=None):
        if icon == "thermometer":
            self.drawicon_thermometer(draw, x, y, w, h)
        if icon == "hdd":
            self.drawicon_piestorage(draw, x, y, w, h, v)
            font = self.getfont(10)
            ttw, tth = draw.textsize(v, font)
            ox, oy = font.getoffset(v)
            ttw += ox
            tth += oy
            draw.text(
                xy=(
                    x + ((w / 2) - (ttw / 2)),
                    y + (tth / 2)  # + 1 - 10
                ),
                text=v,
                font=font,
                fill=self.color("#000000"),
                stroke_width=3
            )
            draw.text(
                xy=(
                    x + ((w / 2) - (ttw / 2)),
                    y + (tth / 2) - 10
                ),
                text=v,
                font=self.getfont(24),
                fill=self.color("#FFFFFF"),
                stroke_width=1
            )
        if icon == "cpuload":
            tt = "CPU Load"
            self._draw_text(draw, tt, x, y, w, h)
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
            self._draw_text(draw, tt, x, y, w, h)
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
        self.drawicon(draw, "thermometer", 5, 5, bw - 10, bh - 10)
        self.drawicon(draw, "hdd", 5 + bw, 5, bw - 10, bh - 10, v="/")
        self.drawicon(draw, "hdd", 5 + bw + bw, 5, bw - 10, bh - 10, v="/dev/sda1")
        self.drawicon(draw, "cpuload", 5, bh + 5, bw, bh - 10, v=str(self.getloadavg()))
        self.drawicon(draw, "memory", 5 + bw, bh + 5, bw, bh - 10, v=str(self.getmemusage("Mem", "RAM")))
        self.drawicon(draw, "memory", 5 + bw + bw, bh + 5, bw, bh - 10, v=str(self.getmemusage("Swap", "Swap")))
        self.drawicon(draw, "datetime", 0, 0, width, height)
        return im

    def gettemp(self) -> int:
        if not os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            return -1
        temp = int(read_file_line("/sys/class/thermal/thermal_zone0/temp"))
        return math.floor(temp / 1000)

    def getdrivefree(self, path):
        import shutil
        return shutil.disk_usage(path)

    def getloadavg(self) -> str:
        try:
            # return " ".join([str(v) for v in os.getloadavg()])
            return read_file_line("/proc/loadavg")
        except:
            return "0.00 0.00 0.00 9 99999"

    def getprocessorcount(self) -> int:
        import multiprocessing
        return multiprocessing.cpu_count()

    def getmemusage(self, memtype, label) -> str:
        import psutil
        try:
            if memtype == "Mem":
                return f"{label} {int(psutil.virtual_memory().percent)}"
            if memtype == "Swap":
                return f"{label} {int(psutil.swap_memory().percent)}"
            return label + " ?"
        except:
            return label + " ?"

    def generate_all_images(self, screen_size: Tuple[int, int]):
        (width, height) = screen_size
        yield self.createimage(width=width, height=height)
