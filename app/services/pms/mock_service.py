from datetime import datetime, timedelta
from typing import List

class MockPMSService:
    """
    Simulates interaction with a Practice Management System (e.g. OpenDental).
    """
    
    @staticmethod
    def get_available_slots() -> List[datetime]:
        """
        Returns a hardcoded list of available slots for the next day.
        """
        base_time = datetime.now() + timedelta(days=1)
        base_time = base_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        slots = []
        # Create 5 hourly slots
        for i in range(5):
            slots.append(base_time + timedelta(hours=i))
            
        return slots
