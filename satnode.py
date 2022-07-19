from vklause import VKlause
from vk12mgr import VK12Manager
from bitgrid import BitGrid
from center import Center
from tail import Tail
from basics import display_vkdic, ordered_dic_string, verify_sat, vk1_to_sat
from branch import Branch

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
        self.vkm = vkm  # all 3vks in here
        Center.snodes[self.nov] = self
        self.next = None
        self.touched = choice['touched']
        self.next_sh = self.sh.reduce(choice["bits"])
        self.bgrid = BitGrid(choice, self.nov)
        self.split_vkm()

    def split_vkm(self):
        for b in self.bgrid.bits:
            Center.satbitdic[b] = self
        self.chdic = {}
        # each vk12 in self.vk12dics[v] referred from Center.sumvk12m[nov]
        vk12kns = Center.vk12kndic.setdefault(self.nov, [])

        bdic = Center.sumbdic.setdefault(self.nov, {})
        vk2dic = {}

        bmap = {}  # {bid:[(cv1, sat),(cv2, sat)]}
        for kn in self.touched:
            vk = self.vkm.pop_vk(kn)        # pop out 3vk
            vk12 = self.bgrid.reduce_vk(vk) # make it vk12
            if vk12.nob == 1:
                sat = vk1_to_sat(vk12)
                print(f"{kn}-{tuple(vk12.cvs)}  becomes sat: {sat}")
                bmap.setdefault(vk12.bits[0],[]).append((tuple(vk12.cvs),sat))
            else:  # vk12.nob == 2
                for b, v in vk12.dic.items():
                    bdic.setdefault(b, set([])).add(kn)
                vk12kns.append(kn)
                vk2dic[kn] = vk12
        self.tail = Tail(self, vk2dic, bdic, bmap)
        x = 1
    # ---- def split_vkm(self) --------

    def spawn(self):
        if len(self.vkm.vkdic) > 0:
            # as long as there exist vk3 in self.vkm.vkdic: 
            # go next (nov -= 3)
            self.next = SatNode(self,  # parent
                                self.next_sh.clone(),
                                self.vkm)
            return self.next.spawn()
        else:
            branch0 = Branch(Center.vk2bdic, Center.snodes[Center.maxnov])
            split_bit = branch0.get_splitbit()
            brch10, brch11 = branch0.split(split_bit)
            x = 1

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
