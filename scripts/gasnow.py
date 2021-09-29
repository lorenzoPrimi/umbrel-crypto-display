import asyncio
import json
from asyncio import AbstractEventLoop
from typing import Dict, Optional

import pygame
import websockets

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iPygameScript):
    _loop: AbstractEventLoop = None
    _lock: asyncio.Lock = None
    _eth_ws: websockets.client.WebSocketClientProtocol = None
    _polygon_cli: HttpClient = None
    _font: pygame.font.Font = None
    _gas_prices = {
        'ETH': {
            'rapid': '',
            'fast': '',
            'standard': '',
            'slow': '',
        },
        'POLYGON': {
            'rapid': '',
            'fast': '',
            'standard': '',
            'slow': '',
        }
    }

    def init(self):
        pygame.font.init()
        font_size = int(self.screen.get_height() / 10)
        self._font = pygame.font.SysFont('Deja Vu Sans', font_size)

        self._setup_ethereum_gas_price()
        self._setup_polygon_gas_price()

    def _setup_ethereum_gas_price(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._lock = asyncio.Lock()
        self._eth_ws = self._loop.run_until_complete(websockets.connect("wss://www.gasnow.org/ws/gasprice"))

    def _get_ethereum_gas_price(self) -> Optional[Dict]:
        msg = json.loads(self._loop.run_until_complete(self._eth_ws.recv()))
        if msg['type'] == 'gasprice_s':
            return msg['data']
        return None

    def _setup_polygon_gas_price(self):
        self._polygon_cli = HttpClient(base_url='https://gasstation-mainnet.matic.network')

    def _get_polygon_gas_price(self) -> Optional[Dict]:
        return self._polygon_cli._request("")

    def _draw_line_center(self, text: str, line: int = 1, limit_left: int = 0, limit_right: Optional[int] = None):
        if limit_right is None:
            limit_right = self.screen.get_width()
        text_width, text_height = self._font.size(text)
        color = (255, 255, 255)
        x = limit_left + int((limit_right - limit_left) / 2 - text_width / 2)
        y = text_height * line * 1.2
        text_surface = self._font.render(text, False, color)
        self.screen.blit(text_surface, dest=(x, y))

    def _draw_line(self, title: str, value: str, line: int = 1, limit_left: int = 0, limit_right: Optional[int] = None):
        if limit_right is None:
            limit_right = self.screen.get_width()

        value_width, value_height = self._font.size(value)
        title_width, title_height = self._font.size(title)
        color = (255, 255, 255)
        y = title_height * line * 1.2
        left_padding = self._font.size("M")[0] + limit_left

        text_title = self._font.render(title, False, color)
        text_value = self._font.render(value, False, color)
        self.screen.blit(text_title, dest=(left_padding, y))
        self.screen.blit(text_value, dest=(limit_right - value_width, y))

    def _str(self, d: float) -> str:
        if d is None:
            return " - "
        d = float(d)
        if d % 1 == 0:
            s = f"{d:,.0f}"
        elif d > 100:
            s = f"{d:,.0f}"
        elif d > 1:
            s = f"{d:,.2f}"
        else:
            s = f"{d:,.8f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s

    def step(self):
        width = self.screen.get_width()
        half_width = width / 2
        data = self._get_ethereum_gas_price()
        if data:
            self._gas_prices['ETH']['rapid'] = self._str(round(data['rapid'] / 1e9))
            self._gas_prices['ETH']['fast'] = self._str(round(data['fast'] / 1e9))
            self._gas_prices['ETH']['standard'] = self._str(round(data['standard'] / 1e9))
            self._gas_prices['ETH']['slow'] = self._str(round(data['slow'] / 1e9))

        data = self._get_polygon_gas_price()
        if data:
            self._gas_prices['POLYGON']['rapid'] = self._str(data['fastest'])
            self._gas_prices['POLYGON']['fast'] = self._str(data['fast'])
            self._gas_prices['POLYGON']['standard'] = self._str(data['standard'])
            self._gas_prices['POLYGON']['slow'] = self._str(data['safeLow'])

        self.screen.fill((0, 0, 0))

        self._draw_line_center("ETHEREUM", 1, 0, half_width)
        self._draw_line("Rapid:", self._gas_prices['ETH']['rapid'], 2, 0, half_width)
        self._draw_line("Fast:", self._gas_prices['ETH']['fast'], 3, 0, half_width)
        self._draw_line("Standard:", self._gas_prices['ETH']['standard'], 4, 0, half_width)
        self._draw_line("Slow:", self._gas_prices['ETH']['slow'], 5, 0, half_width)

        self._draw_line_center("POLYGON", 1, half_width, width)
        self._draw_line("Rapid:", self._gas_prices['POLYGON']['rapid'], 2, half_width, width)
        self._draw_line("Fast:", self._gas_prices['POLYGON']['fast'], 3, half_width, width)
        self._draw_line("Standard:", self._gas_prices['POLYGON']['standard'], 4, half_width, width)
        self._draw_line("Slow:", self._gas_prices['POLYGON']['slow'], 5, half_width, width)

    def on_stop(self):
        self._eth_ws.close()
