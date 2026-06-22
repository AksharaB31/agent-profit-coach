class BookingLoader:

    def load_agent_bookings(self, agent_id):

        return [
            {
                "booking_id": "BK001",
                "profit": 1200,
                "origin": "DEL",
                "destination": "DXB"
            },
            {
                "booking_id": "BK002",
                "profit": 1800,
                "origin": "BOM",
                "destination": "SIN"
            }
        ]