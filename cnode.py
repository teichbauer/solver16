from vklause import VKlause
from center import Center


class CNode:
    def __init__(self, nov, v, vkm, parent=None):
        self.parent = parent
        self.nov = nov  # example: 60
        self.v = v      # example: 1 - 60.1
        self.vkm = vkm

    def find_paths(self, blocks=None):
        if blocks == None:
            blocks = {}
        if self.nov == Center.last_nov:
            self.make_sat(blocks)
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
            dic = {ch: (self.vkm, blocks) for ch in nxt_chs}
        else:
            kns = self.vkm.bits_kns(bs)
            dic = self.handle_kns(nxsn, nxt_chs, kns, blocks)
        # TBD 2022-03-01
        for ch, tpl in dic.items():
            # for each 57.0(vkm), 57.2(vkm), ..., 57.6(vkm), 57.7(vkm)
            cn = CNode(self.nov - 3, ch, tpl[0], self)
            cn.find_paths(tpl[1])
            nxsn.chdic[ch] = cn
        x = 1

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
            vkmx = self.vkm.clone()     # self.vkm with all kns removed
            vkmx.add_vkdic(nxsn.vk12mdic[ch].vkdic)
            if not vkmx.valid:
                blocks[nxsn.nov].add(ch)
                break
            blcks = blocks.copy()
            for ck in chcks:            # for every kn removed, loop
                if ch in ck[0]:         # if the vk1 is relevant for ch
                    vkmx.add_vk(ck[1])  # add this vk1 to vkmx
                    if not vkmx.valid:
                        blcks.setdefault(nxsn.nov, set([])).add(ch)
                        break
                    if len(ck[2]) > 0:
                        # ck[2] has only 1 key/value pair
                        # tuple(ck[2].items())[0] is that pair
                        nv, vset = tuple(ck[2].items())[0]
                        blcks.setdefault(nv, set([])).update(vset)
            dic[ch] = (vkmx, blcks)
        return dic

    def name(self):
        return f"{self.nov}.{self.v}"

    def get_name_chain(self):
        name_chain = [(self.nov, self.v)]
        p = self.parent
        while p:
            name_chain.insert(0, (p.nov, p.v))
            p = p.parent
        return name_chain

    def make_sat(self, blocks):
        x = 1
