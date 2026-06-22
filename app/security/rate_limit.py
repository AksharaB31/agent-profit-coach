from time import time


REQUEST_LOG = {}


def rate_limit(client_id, limit=60):

    current_time = int(time())

    if client_id not in REQUEST_LOG:
        REQUEST_LOG[client_id] = []

    REQUEST_LOG[client_id] = [
        t for t in REQUEST_LOG[client_id]
        if current_time - t < 60
    ]

    if len(REQUEST_LOG[client_id]) >= limit:
        return False

    REQUEST_LOG[client_id].append(current_time)

    return True