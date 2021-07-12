import logging

import coloredlogs
from pymongo import MongoClient

log = logging.getLogger("Database wrapper")
coloredlogs.install(logger=log)


class ErinDatabase(MongoClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
