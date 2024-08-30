import asyncio
from co_table import config, models

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    settings = config.get_setting()
    models.init_db(settings)
    asyncio.run(models.recreate_table())