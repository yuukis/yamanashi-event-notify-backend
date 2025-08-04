import base64
import ecdsa


def generate_vapid_keypair():
    """
    Generate a new set of encoded key-pair for VAPID
    """
    pk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    vk = pk.get_verifying_key()

    return {
        'private_key': base64.urlsafe_b64encode(pk.to_string()).strip(b"="),
        'public_key': base64.urlsafe_b64encode(b"\x04" + vk.to_string()).strip(b"=")
    }


if __name__ == '__main__':
    keys = generate_vapid_keypair()
    print(f"VAPID_PRIVATE_KEY={keys['private_key'].decode()}")
    print(f"VAPID_PUBLIC_KEY={keys['public_key'].decode()}")
