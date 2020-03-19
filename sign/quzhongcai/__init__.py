import sys

from .main import *

logger = logging.getLogger(__name__)

logger.info("成功导入pceggs模块")

def qzc():
    token = "fb50SPzU8WxtlIg_P2fZJf0mU8ehcd9PgFpE7NmYRHQ1QRgrP1zXfetRzoQ1n3qcpUAvJU93vyOSJrb0fiNgLdMVhXw0OLgjRHHQGTjDwVg"
    a = qzc_strategy(token)
    a.run()