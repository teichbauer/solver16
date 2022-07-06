class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        self.bdic = bitdic
        self.sdic = {}  # {cv:[<sat>,<sat>], cv:[],...}
        self.sbmap = {} # {bit:[(cv, sat), (), ..], bit:[]}
        self.sort_vks(snode.bgrid, knss)

    def sort_vks(self, bgrid, knss):
        self.cvks_dic = {v: {} for v in bgrid.chvset }
        for kn in knss[2]:
            for kn, vk in self.vk12dic.items():
                for cv in vk.cvs:
                    self.cvks_dic[cv][kn] = vk
        # vk1a=s turned to sats, and the sat-bits will make other vk2s
        # become vk1s: this will loop on, until all vk1s are gone
        # sdic = {}
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
            self.update_sdic(sdic, bmap)
            sdic, bmap = self._proc_sats(sdic, bmap)
    # end of --- def sort_vks(self, bgrid, knss)

    def update_sdic(self, sdic, bmap):
        if len(self.sbmap) == 0:
            self.sbmap = bmap
            self.sdic = sdic
            return 

        shared_bits = set(self.sbmap).intersection(bmap)
        new_bits = set(bmap) - set(self.sbmap)

        while len(shared_bits) > 0:
            bit = shared_bits.pop()
            res = self.verify(bit, self.sbmap[bit], bmap[bit])
            for cv in res:
                if res[cv] == None:
                    self.sdic[cv] = None
                else:
                    for xsat in res[cv]:
                        self.sdic[cv].append(xsat)

        for bit in new_bits:
            for xcv, xsat in bmap[bit]:
                if self.sdic[xcv] != None:
                    self.sdic[xcv].append(xsat)
    # end of --- def update_sdic(self, sdic, bmap):

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
                    d = vk2.dic.copy()
                    d.pop(sb)
                    b, v = list(d.items())[0]
                    sat = {b: int(not v)}
                    for cv in comm_cvs:
                        if kn in self.cvks_dic[cv]:
                            self.cvks_dic[cv].pop(kn)
                        new_bmap.setdefault(b, []).append((cv, sat))
                        new_sdic.setdefault(cv, []).append(sat)
        return new_sdic, new_bmap
    # end of --- def _proc_sats(self, sdic, bmap):

    def verify(self, bit, old_pairs, new_pairs):
        res = {}
        for xcv, xsat in new_pairs:     # outer-loop on new_pairs
            if xcv in res and res[xcv] == None:
                continue
            add_xsat = True
            for cv, sat in old_pairs:   # inner loop on old_pairs
                if cv == xcv:
                    add_xsat = False
                    if sat[bit] == xsat[bit]:
                        print(f"{xsat} existed for {xcv} already. not added")
                    else:
                        print(f"{xsat} conflicts on {xcv}: kill {xcv}.")
                        res[cv] = None
                        # this xcv killed cv. stop loop on old_pairs
                        # stop inner loop
                        break
                else:
                    pass
            if add_xsat:
                res.setdefault(xcv, []).append(xsat)
        return res
    # end of --- def verify(self, bit, old_pairs, new_pairs):