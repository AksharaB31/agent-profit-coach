class SupplierFeatures:

    def build(self, supplier):

        return {
            "supplier_reliability": supplier.get(
                "reliability",
                0.8
            ),
            "supplier_success_rate": supplier.get(
                "success_rate",
                0.85
            )
        }