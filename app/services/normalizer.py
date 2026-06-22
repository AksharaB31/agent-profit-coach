class Normalizer:

    @staticmethod
    def normalize_price(
        price,
        max_price=50000
    ):

        return round(
            min(price / max_price, 1),
            2
        )

    @staticmethod
    def normalize_duration(
        duration,
        max_duration=1000
    ):

        return round(
            1 - min(duration / max_duration, 1),
            2
        )

    @staticmethod
    def normalize_profit(
        profit,
        max_profit=5000
    ):

        return round(
            min(profit / max_profit, 1),
            2
        )