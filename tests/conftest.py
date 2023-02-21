import os

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {
        "DATA_WAREHOUSE_USER": "user123",
        "DATA_WAREHOUSE_PASSWORD": "pass123",
        "DATA_WAREHOUSE_HOST": "http://localhost/",
        "DATA_WAREHOUSE_PORT": "1234",
        "DATA_WAREHOUSE_SID": "database5678",
        "LOG_LEVEL": "INFO",
        "S3_BUCKET_NAME": "patronload",
        "S3_PATH": "/test/example/",
        "WORKSPACE": "test",
    }
    yield


@pytest.fixture()
def runner():
    return CliRunner()
