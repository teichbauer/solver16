# from cnode import CNode


class Center:
    maxnov = 0
    satbitdic = {}  # every snode has 3x <sat-bit>:<snode> in here
    bits = set([])
    sats = []
    limit = 10
    snodes = {}
    pathroots = {}

    @classmethod
    def set_maxnov(cls, nov):
        cls.maxnov = nov
        cls.bits = set(range(nov))

    @classmethod
    def set_satbits(cls):
        """ called only after snode(last_nov) is done.
            1: unify bits from every snode's 3 sat-bits into cls.satbits
            2: group front-kns in every snode's child-vk12m
            """
        cls.satbits = set(cls.satbitdic)
        cls.tailbits = cls.bits - cls.satbits
        nov = cls.maxnov
        while nov > cls.last_nov:
            snode = cls.snodes[cls.maxnov]
            for ch, vkm in snode.vk12mdic.items():
                all_kns = set(vkm.vkdic)
                kns = set([])
                vkm.tail_kns = set([])  # vk with both bits in tail
                bs = cls.tailbits.intersection(vkm.bdic)
                for b in bs:
                    for kn in vkm.bdic[b]:
                        kns.add(kn)
                        if cls.tailbits.issuperset(vkm.vkdic[kn].bits):
                            vkm.tail_kns.add(kn)
                vkm.tailpart_kns = kns  # kn with at least 1 bit in tail
                # front_kns are vks with both bits in satbits
                vkm.front_kns = all_kns - kns
                x = 0
            nov -= 3

    @classmethod
    def sat_pathup(cls, snode):
        if snode.nov == cls.maxnov:
            return snode.solve()
        for name, vkm in snode.chdic.items():
            x = 1

        cls.sat_pathup(snode.parent)

    @classmethod
    def set_lower_snodes(cls):
        for nov, sn in cls.snodes.items():
            if nov > cls.last_nov:
                index = cls.novs.index(sn.nov)
                ns = cls.novs[index+1:]
                sn.lower_snodes = [cls.snodes[n] for n in ns]
