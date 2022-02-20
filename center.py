import json


class Center:
    maxnov = 0
    satbits = set([])
    bits = set([])
    sats = []
    limit = 10
    snodes = {}

    @classmethod
    def set_maxnov(cls, nov):
        cls.maxnov = nov
        cls.bits = set(range(nov))

    @classmethod
    def add_satbits(cls, bits):
        cls.satbits.update(bits)
        cls.bits -= bits
