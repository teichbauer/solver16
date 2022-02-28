from vklause import VKlause
from center import Center


class CNode:
    def __init__(self, nov, v, vkm):
        self.nov = nov  # example: 60
        self.v = v      # example: 1 - 60.1
        self.vkm = vkm
        if nov > Center.last_nov:
            self.nxt_sn = Center.snodes[nov - 3]  # nov = 57
        else:
            self.nxt_sn = None

    def cn_name(self):
        return f"{self.nov}.{self.v}"

    def find_paths(self, blocks=None):
        if blocks == None:
            blocks = set([])
        all_bs = Center.satbitset.intersection(self.vkm.bdic)
        # what vkm(60.1) covering 57's 3 bits
        bs = self.nxt_sn.bgrid.bitset.intersection(all_bs)
        if len(bs) == 0:  # if not touching any of 57's 3 bits
            dic = {ch: (self.vkm, blocks) for ch in self.nxt_sn.bgrid.chheads}
        else:
            dic = self.handle_bs(self.nxt_sn, bs, blocks)

        for ch, vk12m in self.nxt_sn.vk12mdic.items():
            # for each 57.0(vkm), 57.2(vkm), ..., 57.6(vkm), 57.7(vkm)
            vkm = vk12m.clone()  # clone of 60.1 vkm

            # bs has 1 or 2 bits in it
            vkmx = self.handle_bs(self.nxt_sn, bs, blocks)
            if vkmx:
                cn = CNode(self.nov - 3, ch, vkmx)
                cn.find_paths(blocks)
                if cn.valid:
                    self.nxt_sn.chdic[ch] = cn
                x = 0
        x = 1

    def handle_bs(self, sn, bs, blocks):
        kns = []
        for b in bs:
            kns += self.vkm.bdic[b]
        chcks = []
        for kn in kns:
            vk = self.vkm.remove_vk(kn)
            cvs, out = sn.bgrid.cvs_and_outdic(vk)
            if len(out) == 0:
                for ch in sn.bgrid.chheads:
                    if ch in cvs:
                        blocks.add((sn.nov, ch))
            chcks.append((cvs, out, VKlause(vk.kname, out)))

        dic = {}
        for ch in sn.bgrid.chheads:
            if (sn.nov, ch) in blocks:
                continue
            vkmx = self.vkm.clone()
            blcks = blocks.copy()
            for ck in chcks:
                if ch in ck[0]:
                    vkmx.add_vk(ck[2])
                    if not vkmx.valid:
                        blcks.add((sn.nov, ch))
                        break
                    if ck[2].bits[0] in Center.satbits:
                        for n in Center.satbits[ck[2].bits[0]]:
                            cvx, outs = n.bgrid.cvs_and_outdic(ck[2])
                            for c in n.bgrid.chheads:
                                if c in cvx:
                                    blcks.add((n.nov, c))
            dic[ch] = (vkmx, blcks)
        return dic
