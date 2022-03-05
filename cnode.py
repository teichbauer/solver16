from vklause import VKlause
from center import Center
from pdb import set_trace


class CNode:
    def __init__(self, nov, v, vkm, parent=None):
        self.parent = parent
        self.nov = nov  # example: 60
        self.v = v      # example: 1 - 60.1
        self.vkm = vkm
        self.alive = True

    def find_paths(self, blocks=None):
        if blocks == None:
            blocks = {}
        if self.nov == Center.last_nov:
            set_trace()
            self.make_sat()
            return
        nxsn = Center.snodes[self.nov - 3]
        all_bs = Center.satbits.intersection(self.vkm.bdic)
        nxsn_chblocks = blocks.setdefault(nxsn.nov, set([]))
        if len(nxsn_chblocks) > 0:
            nxt_chs = nxsn.bgrid.chvset - nxsn_chblocks
        else:
            nxt_chs = nxsn.bgrid.chvset
        # what vkm(60.1) covering 57's 3 bits
        bs = nxsn.bgrid.bitset.intersection(all_bs)
        if len(bs) == 0:  # if not touching any of 57's 3 bits
            self.brchdic = {ch: (self.vkm, blocks) for ch in nxt_chs}
        else:
            kns = self.vkm.bits_kns(bs)
            self.brchdic = self.handle_kns(nxsn, nxt_chs, kns, blocks)
        if len(self.brchdic) > 0:
            # can not loop with brchdic.items(), for brchdic may be reduced
            bks = list(self.brchdic.keys())
            for bk in bks:
                tpl = self.brchdic[bk]
                cn = CNode(self.nov - 3, bk, tpl[0], self)  # tpl[0]: vkm[bk]
                cn.find_paths(tpl[1])   # tpl[1]: block-dic for ch
            # for ch, tpl in self.brchdic.items():
            #     cn = CNode(self.nov - 3, ch, tpl[0], self)  # tpl[0]: vkm[ch]
            #     cn.find_paths(tpl[1])   # tpl[1]: block-dic for ch
        else:
            self.die()
        x = 1

    def die(self):
        msg = f"{self.get_name_chain()}"
        # print(f"{msg} dying.")
        self.alive = False
        if self.parent:
            del self.parent.brchdic[self.v]
            if len(self.parent.brchdic) == 0:
                self.parent.die()
        else:
            msg = f"{self.name()} is dead"
            print(msg)

    def handle_kns(self, nxsn, chs, kns, blocks):
        chcks = []
        for kn in kns:
            # the kns touching nxsn's bits are removed from self.vkm
            # they, after dropping a bit, will be casewise added back
            # to the casewise nxsn-child
            vk = self.vkm.remove_vk(kn)
            cvs, out = nxsn.bgrid.cvs_and_outdic(vk)
            if len(out) == 0:
                for ch in nxsn.bgrid.chvset:
                    if ch in cvs:
                        blocks.setdefault(nxsn.nov, set([])).add(ch)
            else:
                vkx = VKlause(vk.kname, out)
                blckx = {}
                if vkx.bits[0] in Center.satbits:
                    lower_sn = Center.satbitdic[vkx.bits[0]]
                    cvx, outx = lower_sn.bgrid.cvs_and_outdic(vkx)
                    for c in lower_sn.bgrid.chvset:
                        if c in cvx:
                            blckx.setdefault(lower_sn.nov, set([])).add(c)
                chcks.append((cvs, vkx, blckx))
        dic = {}
        for ch in chs:
            if ch in blocks[nxsn.nov]:
                continue
            vkmx = self.vkm.clone()     # self.vkm with all kns removed
            vkmx.add_vkdic(nxsn.vk12mdic[ch].vkdic)
            if not vkmx.valid:
                blocks[nxsn.nov].add(ch)
                continue
            nx_blocks = blocks.copy()
            for ck in chcks:            # for every kn removed, loop
                if ch in ck[0]:         # if the vk1 is relevant for ch
                    vkmx.add_vk(ck[1])  # add this vk1 to vkmx
                    if not vkmx.valid:
                        blocks.setdefault(nxsn.nov, set([])).add(ch)
                        break
                    if len(ck[2]) > 0:
                        # ck[2] has only 1 key/value pair
                        # tuple(ck[2].items())[0] is that pair
                        nv, vset = tuple(ck[2].items())[0]
                        nx_blocks.setdefault(nv, set([])).update(vset)
            if ch not in blocks[nxsn.nov]:
                dic[ch] = (vkmx, nx_blocks)
        return dic

    def name(self):
        return (self.nov, self.v)

    def get_satpath(self):
        lst = [self.name()]
        p = self.parent
        while p:
            lst.insert(0, p.name())
            p = p.parent
        return lst

    def get_name_chain(self):
        path = self.get_satpath()
        return path

    def make_sat(self):
        path = self.get_satpath()
        sats = []
        rsat = {}
        sbits = list(Center.satbits)
        for pair in path:
            rsat.update(Center.snodes[pair[0]].bgrid.grid_sat(pair[1]))
        for kn in self.vkm.kn1s:
            vk1 = self.vkm.remove_vk1(kn)
            bit, v = vk1.hbit_value()
            sbits.remove(bit)
            rsat[bit] = int(not(v))
        if len(sbits) > 0:
            xsat = rsat.copy()
            for b in sbits:
                for v in (0, 1):
                    xsat[b] = v
            sats.append(xsat)
        else:
            x = 0
