from typing import Optional, Dict

import requests
from requests.adapters import HTTPAdapter, Retry

__all__ = ['HttpClient']


class HttpClient:
    _allowed_error_codes = []

    def __init__(self, *args, base_url, allowed_error_codes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_url = base_url
        self._http_session = requests.session()
        http_adapter = HTTPAdapter(max_retries=Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 502, 503, 504, 522]
        ))
        self._http_session.mount(self._base_url, http_adapter)
        if allowed_error_codes:
            self._allowed_error_codes = allowed_error_codes

    def _request(self, uri="", method='get', params: Optional[Dict] = None, data: Optional[Dict] = None, **kwargs):
        try:
            response = self._http_session.request(
                method=method,
                url=f'{self._base_url}/{uri}',
                data=data,
                params=params,
                **kwargs
            )
            if response.status_code not in self._allowed_error_codes:
                response.raise_for_status()
            return response.json()
        except Exception:
            raise
