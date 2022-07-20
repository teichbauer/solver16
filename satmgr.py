from vk12mgr import VK12Manager
from basics import vk1_to_sat

class SatManager:
    def __init__(self, owner, bmap=None):
        self.owner = owner
        self.bmap = {}
        if bmap:
            self.add(bmap)

    def add(self, bmap):
        if len(self.bmap) == 0:
            new_bits = set(bmap)
        else:
            new_bits = set(bmap) - set(self.bmap)
        for bit in new_bits:
            for xcv, xsat in bmap[bit]:
                self.bmap.setdefault(bit, []).append((xcv, xsat))
        
        bmap = self.expand_bmap(new_bits)
        if len(bmap) > 0:
            self.add(bmap)

    def clone(self):
        new_satmgr = SatManager(self.owner)
        new_satmgr.add(self.bmap)
        return new_satmgr


    def expand_bmap(self, bits):
        bmap = {}
        while len(bits) > 0:  # bits is a set
            bit = bits.pop()
            # kn2s = bdic.get(bit, []) may ge modified, so use a copy
            kn2s = self.owner.bdic.get(bit, []).copy()
            if len(kn2s) == 0:
                continue
            cvs_sat_lst = [p for p in self.bmap[bit]]
            for kn2 in kn2s:
                vk2 = self.owner.vk2dic[kn2]
                for xcvs, xsat in cvs_sat_lst:
                    comm_cvs = vk2.cvs.intersection(xcvs)
                    if len(comm_cvs) > 0:
                        vk2.pop_cvs(comm_cvs)
                        if len(vk2.cvs) == 0:
                            self.owner.remove_vk2(vk2)
                        for cv in comm_cvs:
                            if kn2 in self.owner.cvks_dic[cv]:
                                self.owner.cvks_dic[cv].pop(kn2)
                        if vk2.dic[bit] != xsat[bit]:
                            continue
                        vk1 = vk2.clone([bit])
                        nsat = vk1_to_sat(vk1)
                        bmap.setdefault(vk1.bits[0],[]).append((comm_cvs, nsat))
        return bmap

