from collections import defaultdict


class MetricsCollector:

    def __init__(self):
        self.metrics = defaultdict(int)

    def increment(self, metric_name: str):
        self.metrics[metric_name] += 1

    def get_metrics(self):
        return dict(self.metrics)


metrics = MetricsCollector()