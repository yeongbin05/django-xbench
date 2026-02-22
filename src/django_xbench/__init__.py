import logging
from logging import NullHandler

__version__ = "0.1.6"

logging.getLogger(__name__).addHandler(NullHandler())
