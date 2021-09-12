import glob
import os
import signal
import tempfile
import time
from typing import Optional
from .ifb import iFB

import psutil

__all__ = ['Fbi']

from PIL import Image


class Fbi(iFB):

    def __init__(self, folder: str, dev_no: int, vt: Optional[int] = None, timeout: int = 5):
        super().__init__(dev_no=dev_no, vt=vt)
        self._folder = folder.rstrip("/")
        self._timeout = timeout

    def start(self):
        os.system(
            " ".join([
                "fbi",
                "--vt", f"{self._vt}",
                "--autozoom",
                "--timeout", f"{self._timeout}",
                "--device", self.fb_path,
                "--noreadahead",
                "--cachemem", "0",
                "--noverbose",
                "--norandom",
                f"{self._folder}/*.png"
            ])
        )

    def show(self, im: Image):
        with tempfile.NamedTemporaryFile(suffix=".png") as fp:
            im.save(fp.file, format="PNG")
            self.stop()
            fp.flush()
            os.chmod(fp.name, 0o777)
            os.system(
                " ".join([
                    "fbi",
                    "--vt", f"{self._vt}",
                    "--autozoom",
                    "--device", self.fb_path,
                    "--noreadahead",
                    "--cachemem", "0",
                    "--noverbose",
                    fp.name
                ])
            )
            time.sleep(1)

    def stop(self):
        pid = self.get_pid()
        if pid is None:
            return
        os.kill(pid, signal.SIGTERM)

    def get_pid(self) -> Optional[int]:
        for proc in psutil.process_iter():
            if "fbi" == proc.name():
                return proc.pid

    def auto(self):
        while True:
            self.start()
            time.sleep(self.file_count() * self._timeout + 1)
            self.stop()

    def file_count(self) -> int:
        return len(glob.glob(os.path.join(self._folder, "*.png")))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __del__(self):
        try:
            self.stop()
        except:
            pass
