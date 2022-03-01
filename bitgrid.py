from basics import set_bit
from vk12mgr import VK12Manager


class BitGrid:
    BDICS = {
        0: {2: 0, 1: 0, 0: 0},
        1: {2: 0, 1: 0, 0: 1},
        2: {2: 0, 1: 1, 0: 0},
        3: {2: 0, 1: 1, 0: 1},
        4: {2: 1, 1: 0, 0: 0},
        5: {2: 1, 1: 0, 0: 1},
        6: {2: 1, 1: 1, 0: 0},
        7: {2: 1, 1: 1, 0: 1},
    }

    def __init__(self, choice):  #
        # grid-bits: high -> low, descending order
        self.bits = tuple(reversed(choice["bits"]))  # bits [1, 6, 16]
        self.bitset = set(choice["bits"])
        self.avks = choice["avks"]
        self.covers = tuple(vk.cmprssd_value() for vk in self.avks)
        chlst = [v for v in range(8) if v not in self.covers]
        self.chvset = frozenset(chlst)

    def filter_pvs(self, pvk12m):
        " among pkv12m, see if local ch-v can be put into lnvkmdic."
        lvkmdic = {h: VK12Manager() for h in self.chvset}
        for vk in pvk12m.vkdic.values():
            # inside a pv-vkm, loop thru all vks(all vk here are vk12)
            lbs = self.bitset.intersection(vk.bits)
            if len(lbs) == 0:
                for ch in self.chvset:
                    if ch in lvkmdic:
                        lvkmdic[ch].add_vk(vk)
                        if not lvkmdic[ch].valid:
                            del lvkmdic[ch]
            else:
                cvs, outdic = self.cvs_and_outdic(vk)
                if len(lbs) == 1:
                    b = lbs.pop()  # vk.bits[0]
                    if vk.nob == 1:
                        for lv in self.chvset:  # ch-head is covered by cvs,
                            if lv in lvkmdic:
                                # then this lv should not be pv-vkm's path down
                                if lv in cvs:
                                    del lvkmdic[lv]
                                # else: lv isn't in cvs, lv makes vk a NOT-hit,
                                # so, this vk shouldn't be added to pv-path
                                # although this pv-path shouldn't be remvoed
                    else:  # vk.nob == 2, with 1 bit in self.bits
                        for lv in self.chvset:
                            if lv in lvkmdic:
                                # 1 bit from vk is hit: drop the bit vk2->vk1
                                if lv in cvs:
                                    vkx = vk.clone([b])  # clone with dropped b
                                    lvkmdic[lv].add_vk1(vkx)
                                    if not lvkmdic[lv].valid:
                                        del lvkmdic[lv]
                                 # else: lv not in cvs of vk: this vk is
                                 # for sure a NOT-hit:this vk will not be added
                else:  # lbs length: 2
                    for lv in self.chvset:
                        if lv in lvkmdic:
                            if lv in cvs:
                                del lvkmdic[lv]
        return lvkmdic

    def grid_sat(self, val):
        return {self.bits[b]: v for b, v in self.BDICS[val].items()}

    def hit(self, satdic):
        for avk in self.avks:
            if avk.hit(satdic):
                return True
        return False

    def reduce_cvs(self, vk12m):
        """ for every vk in vk12m.vkdic, if vk is totally within grid,
            """
        cvs_set = set(self.chvset)
        kns = vk12m.kn1s + vk12m.kn2s
        for kn in kns:
            vk = vk12m.vkdic[kn]
            if self.bitset.issuperset(vk.bits):
                cvs, dummy = self.cvs_and_outdic(vk)
                for cv in cvs:
                    if cv in cvs_set:
                        cvs_set.remove(cv)
                if len(cvs_set) == 0:
                    break
        return cvs_set

    def vary_1bit(self, val, bits, cvs):
        if len(bits) == 0:
            cvs.append(val)
        else:
            bit = bits.pop()
            for v in (0, 1):
                nval = set_bit(val, bit, v)
                if len(bits) == 0:
                    cvs.append(nval)
                else:
                    self.vary_1bit(nval, bits[:], cvs)
        return cvs

    def get_vk12bits(self, snode):
        self.vk12bitdic = {}
        self.vk12sumbits = set([])
        for vk in snode.sumvk12dic.values():
            self.vk12sumbits.update(vk.bits)
            for b in vk.bits:
                self.vk12bitdic.setdefault(b, set([])).add(vk.kname)
        self.vk12dic_bits = {k: set([]) for k in snode.vk12mdic}
        for k in snode.vk12mdic:
            for vk in snode.vk12mdic[k].vkdic.values():
                self.vk12dic_bits[k].update(vk.bits)
        x = 1

    def cvs_and_outdic(self, vk):
        g = [2, 1, 0]
        # for a vk touched by grid-bits (1 or 2 bits)
        # cvs may contain 2 or 4 values in it
        cvs = []
        # vk's dic values within self.grid-bits, forming a value in (0..7)
        # example: grids: (16,6,1), vk.dic:{29:0, 16:1, 1:0} has
        # {16:1,1:0} iwithin grid-bits, forming a value of 4/1*0 where
        # * is the variable value taking 0/1 - that will be set by
        # self.vary_1bit call, but for to begin, set v to be 4/100
        v = 0
        out_dic = {}  # dic with 1 or 2 k/v pairs, for making vk12
        for b in vk.dic:
            if b in self.bits:
                ind = self.bits.index(b)  # self.bits: descending order
                g.remove(ind)
                v = set_bit(v, ind, vk.dic[b])
            else:
                out_dic[b] = vk.dic[b]
        odic_ln = len(out_dic)
        if odic_ln == 0:  # vk is covered by grid-3 bits totally
            # there is no rvk (None)
            if vk.nob == 3:   # cvs is a single value, not a list
                cvs = vk.cmprssd_value()
            elif vk.nob < 3:  # cvs is a list of values
                cvs = self.vary_1bit(v, g, cvs)  # TB verified
            return cvs, None

        if odic_ln == 3:
            raise Exception("vk3!")

        if odic_ln != vk.nob:
            # get values of all possible settings of untouched bits in g
            cvs = self.vary_1bit(v, g, cvs)
            cvs.sort()
        return cvs, out_dic
