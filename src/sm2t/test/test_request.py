#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test requests to running API"""

import requests

BASE = "http://localhost:81/api/v1/"


def test_request_with_data():
    """Test if request within region with data returns data"""
    response = requests.get(BASE + "traffic/csv?bbox=13.3472,52.499,13.4117,52.5304")
    assert response.status_code == 200
    assert len(response.text) > 100


def test_request_without_data():
    """Test if request outside region with data returns no data"""
    response = requests.get(BASE + "traffic/csv?bbox=11.32,50.8,11.35,50.82")
    assert response.status_code == 200
    assert len(response.text) < 100
