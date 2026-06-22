import json


class JsonParser:

    def parse(self, payload):

        if isinstance(payload, str):
            return json.loads(payload)

        return payload