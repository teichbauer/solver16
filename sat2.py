# from center import Center
from snodevkm import SnodeVkm


class Sat2:
    def __init__(self, parent, v, vk12dic):
        self.parent = parent
        if parent.__class__.__name__ == 'Sat2':
            self.name = f"{parent.maxb}.{v}"
        else:
            self.name = 'root'
        self.alive = True
        self.vk12dic = vk12dic
        self.bdict = {}
        for kn, vk in vk12dic.items():
            for b in vk.bits:
                self.bdict.setdefault(b, []).append(kn)
        maxcnt = 0
        self.maxb = -1
        for b in self.bdict:
            if len(self.bdict[b]) > maxcnt:
                maxcnt = len(self.bdict[b])
                self.maxb = b

    def verify(self, nov, stop_nov):
        while nov > stop_nov:
            sn = SnodeVkm(self.vk12dic, nov)
            sn.verify()
            # nov -= 3
            break
        x = 2

    def split2(self):
        self.children = {}
        self.children[0] = self.vk12dic.copy()  # vkdic0 for sat[maxb]:0
        self.children[1] = self.vk12dic.copy()  # vkdic1 for sat[maxb]:1
        kns = self.bdict[self.maxb]
        for kn in kns:
            vk = self.vk12dic[kn]
            if vk.nob == 2:
                if 0 in self.children:
                    self.children[0].pop(kn)
                if 1 in self.children:
                    self.children[1].pop(kn)
                # dropping maxb-bit, becomes a vk1 the same kname,
                vk1 = vk.clone([self.maxb])
                if vk.dic[self.maxb] == 0:  # for children[0], vk->vk1
                    if self.children[0]:
                        self.children[0][vk1.kname] = vk1
                    # for children[1]([maxb] == 1), vk: NOT-HIT, not-add-it
                else:  # vk.dic[maxb] == 1
                    # vk: No-HIT: not-add-it in children[0]
                    # for children[1] (bit-sat-value: 1) vk -> vk1
                    if self.children[1]:
                        self.children[1][vk1.kname] = vk1
            else:   # vk.nob == 1 : a vk1 already
                if self.vk12dic[kn].bits[0] == 0:
                    self.children[0] = None  # children[0] is impossible
                else:  # vk12dic[kn].bits[0] == 1
                    self.children[1] = None  # children[1] is impossible
        if self.children[0]:
            self.children[0] = Sat2(self, 0, self.children[0])
        if self.children[1]:
            self.children[1] = Sat2(self, 1, self.children[1])
        if self.children[0] == None and self.children[0] == None:
            self.alive = False
