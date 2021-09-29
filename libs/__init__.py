try:
    from coingecko_api import *
    from config import *
    from framebuffer import *
    from utils import *
    from fbi import *
    from ifb import *
    from script_interfaces import *
    from http_client import *
except ImportError:
    from .coingecko_api import *
    from .config import *
    from .framebuffer import *
    from .utils import *
    from .fbi import *
    from .ifb import *
    from .script_interfaces import *
    from .http_client import *
