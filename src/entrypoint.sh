#!/usr/bin/env bash
python ./populate_database.py
uwsgi uwsgi.ini
