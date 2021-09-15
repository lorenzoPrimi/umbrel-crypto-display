from datetime import datetime
from typing import Tuple, Iterator, Any, Union

from PIL import ImageColor, ImageFont, ImageDraw

from .config import Config
from .utils import find_file

__all__ = ['iScriptImageGenerator', 'iPygameScript']

default_color_text = ImageColor.getrgb("#ffffff")


class iScriptImageGenerator:
    color_red = ImageColor.getrgb("#FF0000")
    color_green = ImageColor.getrgb("#32CD30")
    color_gold = ImageColor.getrgb("#FFD700")
    color_D9D9D9 = ImageColor.getrgb("#D9D9D9")
    color_404040 = ImageColor.getrgb("#404040")
    color_40C040 = ImageColor.getrgb("#40C040")
    color_40FF40 = ImageColor.getrgb("#40FF40")
    color_000000 = ImageColor.getrgb("#000000")
    color_FFFFFF = ImageColor.getrgb("#ffffff")
    color_202020 = ImageColor.getrgb("#202020")
    color_606060 = ImageColor.getrgb("#606060")

    def __init__(self):
        self.config = Config()
        self.cryptos = self.config.cryptos
        self.show_logo = self.config.get_bool("SHOW_LOGO", 'n')

    @staticmethod
    def getdateandtime() -> str:
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def getfont(self, size: int) -> ImageFont:
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans.ttf"), size)

    def getfont_bold(self, size: int) -> ImageFont:
        return ImageFont.truetype(find_file("/usr/share/fonts", "DejaVuSans-Bold.ttf"), size)

    def drawcenteredtext(
            self,
            draw: ImageDraw,
            s: str,
            fontsize: int,
            x: int,
            y: int,
            textcolor: Tuple[int, int, int] = default_color_text
    ):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - (sw / 2), y - (sh / 2)), text=s, font=thefont, fill=textcolor)

    def drawbottomlefttext(
            self,
            draw: ImageDraw,
            s: str,
            fontsize: int,
            x: int,
            y: int,
            textcolor: Tuple[int, int, int] = default_color_text
    ):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x, y - sh), text=s, font=thefont, fill=textcolor)

    def drawbottomrighttext(
            self,
            draw: ImageDraw,
            s: str,
            fontsize: int,
            x: int,
            y: int,
            textcolor: Tuple[int, int, int] = default_color_text
    ):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y - sh), text=s, font=thefont, fill=textcolor)

    def drawtoprighttext(
            self,
            draw: ImageDraw,
            s: str,
            fontsize: int,
            x: int,
            y: int,
            textcolor: ImageColor = default_color_text
    ):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x - sw, y), text=s, font=thefont, fill=textcolor)

    def drawsatssquare(
            self,
            draw: ImageDraw,
            dc,
            dr,
            spf,
            satw,
            bpx,
            bpy
    ):
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

    def drawtoplefttext(
            self,
            draw: ImageDraw,
            s: str,
            fontsize: int,
            x: int,
            y: int,
            textcolor: Tuple[int, int, int] = default_color_text
    ):
        thefont = self.getfont(fontsize)
        sw, sh = draw.textsize(s, thefont)
        ox, oy = thefont.getoffset(s)
        sw += ox
        sh += oy
        draw.text(xy=(x, y), text=s, font=thefont, fill=textcolor)

    def generate_all_images(self, screen_size: Tuple[int, int]) -> Iterator[Any]:
        raise NotImplementedError("method 'generate_all_images()' not implemented")


import pygame
import threading


class iPygameScript(threading.Thread):

    def __init__(self):
        super().__init__()
        # http://www.pygame.org/docs/ref/display.html#pygame.display.init
        pygame.display.init()
        flags = pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(self.size, flags, 32)
        self.screen.fill((0, 0, 0))
        pygame.font.init()
        pygame.display.update()
        self.stop_event = threading.Event()

    def __del__(self):
        pygame.display.quit()

    @property
    def size(self):
        # return (int(pygame.display.Info().current_w * self.mult), int(pygame.display.Info().current_h * self.mult))
        return pygame.display.list_modes()[0]

    def run(self):
        self.init()
        while not self.quit_event():
            self.step()
            pygame.display.flip()

    def init(self):
        pass

    def step(self):
        raise NotImplementedError("method 'step()' not implemented")

    def stop(self):
        self.stop_event.set()

    def quit_event(self) -> bool:
        if self.stop_event.is_set():
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return True
        return False
