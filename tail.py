from satmgr import SatManager
from center import Center

class Tail:
    def __init__(self, snode, vk2dic, bitdic, bmap):
        self.snode = snode
        self.vk2dic = vk2dic
        # vk2-bdic : all vk1s will be removed in sort_vks
        self.bdic = bitdic  
        self.sort_vks()
        self.satmgr = SatManager(self, bmap) 

    def sort_vks(self):
        self.cvks_dic = {v: {} for v in self.snode.bgrid.chvset }
        # only care about vk2s. All vk1s will become sats
        for kn, vk in self.vk2dic.items():  
            for cv in vk.cvs:
                self.cvks_dic[cv][kn] = vk
        x = 0
    # end of --- def sort_vks(self, bgrid, knss)
