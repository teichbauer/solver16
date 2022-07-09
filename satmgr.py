from vk12mgr import VK12Manager


class SatManager:
    def __init__(self, owner):
        self.owner = owner
        self.sdic = None
        self.bmap = None

    def pair_compatible(self, bit, opairs, npairs):
        res = {}
        for xcv, xsat in npairs:     # outer-loop on new_pairs
            if xcv in res and res[xcv] == None:
                continue
            add_xsat = True
            for cv, sat in opairs:   # inner loop on old_pairs
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


    def add(self, sdic, bmap):
        if not self.bmap:
            self.bmap = bmap
            self.sdic = sdic
            return

        shared_bits = set(self.bmap).intersection(bmap)
        new_bits = set(bmap) - set(self.bmap)

        if len(shared_bits) > 0:
            bmap = {}
            sdic = {}
            while len(shared_bits) > 0:
                bit = shared_bits.pop()
                kn2s = self.owner.bdic.get(bit, [])
                for kn2 in kn2s:
                    vk2 = self.owner.vk12dic[kn2]
                    sat_cvs = [p[0] for p in self.bmap[bit]]
                    comm_cvs = vk2.cvs.intersection(sat_cvs)
                    if len(comm_cvs) > 0:
                        vk2.pop_cvs(comm_cvs)
                        for cv in comm_cvs:
                            if kn2 in self.owner.cvks_dic[cv]:
                                self.owner.cvks_dic[cv].pop(kn2)
                            res = self.vk2_sats(comm_cvs, bit, vk2)
                            for cv, sat in res.items():
                                sdic.setdefault(cv, []).append(sat)
                                sat_bit = tuple(sat)[0]  # tuple({12:1}) > (12,)
                                bmap.setdefault(sat_bit, []).append((cv, sat))
            if len(bmap) > 0:
                self.add(sdic, bmap)

        for bit in new_bits:
            for xcv, xsat in bmap[bit]:
                if self.sdic[xcv] != None:
                    self.sdic[xcv].append(xsat)
                    self.bmap.setdefault(bit, []).append((xcv, xsat))

        # while len(shared_bits) > 0:
        #     bit = shared_bits.pop()
        #     res = self.verify(bit, self.bmap[bit], bmap[bit])
        #     for cv in res:
        #         if res[cv] == None:
        #             self.sdic[cv] = None
        #         else:
        #             for xsat in res[cv]:
        #                 self.sdic[cv].append(xsat)
        #                 self.bmap.setdefault(bit,[]).append((cv, xsat))


    def vk2_sats(self, comm_cvs, bit, vk2):
        res = {}
        d = vk2.dic.copy()
        val = d.pop(bit)
        for cv, sat in self.bmap[bit]:
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
