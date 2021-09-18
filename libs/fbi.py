import glob
import logging
import os
import signal
import tempfile
import time
from typing import Optional

import psutil
from PIL import Image

from .ifb import iFB

__all__ = ['Fbi']


class Fbi(iFB):

    def __init__(self, folder: str, dev_no: int, vt: Optional[int] = None, timeout: int = 5):
        super().__init__(dev_no=dev_no, vt=vt)
        self._folder = folder.rstrip("/")
        self._timeout = timeout

    def start(self):
        cmd = " ".join([
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
        logging.info(cmd)
        os.system(cmd)

    def show(self, im: Image, timeout: int):
        with tempfile.NamedTemporaryFile(suffix=".png") as fp:
            im.save(fp.file, format="PNG")
            # self.stop()
            fp.flush()
            os.chmod(fp.name, 0o777)
            cmd = " ".join([
                "fbi",
                "--vt", f"{self._vt}",
                "--autozoom",
                "--device", self.fb_path,
                "--noreadahead",
                "--cachemem", "0",
                "--noverbose",
                "-1",
                "-timeout", f"{timeout}",
                fp.name
            ])
            logging.info(cmd)
            os.system(cmd)
            time.sleep(0.05)

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
