import os
from typing import Tuple, cast, List, Optional, Any

from dotenv import load_dotenv

__all__ = ['Config']


class Config:
    def __init__(self, *args, **kwargs):
        load_dotenv(*args, **kwargs)

    def get(self, name: str, default: Optional[Any] = None) -> str:
        return os.getenv(name, default)

    def get_list(self, name: str, default: Optional[Any] = None) -> List[str]:
        val = self.get(name, default)
        if val:
            return val.split(",")
        else:
            return []

    def get_int(self, name: str, default: Optional[int] = None) -> Optional[int]:
        val = self.get(name, default)
        if val is None:
            return default
        return int(val)

    def get_bool(self, name: str, default: str = '') -> bool:
        val = self.get(name, default)
        if val is None:
            val = default
        return str(val).lower() in ['1', 'yes', 'true', 'y']

    @property
    def cryptos(self) -> List[str]:
        return self.get_list("CRYPTOS", "eth,btc")

    @property
    def output_folder(self) -> str:
        return self.rel_path(self.get("OUTPUT_FOLDER", "../images/"))

    @property
    def frame_buffer(self) -> int:
        return self.get_int('FRAME_BUFFER', 0)

    @property
    def virtual_terminal(self) -> Optional[int]:
        return self.get_int('VIRTUAL_TERMINAL', None)

    @property
    def force_screen_size(self) -> Optional[Tuple[int, int]]:
        val = self.get_list("FORCE_SCREEN_SIZE", None)
        if not val:
            return None
        assert len(val) == 2
        return cast(Tuple[int, int], tuple([int(v) for v in val]))

    @property
    def save_image_file(self) -> bool:
        return self.get_bool("SAVE_IMAGE_FILE", 'y')

    @property
    def use_fbi(self) -> bool:
        return self.get_bool("USE_FBI", 'y')

    @property
    def refresh_interval(self) -> int:
        return self.get_int("REFRESH_INTERVAL", 5)

    @staticmethod
    def rel_path(relative_path: str) -> str:
        from os.path import dirname, join, abspath, isabs
        if isabs(relative_path):
            return relative_path
        bdir = dirname(__file__)
        joinpath = join(bdir, relative_path)
        return abspath(joinpath)

    @property
    def scripts(self) -> Optional[List[Tuple[str, str]]]:
        SCRIPTS = self.get_list("SCRIPTS", None)
        if not SCRIPTS:
            return None
        return [
            cast(Tuple[str, str], tuple(s.split(":")))
            for s in SCRIPTS
        ]
