# from typing_extensions import ParamSpecKwargs
from vklause import VKlause
from vk12mgr import VK12Manager
from bitgrid import BitGrid
from center import Center
from sat2 import Sat2
# from snodevkm import SnodeVkm
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
        self.bgrid = BitGrid(choice, self.nov)
        self.split_vkm()

    def chname(self, v):
        return f"{self.nov}.{v}"

    def split_vkm(self):
        for b in self.bgrid.bits:
            Center.satbitdic[b] = self
        self.chdic = {}
        # each vk12 in self.vk12dics[v] referred from Center.sumvk12m[nov]
        vk12kns = Center.vk12kndic.setdefault(self.nov, [])

        bdic = Center.sumbdic.setdefault(self.nov, {})
        vk12dic = {}

        for kn in self.touched:
            vk = self.vkm.pop_vk(kn)
            vk12 = self.bgrid.reduce_vk(vk)
            Center.sumvk12dic[kn] = vk12
            for b, v in vk12.dic.items():
                bdic.setdefault(b, [[], []])[v].append(kn)
            vk12kns.append(kn)
            vk12dic[kn] = vk12
        self.sat2 = Sat2(self, None, None, vk12dic)
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
            root_s2 = Center.snodes[Center.maxnov].sat2
            root_s2.split2()
            root_s2.children[1].verify(Center.maxnov, self.nov)
            x = 1
            # root_s2.children[0].verify

            # Center.bit_overlaps(60)

    def make_vk12mdic(self, sumvkdic):
        self.vk12mdic = {v: VK12Manager() for v in self.bgrid.chvset}
        vk12kns = Center.vk12kndic[self.nov]
        for kn in vk12kns:
            vk = sumvkdic[kn]
            for cv in vk.cvs:
                self.vk12mdic[cv].add_vk(vk)

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
