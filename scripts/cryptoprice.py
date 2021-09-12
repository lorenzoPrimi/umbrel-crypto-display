import io
import logging
import os
import time
from datetime import datetime
from decimal import Decimal
from typing import cast, Optional, Tuple

import requests as requests
from PIL import Image, ImageDraw, ImageColor, ImageFont

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script:
    color_red = ImageColor.getrgb("#FF0000")
    color_green = ImageColor.getrgb("#32CD30")
    color_gold = ImageColor.getrgb("#FFD700")
    color_D9D9D9 = ImageColor.getrgb("#D9D9D9")
    color_404040 = ImageColor.getrgb("#404040")
    color_40FF40 = ImageColor.getrgb("#40FF40")
    color_000000 = ImageColor.getrgb("#000000")
    color_FFFFFF = ImageColor.getrgb("#ffffff")

    def __init__(self):
        self.config = Config()
        self.cryptos = self.config.cryptos
        self.coingecko = CoingeckoApi()
        self.show_logo = self.config.get_bool("SHOW_LOGO", 'n')

    def drawsatssquare(self, draw, dc, dr, spf, satw, bpx, bpy):
        satsleft = spf
        for y in range(10):
            for x in range(10):
                if satsleft > 0:
                    tlx = (bpx + (dc * 11 * satw) + (x * satw))
                    tly = (bpy + (dr * 11 * satw) + (y * satw))
                    brx = tlx + satw - 2
                    bry = tly + satw - 2
                    draw.rectangle(xy=((tlx, tly), (brx, bry)), fill=self.color_40FF40)
                satsleft = satsleft - 1

    @staticmethod
    def getdateandtime():
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def getfont(self, size: int):
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans.ttf"), size)

    def drawcenteredtext(self, draw, s, fontsize, x, y, textcolor=color_FFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - (sw / 2), y - (sh / 2)), text=s, font=thefont, fill=textcolor)

    def drawbottomlefttext(self, draw, s, fontsize, x, y, textcolor=color_FFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x, y - sh), text=s, font=thefont, fill=textcolor)

    def drawbottomrighttext(self, draw, s, fontsize, x, y, textcolor=color_FFFFFF):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y - sh), text=s, font=thefont, fill=textcolor)

    def _round_price(self, price: float) -> str:
        if price is None:
            return " - "
        d = Decimal(price)
        if d % 1 == 0:
            s = f"{d:,.0f}"
        elif d > 1000:
            s = f"{d:,.0f}"
        elif d > 100:
            s = f"{d:,.4f}"
        elif d > 1:
            s = f"{d:,.6f}"
        else:
            s = f"{d:,.8f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s

    def getpriceinfo(self, ticker):
        coin = self.coingecko.get_coin_by_symbol(ticker)
        response = self.coingecko.get_coin(coin_id=coin['id'], market_data=True)

        return {
            'name': response['name'],
            'price': self._round_price(response['market_data']['current_price']['usd']),
            'last': self._round_price(response['market_data']['current_price']['usd']),
            'high': self._round_price(response['market_data']['high_24h']['usd']),
            'low': self._round_price(response['market_data']['low_24h']['usd']),
            'percentage': round(response['market_data']['price_change_percentage_24h'], 2),
            # thumb, small, large
            'image': Image.open(io.BytesIO(requests.get(response['image']['small']).content), 'r').convert('RGBA')
        }

    def createimage(self, ticker, screen_size: Tuple[int, int]):
        pi = self.getpriceinfo(ticker)
        width, height = screen_size
        # satw = int(math.floor(width / 87))
        # padleft = int(math.floor((width - (87 * satw)) / 2))
        padtop = 40
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        self.drawcenteredtext(draw, pi['last'], 128, int(width / 2), int(height / 2), self.color_D9D9D9)
        self.drawcenteredtext(draw, pi['last'], 128, int(width / 2) - 2, int(height / 2) - 2, self.color_FFFFFF)
        self.drawcenteredtext(draw, f"{pi['name']} price:", 24, int(width / 2), int(padtop))
        if self.show_logo:
            logo_image: Image = pi['image']
            im.paste(logo_image, (int(width * 0.05), int((padtop - logo_image.size[1] / 2) / 2)))
        perc_color = self.color_green if pi['percentage'] >= 0 else self.color_red
        self.drawcenteredtext(draw, f"24h: {pi['percentage']:.2f} %", 20, int(width / 8 * 4), height - padtop,
                              perc_color)
        self.drawcenteredtext(draw, f"High: {pi['low']}", 20, int(width / 8 * 7), height - padtop)
        self.drawcenteredtext(draw, f"Low: {pi['high']}", 20, int(width / 8 * 1), height - padtop)
        self.drawbottomlefttext(draw, "Market data by coingecko", 16, 0, height, self.color_40FF40)
        self.drawbottomrighttext(draw, f"as of {self.getdateandtime()}", 12, width, height)
        return im

    def generate_all_images(self, screen_size: Tuple[int, int]):
        for ticker in self.cryptos:
            yield self.createimage(ticker, screen_size)

