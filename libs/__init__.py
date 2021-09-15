try:
    from coingecko_api import *
    from config import *
    from framebuffer import *
    from utils import *
    from fbi import *
    from script_interfaces import *
except ImportError:
    from .coingecko_api import *
    from .config import *
    from .framebuffer import *
    from .utils import *
    from .fbi import *
    from .script_interfaces import *
