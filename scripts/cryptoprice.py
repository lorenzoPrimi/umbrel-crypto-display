import io
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Tuple, cast, List, Optional, Any, Dict

import requests as requests
from PIL import Image, ImageDraw, ImageColor, ImageFont
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

load_dotenv()


def find_file(path: str, filename: str):
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn == filename:
                return os.path.join(root, fn)


def rel_path(relative_path: str) -> str:
    from os.path import dirname, join, abspath, isabs
    if isabs(relative_path):
        return relative_path
    bdir = dirname(__file__)
    joinpath = join(bdir, relative_path)
    return abspath(joinpath)


def config_get_list(name: str, default: Optional[Any] = None) -> List[str]:
    val = os.getenv(name, default)
    if val:
        return val.split(",")
    else:
        return []


def config_get_int(name: str, default: Optional[int] = None) -> Optional[int]:
    val = os.getenv(name, default)
    if val is None:
        return default
    return int(val)


def config_get_bool(name: str, default: str = '') -> bool:
    return os.getenv(name, default).lower() in ['1', 'yes', 'true', 'y']

def config_get(name: str, default: Optional[Any] = None) -> str:
    return os.getenv(name, default)


class FrameBuffer:
    _dev_no: int = 0

    def __init__(self, dev_no: int):
        self._dev_no = dev_no

    @property
    def config_dir(self) -> str:
        return f"/sys/class/graphics/fb{self._dev_no}"

    @property
    def size(self) -> Tuple[int, int]:
        return cast(Tuple[int, int], tuple(self._read_ints_config("virtual_size")))

    @property
    def stride(self) -> int:
        return self._read_ints_config("stride")[0]

    @property
    def bits_per_pixel(self) -> int:
        return self._read_ints_config("bits_per_pixel")[0]

    @property
    def fb_path(self) -> str:
        return f"/dev/fb{self._dev_no}"

    def validate(self):
        assert os.path.exists(self.fb_path)
        assert os.path.exists(self.config_dir)
        assert os.access(self.fb_path, os.R_OK)
        assert os.access(self.fb_path, os.W_OK)
        assert self.stride == self.bits_per_pixel // 8 * self.size[0]

    def _read_raw_config(self, conf_name) -> str:
        config_path = os.path.join(self.config_dir, conf_name)
        with open(config_path, 'r') as fd:
            return fd.read()

    def _read_ints_config(self, config_name) -> List[int]:
        raw = self._read_raw_config(config_name)
        values = raw.split(",")
        return [int(v) for v in values]

    def __str__(self):
        return f"FrameBuffer( stride: {self.stride}, size: {self.size}, bits per pixel: {self.bits_per_pixel} )"

    def to_rgba(self, image: Image) -> bytes:
        print(image.mode, self.bits_per_pixel)
        if image.mode == "RGBA" and self.bits_per_pixel == 32:
            return image.tobytes()
        if image.mode == "RGB" and self.bits_per_pixel == 32:
            return bytes([x for r, g, b in image.getdata() for x in (255, r, g, b)])
        if image.mode == "RGB" and self.bits_per_pixel == 24:
            return image.tobytes()
        if image.mode == "RGB" and self.bits_per_pixel == 16:
            return bytes([x for r, g, b in image.getdata() for x in ((g & 0x1c) << 3 | (b >> 3), r & 0xf8 | (g >> 3))])
        print("WARNING: raw output")
        return image.tobytes()

    def show(self, image: Image):
        assert image.size <= self.size
        target = Image.new(mode="RGB", size=self.size)
        target.paste(image, ((target.size[0] - image.size[0]) // 2,
                             (target.size[1] - image.size[1]) // 2))
        bytes_ = self.to_rgba(target)
        with open(self.fb_path, 'wb') as fd:
            fd.write(bytes_)


class CoingeckoApi:
    _base_url = 'https://api.coingecko.com/api/v3'

    def __init__(self):
        self._http_session = requests.session()
        http_adapter = HTTPAdapter(max_retries=Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 502, 503, 504, 522]
        ))
        self._http_session.mount(self._base_url, http_adapter)

    def _request(self, uri, method='get', params: Optional[Dict] = None, data: Optional[Dict] = None, **kwargs):
        try:
            response = self._http_session.request(
                method=method,
                url=f'{self._base_url}/{uri}',
                data=data,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            raise

    def _request_paginated_field(
            self,
            uri: str,
            field_name: str,
            method='get',
            params: Optional[Dict] = None,
            data: Optional[Dict] = None,
            **kwargs
    ):
        params = params or {}
        params['page'] = 1
        response = self._request(
            uri=uri,
            method=method,
            params=params,
            data=data,
            **kwargs
        )

        while len(response[field_name]):
            yield from response[field_name]
            params['page'] += 1
            response = self._request(
                uri=uri,
                method=method,
                params=params,
                data=data,
                **kwargs
            )

    def _request_paginated(
            self,
            uri: str,
            method='get',
            params: Optional[Dict] = None,
            data: Optional[Dict] = None,
            **kwargs
    ):
        page = 1
        params = params or {}
        params['page'] = page
        response = self._request(
            uri=uri,
            method=method,
            params=params,
            data=data,
            **kwargs
        )

        while len(response):
            yield from response
            page += 1
            params['page'] = page
            response = self._request(
                uri=uri,
                method=method,
                params=params,
                data=data,
                **kwargs
            )

    def get_exchange_tickers(self, exchange):
        yield from self._request_paginated_field(
            uri=f'exchanges/{exchange}/tickers',
            field_name='tickers'
        )

    def get_coins(self, include_platform: bool = False):
        return self._request(
            'coins/list',
            params={
                'include_platform': str(include_platform).lower()
            }
        )

    def get_coins_details(self):
        return self._request_paginated(
            'coins'
        )

    def get_coin_by_symbol(self,
                           symbol: str,
                           include_platform: bool = False,
                           also_by_name: bool = False
                           ) -> Optional[Dict]:
        coins = self.get_coins(include_platform=include_platform)
        try:
            return [
                coin for coin in coins
                if coin['symbol'].lower() == symbol.lower() or (
                        also_by_name and coin['name'].lower() == symbol.lower()
                )
            ][0]
        except IndexError:
            return None

    def get_coin_by_name(self, name: str) -> Optional[List]:
        coins = self.get_coins()
        try:
            return [
                coin for coin in coins
                if coin['name'].lower() == name.lower()
            ][0]
        except IndexError:
            return None

    def get_simple_price(
            self,
            ids: List,
            vs_currencies: List,
            include_market_cap: bool = False,
            include_24hr_vol: bool = False,
            include_24hr_change: bool = False,
            include_last_updated_at: bool = False
    ) -> Dict:
        return self._request(
            'simple/price',
            params={
                'ids': ','.join(ids),
                'vs_currencies': ','.join(vs_currencies),
                'include_market_cap': str(include_market_cap).lower(),
                'include_24hr_vol': str(include_24hr_vol).lower(),
                'include_24hr_change': str(include_24hr_change).lower(),
                'include_last_updated_at': str(include_last_updated_at).lower(),
            }
        )

    def get_price_by_symbol(self, symbol, currency):
        coin = self.get_coin_by_symbol(symbol=symbol)
        p = self.get_simple_price(ids=[coin['id']], vs_currencies=[currency])
        return Decimal(p[coin['id']][currency])

    def supported_vs_currencies(self):
        return self._request(
            uri='simple/supported_vs_currencies'
        )

    def get_coin(self,
                 coin_id: str,
                 tickers: bool = True,
                 community_data: bool = False,
                 market_data: bool = False,
                 developer_data: bool = False,
                 localization: bool = True
                 ) -> Dict:
        return self._request(
            f'coins/{coin_id}',
            params={
                'tickers': str(tickers).lower(),
                'community_data': str(community_data).lower(),
                'localization': str(localization).lower(),
                'market_data': str(market_data).lower(),
                'developer_data': str(developer_data).lower(),
            }
        )

    def asset_platforms(self):
        return self._request('asset_platforms')

    def get_platform(self, network_id: int):
        platforms = self.asset_platforms()
        for platform in platforms:
            if platform['chain_identifier'] == network_id:
                return platform

    def get_token_address(self, token_symbol, network_id: int = 137):
        chain_name = self.get_platform(network_id=network_id)['id']
        f = self.get_coin_by_symbol(token_symbol)
        if not f:
            return None
        c = self.get_coin(coin_id=f['id'], developer_data=True)
        if not c:
            return None
        if 'platforms' not in c:
            return None
        if chain_name not in c['platforms']:
            return None
        return {
            'address': c['platforms'][chain_name],
            'symbol': c['symbol'],
            'name': c['name'],
        }

    def token_price(self, symbol: str, network_id: int, vs_currencies: List[str],
                    include_market_cap=False,
                    include_24hr_vol=False,
                    include_24hr_change=False,
                    include_last_updated_at=False
                    ):
        platform = self.get_platform(network_id=network_id)
        token = self.get_token_address(token_symbol=symbol, network_id=network_id)
        return self.token_price_simple(
            platform_id=platform['id'],
            contract_addresses=token['address'],
            vs_currencies=vs_currencies,
            include_market_cap=include_market_cap,
            include_24hr_vol=include_24hr_vol,
            include_24hr_change=include_24hr_change,
            include_last_updated_at=include_last_updated_at
        )

    def token_price_simple(
            self,
            platform_id: str,
            contract_addresses: str,
            vs_currencies: List[str],
            include_market_cap=False,
            include_24hr_vol=False,
            include_24hr_change=False,
            include_last_updated_at=False
    ):
        return self._request(
            uri=f"/simple/token_price/{platform_id}",
            params={
                'vs_currencies': ','.join(vs_currencies),
                'contract_addresses': contract_addresses,
                'include_market_cap': str(include_market_cap).lower(),
                'include_24hr_vol': str(include_24hr_vol).lower(),
                'include_24hr_change': str(include_24hr_change).lower(),
                'include_last_updated_at': str(include_last_updated_at).lower(),
            }
        )

    def get_coins_markets(
            self,
            vs_currency: str,
            symbols: Optional[List[str]] = None,
            per_page: int = 250,
            category: Optional[str] = None,
            order: Optional[str] = None,
            sparkline: bool = False,
            price_change_percentage: Optional[List[str]] = None
    ):
        price_change_percentage = price_change_percentage if price_change_percentage is not None else []
        symbols = symbols if symbols is not None else []
        yield from self._request_paginated(
            'coins/markets',
            params={
                'vs_currency': vs_currency,
                'symbols': ','.join(symbols),
                'per_page': per_page,
                'category': category,
                'order': order,
                'sparkline': str(sparkline).lower(),
                'price_change_percentage': ','.join(price_change_percentage)
            }
        )


class CryptoPrice:
    color_red = ImageColor.getrgb("#FF0000")
    color_green = ImageColor.getrgb("#32CD30")
    color_gold = ImageColor.getrgb("#FFD700")
    color_D9D9D9 = ImageColor.getrgb("#D9D9D9")
    color_404040 = ImageColor.getrgb("#404040")
    color_40FF40 = ImageColor.getrgb("#40FF40")
    color_000000 = ImageColor.getrgb("#000000")
    color_FFFFFF = ImageColor.getrgb("#ffffff")

    def __init__(self):
        self.cryptos = config_get_list("CRYPTOS", "eth,btc")
        self.output_folder = rel_path(config_get("OUTPUT_FOLDER", "../images/"))
        self.coingecko = CoingeckoApi()
        self.fb = FrameBuffer(0)
        force_screen_size = config_get_list("FORCE_SCREEN_SIZE", None)
        self.save_file = config_get_bool("SAVE_IMAGE_FILE", 'y')
        self.show_logo = config_get_bool("SHOW_LOGO", 'n')
        if force_screen_size:
            self.screen_size = tuple([int(t) for t in force_screen_size])
        else:
            self.screen_size = self.fb.size
        self.fb.validate()

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

    def createimage(self, ticker):
        pi = self.getpriceinfo(ticker)
        width, height = self.screen_size
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
        if self.save_file:
            output_file = os.path.join(self.output_folder, f"{ticker}.png")
            im.save(output_file)
        else:
            try:
                self.fb.show(im)
            except Exception as e:
                logging.exception(e)

    def create_all_images(self):
        for t in self.cryptos:
            self.createimage(t)


# TODO: con2fbmap to wanted tty
# TODO: disable cursor blink in tty ( $ tput civis > /dev/tty2 )

if __name__ == '__main__':
    CryptoPrice().create_all_images()
