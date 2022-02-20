# from typing_extensions import ParamSpecKwargs
from vklause import VKlause
from vk12mgr import VK12Manager
from bitgrid import BitGrid
from center import Center
from basics import display_vkdic, ordered_dic_string, testing


class SatNode:

    def __init__(self, parent, sh, vkm):
        choice = vkm.make_choice()  # avks be pooped out from vkm.vkdic
        self.parent = parent
        if parent == None:
            self.nov = Center.maxnov
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
               grid-values(bgrid/chheads), vkdics restricting the value
               if vk2dics misses a chhead-value, that doesn't mean, this value
               if not allowed - quite the opposite: This means that there is no
               restriction(restrictive vk2) on this ch-head/value.
            3. make next-choice from vkm - if not empty, if it is empty,no .next
            """
        Center.add_satbits(self.bgrid.bitset)
        self.chdic = {}
        # each vk12 in here is referred by from vk12 in each self.vk12dics[v]
        self.sumvk12dic = {}  # all vk12s from touched.
        self.vk12dics = {v: {} for v in self.bgrid.chheads}
        for kn in self.touched:
            vk = self.vkm.pop_vk(kn)
            cvs, outdic = self.bgrid.cvs_and_outdic(vk)
            rvk = VKlause(vk.kname, outdic)
            for v in cvs:
                if v not in self.bgrid.covers:
                    self.vk12dics[v][kn] = rvk
                if kn not in self.sumvk12dic:
                    self.sumvk12dic[kn] = rvk
        if len(self.sumvk12dic) > 0:
            self.bgrid.get_vk12bits(self)

        if self.parent == None:
            for v in self.vk12dics:
                self.chdic[self.chname(v)] = VK12Manager(self.vk12dics[v])
        else:
            for pvname in self.parent.chdic:
                lvdic = self.bgrid.filter_pvs(self.parent.chdic[pvname])
                for lv in lvdic:
                    vkm = lvdic[lv]
                    valid = vkm.add_vkdic(self.vk12dics[lv])
                    if valid:
                        lvname = self.chname(lv)
                        name = f"{pvname}-{lvname}"
                        self.chdic[name] = vkm
            x = 0
        x = 1
    # ---- def split_vkm(self) --------

    def spawn(self):
        if len(self.vkm.vkdic) > 0:
            self.next = SatNode(self,  # parent
                                self.next_sh.clone(),
                                self.vkm)
            return self.next.spawn()
        else:
            return self.solve()

    def solve(self):
        for pname, vkm in self.chdic.items():
            sat = self.path_sat(pname)
            sats, vk2m = self.vk1_sat(vkm, sat)
            Center.sats += sats
            if len(vk2m.kn2s) > 0:
                # TBD: still vk2s left: solve that
                # and update sats
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
