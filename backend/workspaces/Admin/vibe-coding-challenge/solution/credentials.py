#!/usr/bin/env python3
"""
ODPS 凭据管理模块 - 参考答案
"""

import os


def get_credentials():
    """
    读取 ODPS 连接凭据。

    返回: (access_id, secret_key, project, endpoint)
    """
    access_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "mock_access_id")
    secret_key = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "mock_secret_key")
    project = os.environ.get("ODPS_PROJECT", "icbu_ensa")
    endpoint = os.environ.get("ODPS_ENDPOINT", "http://mock-odps.aliyun-inc.com/api")

    return access_id, secret_key, project, endpoint
