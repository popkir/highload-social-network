import logging
import sys

from logging import StreamHandler, Formatter


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(threadName)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
