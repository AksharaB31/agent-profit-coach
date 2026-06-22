USED_NONCES = set()


def validate_nonce(nonce: str):

    if nonce in USED_NONCES:
        return False

    USED_NONCES.add(nonce)

    return True