# from center import Center
from snodevkm import SnodeVkm


class Sat2:
    def __init__(self, snode, parent, v, vk12dic):
        self.snode = snode
        self.parent = parent
        if parent:
            self.name = f"{parent.maxb}.{v}"
        else:
            self.name = 'root'
        self.alive = True
        self.vk12dic = vk12dic
        self.chvkdic = {v: set([]) for v in snode.bgrid.chvset}
        self.bdict = {}
        self.svkm = SnodeVkm(self, snode.nov)
        self.find_maxb()

    def find_maxb(self):
        self.maxb = -1
        maxcnt = 0
        for b in self.bdict:
            if len(self.bdict[b]) > maxcnt:
                maxcnt = len(self.bdict[b])
                self.maxb = b

    def verify(self, nov, stop_nov):
        while nov > stop_nov:
            self.svkm.sort_chvkdic()
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
            self.children[0] = Sat2(self.snode, self, 0, self.children[0])
        if self.children[1]:
            self.children[1] = Sat2(self.snode, self, 1, self.children[1])
        if self.children[0] == None and self.children[0] == None:
            self.alive = False
