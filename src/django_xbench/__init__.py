import logging
from logging import NullHandler

__version__ = "0.1.5"

logging.getLogger(__name__).addHandler(NullHandler())
