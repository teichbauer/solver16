# from cnode import CNode


class Center:
    maxnov = 0
    satbits = {}
    bits = set([])
    sats = []
    limit = 10
    snodes = {}

    @classmethod
    def set_maxnov(cls, nov):
        cls.maxnov = nov
        cls.bits = set(range(nov))

    @classmethod
    def add_satbits(cls, snode):  # bits):
        if snode.nov == cls.maxnov:
            return
        bits = snode.bgrid.bitset
        for b in bits:
            cls.satbits.setdefault(b, []).append(snode)
        cls.bits -= bits
