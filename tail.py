from satmgr import SatManager
from center import Center
from branch import Branch

class Tail:
    def __init__(self, snode, vk2dic, bitdic, sat_cvs_dic=None):
        self.snode = snode
        self.vk2dic = vk2dic
        self.splitbit = -1
        # vk2-bdic : all vk1s will be removed in sort_vks
        self.bdic = self.copy_bdic(bitdic)
        if sat_cvs_dic != None:  # sat_cvs_dic==None: for clone
            self.sort_vks()
            self.satmgr = SatManager(self, sat_cvs_dic) 
        if Center.root_branch == None:
            Center.root_branch = Branch()
        Center.root_branch.add_tail(self.snode.nov, self)


    def sort_vks(self):
        self.cvks_dic = {v: set([]) for v in self.snode.bgrid.chvset }
        # only care about vk2s. All vk1s will become sats
        for kn, vk in self.vk2dic.items():  
            for cv in vk.cvs:
                self.cvks_dic[cv].add(kn)
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
            self.copy_bdic(self.bdic)
        )
        ntail.splitbit = splitbit
        ntail.cvks_dic = self.copy_cvks_dic(self.cvks_dic)
        ntail.satmgr = SatManager(ntail) # self.satmgr.clone(ntail)
        ntail.satmgr.add(self.satmgr.sat_cvs_dic)
        # ntail.satmgr.add({splitbit:[(tuple(range(8)), split_sat)]})
        ntail.satmgr.add({splitbit:{split_sat[splitbit]:tuple(range(8))}})
        return ntail

    def proc_svks(self, bits):
        x = 1

    def remove_kn2_from_cvk_dic(self, cvs, kn2):
        for cv in cvs:
            if kn2 in self.cvks_dic[cv]:
                self.cvks_dic[cv].remove(kn2)

    def copy_bdic(self, bdic):
        dic = {}
        for bit, val in bdic.items():
            dic[bit] = list(val)
        return dic

    def copy_cvks_dic(self, cvks_dic):
        dic = {}
        for cv, val in cvks_dic.items():
            dic[cv] = set(val)
        return dic

    def metrics(self):
        dic = {
            'vk2s': len(self.vk2dic),
            'bdic': len(self.bdic),
        }
        for cv, lst in self.cvks_dic.items():
            dic.setdefault(cv, len(lst))
        msg = f"{self.snode.nov}/{self.splitbit}:\n"
        msg += f"{dic}, \nbmap: {self.satmgr.sat_cvs_dic}."
        return msg