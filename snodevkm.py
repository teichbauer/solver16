from vk12mgr import VK12Manager
from center import Center


class SnodeVkm:
    def __init__(self, vk12kdic, nov):
        self.nov = nov
        self.vk12dic = vk12kdic
        self.vk12kns = [[], []]  # [[original kns],[modified kns]]
        self.vk12m = VK12Manager(self)
        self.sn = Center.snodes[nov]

        self.chknsdic = {v: [] for v in self.sn.bgrid.chvset}

    def verify(self):
        for kn, vk in self.vk12dic.items():
            self.vk12m.add_vk(vk)
            if not self.vk12m.valid:
                return False
        return True

    def set_blinks(self):
        pass

    def get_vkdic(self, nov):
        bdic = self.center.sumbdic.setdefault(nov, {})
        for kn, (vk, cvs) in self.center.sumvk12m[nov].items():
            for b, v in vk.dic.items():
                lst = bdic.setdefault(b, [[], []])
                lst[v].append((kn, nov))
