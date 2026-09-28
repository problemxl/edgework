"""Config model backed by the Stats API ``/{lang}/config`` resource.

The local ``API_PATH`` endpoint registry in :mod:`edgework.endpoints`
describes *this library's* routes — it is not server configuration and is
never stored on the model. Server configuration comes from the documented
Stats API ``/{lang}/config`` route (registry key ``stats_config``).
"""

from edgework.clients.stats_client import StatsClient
from edgework.models.base import BaseNHLModel


class Config(BaseNHLModel):
    """
    This class represents the NHL Stats API server configuration.

    Data is lazily fetched from the documented ``/{lang}/config`` Stats API
    route the first time an attribute is accessed, following the
    :class:`~edgework.models.base.BaseNHLModel` lazy-load conventions.
    """

    def __init__(self, edgework_client, obj_id=None, lang: str = "en", **kwargs):
        """
        Initialize a Config object with dynamic attributes.

        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the config
            lang: Language code for the Stats API request (default "en").
            **kwargs: Dynamic attributes for config properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = dict(kwargs)
        self._lang = lang

    def fetch_data(self):
        """
        Fetch the server configuration from the Stats API ``/{lang}/config``
        route (registry key ``stats_config``).

        Intentional delegation: ``StatsClient.get_config`` owns the config
        route and its request construction, so the model and the client
        produce identical requests for the same language.

        Raises:
            ValueError: If the server returns a non-object JSON payload.
        """
        # Intentional delegation (see docstring): the route lives in
        # StatsClient so there is a single construction to maintain.
        payload = StatsClient(self._client).get_config(lang=self._lang)
        if not isinstance(payload, dict):
            raise ValueError(
                "Unexpected /config payload: expected a JSON object, got "
                f"{type(payload).__name__}"
            )
        # Server values win over any constructor kwargs.
        self._data = {**self._data, **payload}
        self._fetched = True
