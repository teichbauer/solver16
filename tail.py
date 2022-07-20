from satmgr import SatManager
from center import Center

class Tail:
    def __init__(self, snode, vk2dic, bitdic, bmap=None):
        self.snode = snode
        self.vk2dic = vk2dic
        # vk2-bdic : all vk1s will be removed in sort_vks
        self.bdic = bitdic  
        if bmap != None:  # bmap==None: for clone
            self.sort_vks()
            self.satmgr = SatManager(self, bmap) 

    def sort_vks(self):
        self.cvks_dic = {v: {} for v in self.snode.bgrid.chvset }
        # only care about vk2s. All vk1s will become sats
        for kn, vk in self.vk2dic.items():  
            for cv in vk.cvs:
                self.cvks_dic[cv][kn] = vk
        x = 0

    def remove_vk2(self, vk2):
        # vk2.cvs became empty, remove it from vk2dic, and bdic
        kn = vk2.kname
        self.vk2dic.pop(kn, None)
        for b in vk2.bits:
            if kn in self.bdic[b]:
                self.bdic[b].remove(kn)
                if len(self.bdic[b]) == 0:
                    del self.bdic[b]
            
    
    def clone(self, split_sat, splitbit):
        ntail = Tail(
            self.snode, 
            self.vk2dic.copy(),
            self.bdic.copy())
        ntail.satmgr = self.satmgr.clone()
        bmap = {splitbit:[((0,1,2,3,4,5,6,7), split_sat)]}
        ntail.satmgr.add(bmap)
        x = 0
        return ntail
