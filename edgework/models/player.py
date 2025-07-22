from datetime import datetime

from edgework.models.base import BaseNHLModel


class Player(BaseNHLModel):
    """Player model to store player information."""

    def __init__(self, edgework_client=None, obj_id=None, **kwargs):
        """
        Initialize a Player object with dynamic attributes.

        Args:
            edgework_client: The Edgework client (optional for player data from API)
            obj_id: The ID of the player object
            **kwargs: Dynamic attributes for player properties
        """
        super().__init__(edgework_client, obj_id)
        self._data = kwargs

        # Set the player_id as obj_id if provided in kwargs
        if "player_id" in kwargs:
            self.obj_id = kwargs["player_id"]

        # Mark as fetched since we're initializing with data
        self._fetched = True

    def __str__(self) -> str:
        """String representation showing player name and number.

        Returns:
            str: Formatted string with player name, number, and team abbreviation.
                Examples: "#97 Connor McDavid (EDM)", "Connor McDavid (EDM)",
                "#97 Connor McDavid", or "Connor McDavid".
        """
        first_name = self._data.get("first_name", "")
        last_name = self._data.get("last_name", "")
        sweater_number = self._data.get("sweater_number")
        team_abbr = self._data.get("current_team_abbr", "")

        name = f"{first_name} {last_name}".strip()
        if sweater_number and team_abbr:
            return f"#{sweater_number} {name} ({team_abbr})"
        elif team_abbr:
            return f"{name} ({team_abbr})"
        elif sweater_number:
            return f"#{sweater_number} {name}"
        else:
            return name

    def __repr__(self):
        """Developer representation of the Player object.

        Returns:
            str: Developer-friendly string representation showing the player ID.
                Example: "Player(id=8478402)".
        """
        player_id = self._data.get("player_id", self.obj_id)
        return f"Player(id={player_id})"

    def __eq__(self, other) -> bool:
        """Compare players by their player_id.

        Args:
            other: The other object to compare with.

        Returns:
            bool: True if both objects are Player instances with the same player_id,
                False otherwise.
        """
        if isinstance(other, Player):
            return self._data.get("player_id") == other._data.get("player_id")
        return False

    def __hash__(self):
        """Hash based on player_id for use in sets and dicts.

        Returns:
            int: Hash value based on the player_id.
        """
        return hash(self._data.get("player_id"))

    def fetch_data(self):
        """Fetch the data for the player from the API.

        Uses the NHL Web API player landing endpoint to get detailed player information.

        Raises:
            ValueError: If no client is available to fetch player data.
            ValueError: If no player ID is available to fetch data.
        """
        if not self._client:
            raise ValueError("No client available to fetch player data")
        if not self.obj_id:
            raise ValueError("No player ID available to fetch data")

        # Import here to avoid circular imports
        from edgework.clients.player_client import landing_to_dict

        # Call the NHL Web API player landing endpoint
        response = self._client.get(f"player/{self.obj_id}/landing", web=True)
        data = response.json()

        # Convert API response to our player dictionary format
        player_data = landing_to_dict(data)

        # Update our internal data with the fetched information
        self._data.update(player_data)

        # Mark as fetched
        self._fetched = True

    @property
    def full_name(self):
        """Get the player's full name.

        Returns:
            str: The player's full name (first name + last name).
                Example: "Connor McDavid".
        """
        first_name = self._data.get("first_name", "")
        last_name = self._data.get("last_name", "")
        return f"{first_name} {last_name}".strip()

    @property
    def name(self):
        """Alias for full_name.

        Returns:
            str: The player's full name (first name + last name).
                Example: "Connor McDavid".
        """
        return self.full_name

    @property
    def age(self):
        """Calculate player's age from birth_date.

        Returns:
            int | None: The player's age in years, or None if birth_date is not available
                or cannot be parsed.
        """
        birth_date = self._data.get("birth_date")
        if birth_date:
            if isinstance(birth_date, str):
                birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00"))
            elif isinstance(birth_date, datetime):
                pass
            else:
                return None

            today = datetime.now()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (
                today.month == birth_date.month and today.day < birth_date.day
            ):
                age -= 1
            return age
        return None
