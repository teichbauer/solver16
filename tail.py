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
    
    def clone(self, split_sat):
        new_tail = Tail(
            self.snode, 
            self.vk2dic.copy(),
            self.bdic.copy())
        new_tail.satmgr = self.satmgr.clone()
        x = 0
        return new_tail
