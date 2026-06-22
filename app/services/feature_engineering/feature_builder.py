from app.services.feature_engineering.booking_features import BookingFeatures
from app.services.feature_engineering.itinerary_features import ItineraryFeatures
from app.services.feature_engineering.market_features import MarketFeatures
from app.services.feature_engineering.supplier_features import SupplierFeatures


class FeatureBuilder:

    def __init__(self):

        self.booking_features = BookingFeatures()
        self.itinerary_features = ItineraryFeatures()
        self.market_features = MarketFeatures()
        self.supplier_features = SupplierFeatures()

    def build(
        self,
        booking,
        itinerary,
        supplier
    ):

        features = {}

        features.update(
            self.booking_features.build(booking)
        )

        features.update(
            self.itinerary_features.build(itinerary)
        )

        features.update(
            self.market_features.build()
        )

        features.update(
            self.supplier_features.build(supplier)
        )

        return features