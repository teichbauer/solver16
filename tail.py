from satmgr import SatManager

class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        self.bdic = bitdic
        self.satmgr = SatManager()
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
        sdic = {}
        for kn in knss[1]:
            vk1 = self.vk12dic.pop(kn)
            bit, val = tuple(vk1.dic.items())[0]  # {11:0} -> 11, 0
            self.bdic[bit].remove(vk1.kname)
            sat = {bit: int(not val)}
            bit_sats = bmap.setdefault(bit, [])
            for cv in vk1.cvs:
                sdic.setdefault(cv,[]).append(sat)
                bit_sats.append((cv, sat))
        while len(bmap) > 0:
            self.satmgr.add(sdic, bmap)
            sdic, bmap = self._proc_sats(sdic, bmap)
    # end of --- def sort_vks(self, bgrid, knss)

    def _proc_sats(self, sdic, bmap):
        new_bmap = {}
        new_sdic = {}
        for sb in bmap:
            kns = self.bdic[sb]
            for kn in kns:
                vk2 = self.vk12dic[kn]
                comm_cvs = vk2.cvs.intersection(sdic)
                if len(comm_cvs):
                    vk2.pop_cvs(comm_cvs)
                    for cv in comm_cvs:
                        if kn in self.cvks_dic[cv]:
                            self.cvks_dic[cv].pop(kn)
                    res = self.vk2_sats(comm_cvs, sb, bmap, vk2)
                    for cv, sat in res.items():
                        if sat:
                            new_sdic.setdefault(cv, []).append(sat)
                            b, v = tuple(sat.keys())[0]
                            new_bmap.setdefault(b, []).append((cv, sat))
        return new_sdic, new_bmap
    # end of --- def _proc_sats(self, sdic, bmap):

    def vk2_sats(self, comm_cvs, bit, bmap, vk2):
        res = { cv: None for cv in comm_cvs }
        d = vk2.dic.copy()
        val = d.pop(bit)
        for cv, sat in bmap[bit]:
            if cv in res:
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
