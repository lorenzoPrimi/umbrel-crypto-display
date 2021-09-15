from decimal import Decimal
from typing import List, Optional, Dict

import cachetools
import requests as requests
from cachetools import cached, TTLCache
from requests.adapters import HTTPAdapter, Retry

cache = TTLCache(ttl=60 * 10, maxsize=12800)

__all__ = ['CoingeckoApi']


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

    @cached(cache, key=cachetools.keys.hashkey)
    def get_exchange_tickers(self, exchange):
        yield from self._request_paginated_field(
            uri=f'exchanges/{exchange}/tickers',
            field_name='tickers'
        )

    @cached(cache, key=cachetools.keys.hashkey)
    def get_coins(self, include_platform: bool = False):
        return self._request(
            'coins/list',
            params={
                'include_platform': str(include_platform).lower()
            }
        )

    @cached(cache)
    def get_coins_details(self):
        return self._request_paginated(
            'coins'
        )

    @cached(cache, key=cachetools.keys.hashkey)
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

    @cached(cache, key=cachetools.keys.hashkey)
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

    @cached(cache)
    def supported_vs_currencies(self):
        return self._request(
            uri='simple/supported_vs_currencies'
        )

    @cached(cache, key=cachetools.keys.hashkey)
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

    @cached(cache, key=cachetools.keys.hashkey)
    def asset_platforms(self):
        return self._request('asset_platforms')

    @cached(cache, key=cachetools.keys.hashkey)
    def get_platform(self, network_id: int):
        platforms = self.asset_platforms()
        for platform in platforms:
            if platform['chain_identifier'] == network_id:
                return platform

    @cached(cache, key=cachetools.keys.hashkey)
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
