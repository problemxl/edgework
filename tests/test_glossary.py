from unittest.mock import Mock

import pytest

from edgework.clients.glossary_client import GlossaryClient
from edgework.models.glossary import Glossary


@pytest.fixture
def mock_http_client():
    return Mock()


@pytest.fixture
def glossary_client(mock_http_client):
    return GlossaryClient(mock_http_client)


def test_get_glossary(glossary_client, mock_http_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {
                "id": 1,
                "abbreviation": "G",
                "definition": "Goals",
                "first_season": 1917,
                "last_updated": "2023-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "abbreviation": "A",
                "definition": "Assists",
                "first_season": 1917,
                "last_updated": "2023-01-01T00:00:00Z"
            }
        ]
    }
    mock_http_client.get.return_value = mock_response

    glossary = glossary_client.get_glossary()
    assert isinstance(glossary, Glossary)
    assert len(glossary.terms) == 2
    assert glossary.terms[0].id == 1
    assert glossary.terms[0].abbreviation == "G"
    assert glossary.terms[0].definition == "Goals"
    assert glossary.terms[0].first_season == 1917
    assert glossary.terms[0].last_updated == "2023-01-01T00:00:00Z"
    assert glossary.terms[1].id == 2
    assert glossary.terms[1].abbreviation == "A"
    assert glossary.terms[1].definition == "Assists"
    assert glossary.terms[1].first_season == 1917
    assert glossary.terms[1].last_updated == "2023-01-01T00:00:00Z"
