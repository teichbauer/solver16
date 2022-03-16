from center import Center
from vkmgr import VKManager


class UberVk12m:
    def __init__(self, snode):
        self.snode = snode
        self.get_vkdic(snode.nov)
        self.blinks = {}
        sn = snode.next
        while sn:
            self.get_vkdic(sn.nov)
            sn = sn.next
        self.set_blinks()

    def set_blinks(self):
        pass

    def get_vkdic(self, nov):
        bdic = Center.sumbdic.setdefault(nov, {})
        for kn, (vk, cvs) in Center.sumvk12m[nov].items():
            for b, v in vk.dic.items():
                lst = bdic.setdefault(b, [[], []])
                lst[v].append((kn, nov))
