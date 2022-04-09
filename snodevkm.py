from vk12mgr import VK12Manager
from center import Center


class SnodeVkm:
    def __init__(self, vk12kdic, nov):
        self.nov = nov
        self.vk12dic = vk12kdic
        self.vk12kns = [[], []]  # [[original kns],[modified kns]]
        self.vk12m = VK12Manager(self)
        self.sn = Center.snodes[nov]

        self.chvkdic = {v: [] for v in self.sn.bgrid.chvset}

    def verify(self):
        for kn, vk in self.vk12dic.items():
            self.vk12m.add_vk(vk)
        return True

    def add_vk(self, vk):
        for v in vk.cvs:
            if v in self.chvkdic and vk not in self.chvkdic[v]:
                self.chvkdic[v].append(vk)

    def add_shadowed(self,
                     vk,             # shadowed vk, to be added
                     shadowing_vk):  # existing vklause(vk1) shadowing vk
        # vk is shadowed by existing vk1(E.G. {9:0, 11:1} by {9:0})
        # vs from vk1.cvs should be excluded from vk.cvs
        b = shadowing_vk.bits[0]
        shadowed_cvs = shadowing_vk.cvs
        if vk.dic[b] == shadowing_vk.dic[b]:
            for v in vk.cvs:
                if v in self.chvkdic and (v not in shadowing_vk.cvs):
                    if vk not in self.chvkdic[v]:
                        self.chvkdic[v].append(vk)
        else:
            cut_vk = vk.clone([b])
            self.vk12dic[cut_vk.kname] = cut_vk
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
        self.vk12m.bdic[vk1.bits[0]].append(vk1.kname)
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
                if vk.kname not in self.vk12m.bdic[vk.bits[0]]:
                    self.vk12m.bdic[vk.bits[0]].insert(0, vk.kname)

    def set_blinks(self):
        pass

    def get_vkdic(self, nov):
        bdic = self.center.sumbdic.setdefault(nov, {})
        for kn, (vk, cvs) in self.center.sumvk12m[nov].items():
            for b, v in vk.dic.items():
                lst = bdic.setdefault(b, [[], []])
                lst[v].append((kn, nov))
