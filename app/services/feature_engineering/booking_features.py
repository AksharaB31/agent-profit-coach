class BookingFeatures:

    def build(self, booking):

        return {
            "profit": booking.get("profit", 0),
            "route": (
                booking["origin"] +
                "-" +
                booking["destination"]
            )
        }