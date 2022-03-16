# from typing_extensions import ParamSpecKwargs
from vklause import VKlause
from vk12mgr import VK12Manager
from bitgrid import BitGrid
from center import Center
from cnode import CNode
from basics import display_vkdic, ordered_dic_string, verify_sat


class SatNode:

    def __init__(self, parent, sh, vkm):
        choice = vkm.make_choice()  # avks be pooped out from vkm.vkdic
        self.parent = parent
        self.repo = Center
        if parent == None:
            self.nov = Center.maxnov
            Center.root_snode = self
        else:
            self.nov = parent.nov - 3
        self.sh = sh
        self.vkm = vkm
        Center.snodes[self.nov] = self
        self.next = None
        self.touched = choice['touched']
        self.next_sh = self.sh.reduce(choice["bits"])
        self.bgrid = BitGrid(choice)
        self.split_vkm()

    def chname(self, v):
        return f"{self.nov}.{v}"

    def split_vkm(self):
        """ 1. pop-out touched-vk3s forming sumvk2dic with them
            2. tdic: keyed by cvs of vks and values are lists of vks
               this results in self.vk12dics dict, keyed by the possible
               grid-values(bgrid/chvset), vkdics restricting the value
               if vk2dics misses a chhead-value, that doesn't mean, this value
               if not allowed - quite the opposite: This means that there is no
               restriction(restrictive vk2) on this ch-head/value.
            3. make next-choice from vkm - if not empty, if it is empty,no .next
            """
        for b in self.bgrid.bits:
            Center.satbitdic[b] = self
        # Center.orig_vkm.drop_bits(
        #     self.bgrid.bits, self.touched, self.bgrid.avks)
        self.chdic = {}
        # each vk12 in self.vk12dics[v] referred from Center.sumvk12m[nov]
        sumvk12dic = Center.sumvk12m.setdefault(self.nov, {})
        bdic = Center.sumbdic.setdefault(self.nov, {})
        self.vk12mdic = {v: VK12Manager() for v in self.bgrid.chvset}
        for kn in self.touched:
            vk = self.vkm.pop_vk(kn)
            vk12, cvs = self.bgrid.reduce_vk(vk)
            for b, v in vk12.dic.items():
                bdic.setdefault(b, [[], []])[v].append(kn)
            sumvk12dic[kn] = (vk12, cvs)
            for cv in cvs:
                self.vk12mdic[cv].add_vk(vk12)
        x = 1
    # ---- def split_vkm(self) --------

    def spawn(self):
        if len(self.vkm.vkdic) > 0:
            self.next = SatNode(self,  # parent
                                self.next_sh.clone(),
                                self.vkm)
            return self.next.spawn()
        else:
            Center.last_nov = self.nov
            Center.novs = sorted([n for n in Center.snodes], reverse=True)
            Center.set_satbits()
            for ch in self.bgrid.chvset:
                ch_sat = self.bgrid.grid_sat(ch)
                self.chdic[(self.nov, ch)] = (
                    self.vk12mdic[ch], ch_sat, set([]))

            Center.snodes[60].path_down()
            # Center.snodes[60].bit_choice()
            # Center.snodes[57].bit_choice()
            # Center.snodes[54].bit_choice()
            # Center.snodes[51].bit_choice()
            # Center.snodes[48].bit_choice()
            # Center.snodes[45].bit_choice()
            # Center.snodes[42].bit_choice()
            # Center.snodes[39].bit_choice()
            # Center.snodes[36].bit_choice()
            # Center.snodes[33].bit_choice()
            # Center.snodes[30].bit_choice()
            # Center.snodes[27].bit_choice()
            # Center.snodes[24].bit_choice()
            # Center.set_blinks()
            # Center.bit_overlaps(60)

    def path_down(self):
        altered_vkdic = {}
        vkdic = {kn: p[0] for kn, p in Center.sumvk12m[self.nov].items()}
        vk12m = VK12Manager(vkdic)
        nv = self.nov - 3
        xvkdic = {kn: p[0] for kn, p in Center.sumvk12m[nv].items()}
        vk12m.add_vkdic(xvkdic)
        x = 1

    def bit_choice(self):
        # bdic = Center.sumbdic[self.nov]
        # dic = {b: {} for b in bdic }
        dic = {}
        for bit in Center.sumbdic[self.nov]:
            nv = self.nov
            while nv > Center.last_nov:
                d = dic.setdefault(bit, {})
                bdic = Center.sumbdic[nv]
                if bit in bdic:
                    d[nv] = len(bdic[bit][0] + bdic[bit][1])
                else:
                    d[nv] = 0
                nv -= 3
        ar = [(sum(dic[bit].values()), bit) for bit in dic]
        ar = sorted(ar, reverse=True)
        return ar[0]

    def solve(self):
        for pname, vkm in self.chdic.items():
            sat = self.path_sat(pname)
            sats, vk2m = self.vk1_sat(vkm, sat)
            Center.sats += sats
            if len(vk2m.kn2s) > 0:  # TBD: still vk2s left: solve that
                x = 1
        return Center.sats

    def path_sat(self, pname):
        sat = {}
        secs = pname.split('-')
        for sec in secs:
            pair = sec.split('.')
            snode = Center.snodes[int(pair[0])]
            snv_sat = snode.bgrid.grid_sat(int(pair[1]))
            sat.update(snv_sat)
        return sat

    def vk1_sat(self, vk12m, sat):
        bits = Center.bits.copy()
        kn1s = vk12m.kn1s[:]
        for kn in kn1s:
            vk = vk12m.remove_vk1(kn)
            b = vk.bits[0]
            if b in bits:
                bits.remove(b)
                sat[b] = int(not(vk.dic[b]))
        tmps = [sat]
        sats = []
        while len(tmps) > 0:
            sx = tmps.pop()
            for b in bits:
                for v in (0, 1):
                    st = sx.copy()
                    st[b] = v
                    sats.append(st)
        return sats, vk12m
