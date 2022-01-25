#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__init__"""

from dotenv import load_dotenv
import logging.config

load_dotenv("../.env", verbose=True)

try:
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
except KeyError:
    print("logging could not be initialized.")
