
def make_tree(self):
    self.tree = {}
    for nov, sn in self.snodes.items():
        # bits of vkm overlapping sn's 3 sat-bits
        bs = sn.bgrid.bitset.intersection(self.vkm.bdic)
        self.satbits -= bs
        sndic = self.tree.setdefault(nov, {})
        vks = []
        for b in bs:
            for kn in self.vkm.bdic[b]:
                vk = self.vkm.remove_vk(kn)
                cvs, out = sn.bgrid.cvs_and_outdic(vk)
                # for every vk1: save an entry in vks(list of tuples)
                vks.append((cvs, out, vk.kname))
        for ch in sn.bgrid.chheads:
            # for each child-head(ch) of sn57(1):
            # {0:{}, 2:{},3:{},4:{},5:{},6:{},7:{}}
            vkmx = self.vkm.clone()
            for thr in vks:
                if ch not in thr[0]:
                    vkmx.add_vk1(VKlause(thr[2], thr[1]))
            if not vkmx.valid:
                sndic.pop(ch)
            else:
                if sn.nov > sn.repo.last_nov:
                    sns = sn.repo.snodes.copy()
                    self.tree[ch] = CNode(
                        f"{nov}.{ch}",
                        vkmx,
                        sns,
                        self.satbits
                    )
                else:
                    x = 2
        x = 1
    x = 0


----------------------

    def proc_satbits(self, snode, vkm, bs, blocks):
        checks = []
        for b in bs:
            kns = vkm.bdic[b][:]
            for kn in kns:
                vk = vkm.remove_vk(kn)
                cvs, out = snode.bgrid.cvs_and_outdic(vk)
                if len(out) == 0:
                    for cv in cvs:
                        if cv in snode.bgrid.chheads:
                            blocks.add((snode.nov, cv))
                            return None
                else:  # out has 1 bit/value
                    vk.drop_bit(b)
                    vkm.add_vk1(vk)
                    if not vkm.valid:
                        return None  # this snode has no path: end-ppoint !
                    # check if any lower sns(nov < snode.nov) conflicts on vk?
                    sns = Center.satbits[vk.bits[0]]
                    for sn in sns:
                        cvx, outx = sn.bgrid.cvs_and_outdic(vk)
                        for cv in cvx:
                            blocks.add((sn.nov, cv))

                    checks.append((vk, cvs, out))
        for chck in checks:
            x = 0
        return vkm

    # def make_paths(self, snode, vkm, bs, blocks):
    #     if snode.nov == Center.last_nov:
    #         return True
    #     nxt_sn = Center.snodes[snode.nov - 3]
    #     if blocks == None:
    #         blocks = set([])

    #     all_bs = Center.satbitset.intersection(self.vkm.bdic)
    #     bs = nxt_sn.bgrid.bitset.intersection(all_bs)

    #     for ch in snode.bgrid.chheads:
    #         ch_vkm = snode.vk12mdic[ch]
    #         ch_vkm.add_vkdic(vkm.vkdic)
    #         if ch_vkm.valid:
    #             cn = CNode(nxt_sn.nov, ch, ch_vkm)
    #             all
    #             bits = nxt_sn
    #             if cn.make_paths(nxt_sn, ch_vkm, bits, blocks)
    #         pass


-----------------------
  def find_paths(self, blocks=None):
       if blocks == None:
            blocks = set([])
        all_bs = Center.satbitset.intersection(self.vkm.bdic)
        # what vkm(60.1) covering 57's 3 bits
        bs = self.nxt_sn.bgrid.bitset.intersection(all_bs)
        if len(bs) == 0:  # if not touching any of 57's 3 bits
            dic = {ch: (self.vkm, blocks) for ch in self.nxt_sn.bgrid.chheads}
        else:
            dic = self.handle_bs(self.nxr_sn, bs, blocks)
            # kns = []
            # for b in bs:
            #     kns += self.vkm.bdic[b]
            # dic = {}
            # chcks = []
            # for kn in kns:
            #     vk = vkm.remove_vk(kn)
            #     cvs, out = self.nxt_sn.bgrid.cvs_and_outdic(vk)
            #     if len(out) == 0:
            #         for ch in self.nxt_sn.bgrid.chheads:
            #             if ch in cvs:
            #                 blocks.add((self.nxt_sn.nov, ch))
            #     chcks.appen((cvs, out, VKlause(vk.kname, out)))
            # for ch in self.nxt_sn.bgrid.chheads:
            #     if (self.nxt_sn.nov, ch) in blocks:
            #         continue
            #     vkm = self.vkm.clone()
            #     blcks = blocks.copy()
            #     for ck in chcks:
            #         if ch in ck[0]:
            #             vkm.add_vk(ck[2])
            #             if not vkm.valid:
            #                 blcks.add((self.nxt_sn.nov, ch))
            #                 break
            #             if ck[2].bits[0] in Center.satbits:
            #                 for sn in Center.satbits[ck[2].bits[0]]:
            #                     cvx, outs = sn.bgrid.cvs_and_outdic(ck[2])
            #                     for c in sn.bgrid.chheads:
            #                         if c in cvx:
            #                             blcks.add((sn.nov, c))
            #     dic[ch] = (vkm, blcks)

        for ch, vk12m in self.nxt_sn.vk12mdic.items():
            # for each 57.0(vkm), 57.2(vkm), ..., 57.6(vkm), 57.7(vkm)
            vkm = vk12m.clone()  # clone of 60.1 vkm

            # bs has 1 or 2 bits in it
            vkmx = self.proc_satbits(self.nxt_sn, vkm, bs, blocks)
            if vkmx:
                cn = CNode(self.nov - 3, ch, vkmx)
                cn.find_paths(blocks)
                if cn.valid:
                    self.nxt_sn.chdic[ch] = cn
                x = 0
        x = 1


    @classmethod
    def sat_pathup(cls, snode):
        if snode.nov == cls.maxnov:
            return snode.solve()
        else:
            pnode = snode.parent
        for name, (vkm, ssat, blocks) in snode.chdic.items():
            if type(name[-1]) == int:
                chv = name[-1]
            else:
                chv = name[-1][-1]
            for pv, pvkm in pnode.vk12mdic.items():
                if (pnode.nov, pv) in blocks:
                    continue
                svkm = vkm.clone()
                svkm.add_vkdic(pvkm.vkdic)
                if svkm.valid:
                    if verify_sat(svkm.vkdic, ssat):
                        psat = pnode.bgrid.grid_sat(pv)
                        psat.update(ssat)
                        if len(svkm.kn1s) > 1:
                            sdic = {}
                            kn1s = svkm.kn1s[:]
                            for kn in kn1s:
                                vk1 = svkm.remove_vk1(kn)
                                b, v = vk1.hbit_value()
                                sdic[b] = int(not(v))
                            psat.update(sdic)
                        if snode.nov == cls.last_nov:
                            pname = (name, (pnode.nov, pv))
                        else:
                            name_lst = list(name)
                            name_lst.append((pnode.nov, pv))
                            pname = tuple(name_lst)
                        blcks = cls.find_blocks(pnode.nov, psat, pname)
                        pnode.chdic[pname] = (svkm, psat, blcks)
                    else:
                        pass
        cls.sat_pathup(pnode)

    @classmethod
    def find_blocks(cls, nov, sat, sat_name):
        print(f"checking on {sat_name}/{str(sat)} -------")
        nv = cls.maxnov
        blocks = set([])
        while nv > nov:
            sn = cls.snodes[nv]
            kns = verify_sat(sn.sumvk12dic, sat, True)
            if kns == False:
                m = f"{nv} passed {sat_name}"
                print(m)
            else:
                # m = f"{nv} failed on {sat_name}"
                for ch in sn.bgrid.chvset:
                    if kns != True:
                        if len(kns.intersection(sn.vk12mdic[ch].vkdic)):
                            blocks.add((sn.nov, ch))
            nv -= 3
        return blocks

#  snode
# ------------------
    def recognize_parents(self, ch):
        psnode = Center.snodes[self.nov + 3]
        mysat = self.bgrid.grid_sat(ch)
        for pv, pvkm in psnode.vk12mdic.items():
            vkm = pvkm.clone()
            # vkm = self.vk12mdic[ch].clone()
            vkm.add_vkdic(self.vk12mdic[ch].vkdic)
            if vkm.valid:
                mysat.update(psnode.bgrid.grid_sat(pv))
                kns = vkm.bits_kns(self.bgrid.bits)
                vks = {kn: vkm.vkdic[kn] for kn in kns}
                if verify_sat(vks, mysat):
                    psnode.chdic[f"{psnode.nov}.{pv}-{self.nov}.{ch}"] = vkm
