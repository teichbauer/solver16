from center import Center
from basics import vk1_to_sat

class SatManager:
    def __init__(self, owner, bmap=None):
        self.owner = owner
        self.bmap = {}
        if bmap:
            self.add(bmap)

    def add(self, bmap):
        for bit in bmap:
            for xcvs, xsat in bmap[bit]:
                old_lst = self.bmap.setdefault(bit,[])
                ind = -1
                ncvs = None
                for index, (ycvs, ysat) in enumerate(old_lst):
                    if xsat == ysat:
                        ind = index
                        ncvs = tuple(set(xcvs).union(ycvs))
                if ind == -1:
                    self.bmap.setdefault(bit,[]).append((xcvs, xsat))
                else:  # there has bee xsat on ind: set the unioned ncvs to it
                    self.bmap[bit][ind] = (ncvs, xsat)
        
        bmap = self.expand_bmap(list(bmap))
        if len(bmap) > 0:
            self.add(bmap)


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
                        # since vk2 in vk2dic is a ref, and here the vk2
                        # is modified, replace this vk2 with a clone, so tha
                        # the modification will not harm the original vk2
                        vk2_clone = vk2.clone()
                        self.owner.vk2dic[kn2] = vk2_clone
                        vk2_clone.pop_cvs(comm_cvs)
                        if len(vk2_clone.cvs) == 0:
                            self.owner.remove_vk2(vk2_clone)

                        self.owner.remove_kn2_from_cvk_dic(comm_cvs, kn2)

                        if vk2_clone.dic[bit] != xsat[bit]:
                            continue
                        vk1 = vk2_clone.clone([bit])
                        nsat = vk1_to_sat(vk1)
                        bmap.setdefault(vk1.bits[0],[]).append((comm_cvs, nsat))
        return bmap

