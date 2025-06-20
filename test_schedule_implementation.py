#!/usr/bin/env python3
"""
Simple test script to verify the Schedule model implementation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edgework.models.schedule import Schedule
from datetime import datetime

def test_schedule_model():
    """Test basic Schedule model functionality."""
    print("Testing Schedule model...")
    
    # Test data similar to what would come from the API
    test_data = {
        "previousStartDate": "2024-06-01T00:00:00Z",
        "games": [
            {
                "id": 2023030001,
                "gameDate": "2024-06-01",
                "startTimeUTC": "2024-06-01T20:00:00Z",
                "awayTeam": {"abbrev": "FLR", "id": 13, "score": 2},
                "homeTeam": {"abbrev": "EDM", "id": 22, "score": 3},
                "gameState": "FINAL",
                "season": 20232024
            }
        ],
        "preSeasonStartDate": "2024-09-15T00:00:00Z",
        "regularSeasonStartDate": "2024-10-01T00:00:00Z",
        "regularSeasonEndDate": "2025-04-15T00:00:00Z",
        "playoffEndDate": "2025-06-30T00:00:00Z",
        "numberOfGames": 1
    }
    
    # Test from_api method
    schedule = Schedule.from_api(None, test_data)
    
    print(f"Schedule created: {schedule}")
    print(f"Number of games: {schedule._data.get('number_of_games')}")
    print(f"Regular season start: {schedule._data.get('regular_season_start_date')}")
    print(f"Regular season end: {schedule._data.get('regular_season_end_date')}")
    
    # Test string representation
    print(f"String representation: {str(schedule)}")
    print(f"Repr: {repr(schedule)}")
    
    print("✓ Schedule model test passed!")

if __name__ == "__main__":
    test_schedule_model()
