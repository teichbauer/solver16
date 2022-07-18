from vk12mgr import VK12Manager


class SatManager:
    def __init__(self, owner, bmap=None):
        self.owner = owner
        self.sdic = {}
        self.bmap = {}
        if bmap:
            self.add(bmap)

    def expand_bmap(self, bits):
        bmap = {}
        sdic = {}
        while len(bits) > 0:  # bits is a set
            bit = bits.pop()
            kn2s = self.owner.bdic.get(bit, [])
            if len(kn2s) == 0:
                continue
            sat_cvs = [p[0] for p in self.bmap[bit]]
            for kn2 in kn2s:
                vk2 = self.owner.vk12dic[kn2]
                comm_cvs = vk2.cvs.intersection(sat_cvs)
                if len(comm_cvs) > 0:
                    vk2.pop_cvs(comm_cvs)
                    for cv in comm_cvs:
                        if kn2 in self.owner.cvks_dic[cv]:
                            self.owner.cvks_dic[cv].pop(kn2)
                    res = self.vk2_sats(comm_cvs, bit, vk2)
                    for cv, sat in res.items():
                        sdic.setdefault(cv, []).append(sat)
                        sat_bit = tuple(sat)[0]  # tuple({12:1}) > (12,)
                        bmap.setdefault(sat_bit, []).append((cv, sat))
        return bmap

    def add(self, bmap):
        new_bits = set(bmap) - set(self.bmap)
        for bit in new_bits:
            for xcv, xsat in bmap[bit]:
                self.sdic.setdefault(xcv,[]).append(xsat)
                self.bmap.setdefault(bit, []).append((xcv, xsat))
        
        bmap = self.expand_bmap(new_bits)
        if len(bmap) > 0:
            self.add(bmap)
        x = 1


    def vk2_sats(self, comm_cvs, bit, vk2):
        res = {}
        d = vk2.dic.copy()
        val = d.pop(bit)
        for cv, sat in self.bmap[bit]:
            if cv in comm_cvs:
                # val == sat[bit] means: vk2.dic[bit] agrees with sat, so that
                # vk2 -> vk1.dic[other-bit] becomes a new-sat = {b: (not val)}
                # which will be added to sdic/bmap
                # -------------------------------------------------------------
                # in case val != sat[bit], the sat already makes vk2 a non-hit:
                # this vk2 should not be in cvks_dic[cv]
                if sat[bit] == val:
                    b, v = tuple(d.items())[0]
                    res[cv] = {b: int(not(v))}
        return res
    # end of ---  def vk2_sats(self, comm_cvs, bit, bmap, vk2):
