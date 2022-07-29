from bisect import bisect
from pickle import BINBYTES
from satmgr import SatManager
from center import Center
from branch import Branch

def sat_from_pair(vk2a, vk2b):
    # dic1:{ 11:0, 21:1}, dic2:{11:1, 21:1} -> {(21,1)}
    # dic1:{ 11:0, 21:1}, dic2:{11:0, 21:0} -> {(11,0)}
    # dic1:{ 11:0, 21:1}, dic2:{11:1, 21:0} -> {}
    # dic1:{ 11:0, 21:1}, dic2:{11:0, 21:1} -> {(11,0),(21,1)}
    shared_cvs = vk2a.cvs.intersection(vk2b.cvs)
    if len(shared_cvs) == 0:
        return None
    s1 = set(tuple(vk2a.dic.items()))
    s2 = set(tuple(vk2b.dic.items()))
    s = s1.intersection(s2)
    if len(s) == 0:
        return None
    if len(s) == 2:
        raise Exception(f'{vk2a.kname} and {vk2b.kname} are duplicates')
    t = s.pop()
    return t

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
            Center.root_branch = Branch(None)
        Center.root_branch.add_tail(self.snode.nov, self)
        pairs = self.vk2_pairs()
        if pairs:
            res = [sat_from_pair(vk2a, vk2b) for vk2a, vk2b in pairs]
            x = 0


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

    def vk2_pairs(self):
        # find pairs of vk2s bitting on the same 2 bits
        pairs = []
        vks = self.vk2dic.values()
        i = 0
        while i < len(vks) - 1:
            if vks[i].bits == vks[i+1].bits:
                pairs.append((vks[i], vks[i+1]))
        
        if len(pairs) == 0:
            return None
        return pairs


    def bdic_info(self):
        bs = sorted(self.bdic)
        msg = ''
        for b in bs:
            msg += f"{b}: {self.bdic[b]}\n"
        return msg

    def cvk_info(self, cv):
        msg = f'{self.snode.nov}.{cv}({len(self.cvks_dic[cv])}):\n'
        for kn in self.cvks_dic[cv]:
            vk = self.vk2dic[kn]
            msg += f'{kn}:{vk.dic}({vk.cvs})\n'
        print(msg)
        return msg


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
        len1 = len(self.vk2dic)
        len2 = len(self.bdic)
        for cv, lst in self.cvks_dic.items():
            dic.setdefault(cv, len(lst))
        msg = f"{self.snode.nov}/{self.splitbit}: vk2dic:{len1}, 'bdic:{len2}\n"
        msg += self.bdic_info()
        msg += f"{dic}, \nbmap: {self.satmgr.sat_cvs_dic}.\n"
        return msg