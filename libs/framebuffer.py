import logging
import os
import sys
from fcntl import ioctl

from PIL import Image

__all__ = ['STDIN_FILENO', 'VT_WAITACTIVE', 'VT_ACTIVATE', 'FrameBuffer']

from .ifb import iFB

STDIN_FILENO = 0
VT_WAITACTIVE = 0x5607
VT_ACTIVATE = 0x5606


class FrameBuffer(iFB):

    def __str__(self):
        return f"FrameBuffer( stride: {self.stride}, size: {self.size}, bits per pixel: {self.bits_per_pixel} )"

    def to_rgba(self, image: Image) -> bytes:
        if image.mode == "RGBA" and self.bits_per_pixel == 32:
            return image.tobytes()
        if image.mode == "RGB" and self.bits_per_pixel == 32:
            return bytes([x for r, g, b in image.getdata() for x in (255, r, g, b)])
        if image.mode == "RGB" and self.bits_per_pixel == 24:
            return image.tobytes()
        if image.mode == "RGB" and self.bits_per_pixel == 16:
            return bytes([x for r, g, b in image.getdata() for x in ((g & 0x1c) << 3 | (b >> 3), r & 0xf8 | (g >> 3))])

        logging.warning("frame buffer using raw output")
        return image.tobytes()

    def show(self, image: Image, timeout: int):
        assert image.size <= self.size
        target = Image.new(mode="RGB", size=self.size)
        target.paste(image, ((target.size[0] - image.size[0]) // 2,
                             (target.size[1] - image.size[1]) // 2))
        bytes_ = self.to_rgba(target)
        with open(self.fb_path, 'wb') as fd:
            fd.write(bytes_)

    def hide_vt_cursor(self):
        if not self.vt_path:
            return
        with open(self.vt_path, 'w') as fp:
            fp.write("\x1b[?25l")

    def show_vt_cursor(self):
        if not self.vt_path:
            return
        with open(self.vt_path, 'w') as fp:
            fp.write("\x1b[?25h")

    def fork(self):
        pid = os.fork()
        if pid != 0:
            sys.exit()
        os.setsid()

    def activate_tty(self):
        # os.chown(self.vt_path, os.getuid(), os.getgid())
        self._vt_fp = self._activate_tty(self._vt)

    def _activate_tty(self, vtno: int) -> int:
        fp = os.open(self.vt_path, os.O_RDWR)
        ioctl(fp, VT_ACTIVATE, vtno)
        ioctl(fp, VT_WAITACTIVE, vtno)
        return fp

    def __enter__(self):
        if self._vt is None:
            return self
        try:
            self.activate_tty()
        except Exception as e:
            logging.error("error activating tty:")
            logging.exception(e)

        self.hide_vt_cursor()

        try:
            os.system(f'con2fbmap {self._dev_no} {self._vt}')
        except Exception as e:
            logging.exception(e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import os
        self.show_vt_cursor()
        try:
            if self._vt_fp is not None:
                os.close(self._vt_fp)
        except Exception as e:
            logging.exception(e)
        try:
            os.system(f'con2fbmap 0 {self._vt}')
        except Exception as e:
            logging.exception(e)
