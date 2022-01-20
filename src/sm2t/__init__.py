#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from .utils import *

from dotenv import load_dotenv
load_dotenv("../.env", verbose=True)

import logging.config
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

