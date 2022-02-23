#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import os


def get_engine(user, passwd, host, port, db):
    """
    Create SQLalchemy engine
    :param user: Username
    :param passwd: Password
    :param host: Host
    :param port: Port
    :param db: Database name
    :return:
    """
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return engine


def get_engine_from_environment():
    """
    Create an engine from the settings in the environment variables
    :return:
    """
    return get_engine(
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["HOST"],
        os.environ["POSTGRES_PORT"],
        os.environ["POSTGRES_DB"],
    )


def get_session(engine=None):
    """Creates a SQLalchemy session"""
    if not engine:
        engine = get_engine_from_environment()
    session = sessionmaker(bind=engine)()
    return session
