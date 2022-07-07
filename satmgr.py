class SatManager:
    def __init__(self):
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

        while len(shared_bits) > 0:
            bit = shared_bits.pop()
            res = self.verify(bit, self.bmap[bit], bmap[bit])
            for cv in res:
                if res[cv] == None:
                    self.sdic[cv] = None
                else:
                    for xsat in res[cv]:
                        self.sdic[cv].append(xsat)
                        self.bmap.setdefault(bit,[]).append((cv, xsat))

        for bit in new_bits:
            for xcv, xsat in bmap[bit]:
                if self.sdic[xcv] != None:
                    self.sdic[xcv].append(xsat)
                    self.bmap.setdefault(bit, []).append((xcv, xsat))

