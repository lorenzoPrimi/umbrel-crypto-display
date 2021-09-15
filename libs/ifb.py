import os
from typing import Optional, List, cast, Tuple

from PIL import Image

__all__ = ['iFB']


class iFB:
    _dev_no: int = 0
    _vt: Optional[int] = None
    _vt_fp: Optional[int] = None

    def __init__(self, dev_no: int, vt: Optional[int] = None):
        self._dev_no = dev_no
        self._vt = vt

    def _read_ints_config(self, config_name) -> List[int]:
        raw = self._read_raw_config(config_name)
        values = raw.split(",")
        return [int(v) for v in values]

    def _read_raw_config(self, conf_name) -> str:
        config_path = os.path.join(self.config_dir, conf_name)
        with open(config_path, 'r') as fd:
            return fd.read()

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

    @property
    def vt_path(self) -> Optional[str]:
        if self._vt is None:
            return None
        return f'/dev/tty{self._vt}'

    def validate(self):
        assert os.path.exists(self.fb_path)
        assert os.path.exists(self.config_dir)
        assert os.access(self.fb_path, os.R_OK)
        assert os.access(self.fb_path, os.W_OK)
        assert self.stride == self.bits_per_pixel // 8 * self.size[0]

    def show(self, im: Image, timeout: int):
        pass
