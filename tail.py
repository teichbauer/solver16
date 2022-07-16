from satmgr import SatManager
from center import Center

class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        # vk2-bdic : all vk1s will be removed in sort_vks
        self.bdic = bitdic  
        self.satmgr = SatManager(self) 
        self.sort_vks(snode.bgrid, knss)

    def sort_vks(self, bgrid, knss):
        self.cvks_dic = {v: {} for v in bgrid.chvset }
        # only care about vk2s. All vk1s will become sats
        for kn in knss[2]:  
            vk = self.vk12dic[kn]
            for cv in vk.cvs:
                self.cvks_dic[cv][kn] = vk
        # the bits in all sats will make other vk2s -> vk1s -> sats
        bmap = {}
        for kn in knss[1]:
            vk1 = self.vk12dic.pop(kn)
            bit, val = tuple(vk1.dic.items())[0]  # {11:0} -> 11, 0
            self.bdic[bit].remove(vk1.kname)
            if len(self.bdic[bit]) == 0:
                del self.bdic[bit]
            sat = {bit: int(not val)}
            bit_sats = bmap.setdefault(bit, [])
            for cv in vk1.cvs:
                bit_sats.append((cv, sat))
        if len(bmap) > 0:
            self.satmgr.add(bmap)
        for bit in self.bdic:
            Center.vk2bdic.setdefault(bit,[]).append(
                (self.snode.nov, len(self.bdic[bit])))
        x = 0
    # end of --- def sort_vks(self, bgrid, knss)

    def vk2_sats(self, comm_cvs, bit, bmap, vk2):
        res = {}
        d = vk2.dic.copy()
        val = d.pop(bit)
        for cv, sat in bmap[bit]:
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
