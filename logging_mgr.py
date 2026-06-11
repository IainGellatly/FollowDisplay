# Logger
#
# Version 1.0
# 08-Apr-2026
#
# logging manager

import logging
from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger('client')

# end of file