import binascii
import os


def generate_random_string():
    return binascii.b2a_hex(os.urandom(8)).decode("utf-8")
