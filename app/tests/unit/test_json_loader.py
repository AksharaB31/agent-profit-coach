from app.services.json_loader.json_parser import (
    JsonParser
)


def test_json_parser():

    parser = JsonParser()

    payload = '{"name":"test"}'

    result = parser.parse(payload)

    assert result["name"] == "test"