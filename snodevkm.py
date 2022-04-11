from center import Center


class SnodeVkm:
    def __init__(self, sat2, nov):
        self.nov = nov
        self.sat2 = sat2
        self.chvkdic = sat2.chvkdic
        self.kn1s = set([])
        self.kn2s = set([])
        self.bdic = sat2.bdict
        self.vk12dic = sat2.vk12dic
        for kn, vk in self.vk12dic.items():
            if vk.nob == 1:
                self.kn1s.add(kn)
            else:
                self.kn2s.add(kn)
            for b in vk.bits:
                self.bdic.setdefault(b, []).append(kn)

    def sort_chvkdic(self):
        for kn, vk in self.vk12dic.items():
            if vk.nob == 1:
                self.add_vk1(vk)
            else:
                self.add_vk2(vk)

    def add_vk1(self, vk):
        bit = vk.bits[0]
        kns = self.bdic[bit][:]
        # kns for loop usage. can't use knames directly, for knames may change
        for kn in kns:
            if kn in self.kn1s:
                # bdic may have been updated, so kn may no more be
                # in there on this bit any more
                if kn not in self.bdic[bit]:
                    continue
                vk1 = self.vk12dic[kn]
                if vk1.dic[bit] != vk.dic[bit]:
                    self.add_licker_vk1(vk, vk1)
                else:  # self.vk12dic[kn].dic[bit] == vk.dic[bit]
                    self.add_duplicated_vk1(vk, vk1)
            elif kn in self.kn2s:
                vk2 = self.vk12dic[kn]
                if bit in vk2.bits:
                    if vk2.dic[bit] == vk.dic[bit]:
                        # a vk2 has the same v on this bit:
                        # remove vk2 from vs vk is on
                        self.add_shadowing(vk, self.vk12dic[kn])
                    else:  # vk2 has diff val on this bit
                        # drop a bit:it becomes vk1, add it back as vk1
                        self.add_cutting(vk, self.vk12dic[kn])
                else:
                    self.add_vk(vk)
                    self.kn1s.add(vk.kname)
    # ---- end of def add_vk1(self, vk) -----------------------------

    def add_vk2(self, vk):
        for kn in self.kn1s:  # any existing vk1 covers vk?
            b = self.vk12dic[kn].bits[0]
            if b in vk.bits:
                self.add_shadowed(vk, self.vk12dic[kn], b)
        # find vk2s withsame bits
        pair_kns = []
        for kn in self.kn2s:
            if self.vk12dic[kn].bits == vk.bits:
                pair_kns.append(kn)
        bs = vk.bits
        if len(pair_kns) == 0:  # there is no pair
            for b in bs:
                self.bdic.setdefault(b, []).append(vk.kname)
            self.kn2s.append(vk.kname)
            self.add_vk(vk)
        else:
            for pk in pair_kns:
                pvk = self.vk12dic[pk]
                if vk.dic[bs[0]] == pvk.dic[bs[0]]:
                    if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                        self.add_duplicate(vk, pvk)
                    else:  # b0: same value, b1 diff value
                        self.add_dupbits_compliment(vk, pvk, bs[1])
                elif vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    self.add_dupbits_compliment(vk, pvk, bs[0])
        return True
    # ---- end of def add_vk2(self, vk): --------------------------

    ##########################################################################
    def add_vk(self, vk):
        for v in vk.cvs:
            if v in self.chvkdic and vk not in self.chvkdic[v]:
                self.chvkdic[v].append(vk)

    def add_duplicate(self, vk, old_vk):
        for v in vk.cvs:
            if v not in old_vk.cvs:
                self.chvkdic[v].append(vk)

    def add_dupbits_compliment(self, vk, old_vk, diff_v_bit):
        # vk and old_vk are both vk2 (nob==2)
        # vk and old_vk have the same bits, and
        # vk.dic[same_bit] == old_vk.dic[same_bit]
        # vk.dic[diff_v_bit] != old_vk.dic[diff_v_bit]
        vk1 = vk.clone([diff_v_bit])    # vk1.kname: "M***"
        self.vk12dic[vk1.kname] = vk1   # register vk1
        vs = vk.cvs.intersection(old_vk.cvs)
        vs1 = vk.cvs - old_vk.cvs  # left-over in vk after removing old-vk.cvs
        for v in vk.cvs:
            if v in vs:
                if old_vk in self.chvkdic[v]:
                    self.chvkdic.remove(old_vk)
                self.chvkdic[v].append(vk1)
            elif v in vs1:
                if vk not in self.chvkdic[v]:
                    self.chvkdic[v].append(vk)

    def add_shadowed(self,
                     vk,             # shadowed vk, to be added
                     shadowing_vk,   # existing vklause(vk1) shadowing vk
                     vk1_bit):       # the shadowing-bit
        # vk is shadowed by existing vk1(E.G. {9:0, 11:1} by {9:0})
        # vs from vk1.cvs should be excluded from vk.cvs
        shadowed_cvs = shadowing_vk.cvs
        if vk.dic[vk1_bit] == shadowing_vk.dic[vk1_bit]:
            for v in vk.cvs:
                if v in self.chvkdic and (v not in shadowing_vk.cvs):
                    if vk not in self.chvkdic[v]:
                        self.chvkdic[v].append(vk)
        else:
            cut_vk = vk.clone([vk1_bit])
            self.vk12dic[cut_vk.kname] = cut_vk
            self.bdic[vk1_bit].append(cut_vk.kname)
            if vk.cvs == shadowed_cvs and vk.kname in self.bdic[vk1_bit]:
                self.bdic[vk1_bit].remove(vk.kname)

            for v in vk.cvs:
                if v in shadowed_cvs:
                    self.chvkdic[v].append(cut_vk)
                else:
                    self.chvkdic[v].append(vk)
            x = 1

    def add_shadowing(self,
                      vk,         # shadowing vk (to be added)
                      old_vk):    # shadowed old-vk
        for v in vk.cvs:
            if old_vk in self.chvdic[v]:
                self.chvkdic[v].remove(old_vk)
                self.chvkdic[v].append(vk)

    def add_cutting(self,
                    vk,         # vk1 to be added (on bit b)
                    old_vk):    # vk2[b] == !vk.dic[b]
        # vk2 get bit b dropped, becoming vk1 (on vk.cvs)
        # vk.cvs removed old-vk.cvs
        vk1 = old_vk.clone(vk.bits)    # vk1.kname: 'C<nnn>' -> 'M<nnn>'
        vk1.cvs.clear()
        self.bdic[vk1.bits[0]].append(vk1.kname)
        self.vk12dic[vk1.kname] = vk1  # vk1(named Mnnn) added
        for v in vk.cvs:
            self.chvkdic[v].append(vk)
            if old_vk in self.chvkdic[v]:
                self.chvkdic[v].remove(old_vk)
                vk1.cvs.append(v)
                self.chvkdic[v].append(vk1)

    def add_kicker_vk1(self,
                       vk,         # vk1 being added
                       hit_vk):    # old vk1 with conflict
        for v in vk.cvs:
            if v in hit_vk.cvs:
                self.chvkdic.pop(v)
            else:
                self.chvkdic[v].append(vk)

    def add_duplicated_vk1(self,
                           vk,
                           old_vk):
        for v in vk.cvs:
            if v not in old_vk.cvs:
                self.chvkdic[v].append(vk)
                if vk.kname not in self.bdic[vk.bits[0]]:
                    self.bdic[vk.bits[0]].insert(0, vk.kname)
