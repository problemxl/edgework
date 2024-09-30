import pytest

import edgework.http_client as http_client


@pytest.fixture
def http_client_instance():
    return http_client.HttpClient()
