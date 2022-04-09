from vklause import VKlause
from basics import get_bit, oppo_binary, display_vkdic


class VK12Manager:
    # debug = True
    debug = False

    def __init__(self, svkm, vkdic=None, raw=False):
        self.svkm = svkm
        self.valid = True
        if not raw:
            self.reset()  # set vkdic, bdic, kn1s, kn2s
        if vkdic and len(vkdic) > 0:
            self.add_vkdic(vkdic)

    def add_vk1(self, vk):
        if self.debug:
            print(f"adding vk1: {vk.kname}")
        bit = vk.bits[0]
        knames = self.bdic.setdefault(bit, [])
        # kns for loop usage. can't use knames directly, for knames may change
        kns = knames[:]  # kns for loop:can't use knames, for it may change.
        for kn in kns:
            if kn in self.kn1s:
                # bdic may have been updated, so kn may no more be
                # in there on this bit any more
                if kn not in self.bdic[bit]:
                    continue
                vk1 = self.svkm.vk12dic[kn]
                if vk1.dic[bit] != vk.dic[bit]:
                    self.svkm.add_licker_vk1(vk, vk1)
                    self.valid = False
                    return False
                else:  # self.svkm.vk12dic[kn].dic[bit] == vk.dic[bit]
                    # if self.debug:
                    #     self.info.append(f"{vk.kname} duplicats {kn}")
                    #     print(self.info[-1])
                    self.svkm.add_duplicated_vk1(vk, vk1)
                    return False
            elif kn in self.kn2s:
                vk2 = self.svkm.vk12dic[kn]
                if bit in vk2.bits:
                    if vk2.dic[bit] == vk.dic[bit]:
                        # a vk2 has the same v on this bit:
                        # remove vk2 from vs vk is on
                        self.svkm.add_shadowing(vk, self.svkm.vk12dic[kn])
                    else:  # vk2 has diff val on this bit
                        # drop a bit:it becomes vk1, add it back as vk1
                        self.svkm.add_cutting(vk, self.svkm.vk12dic[kn])
                    return
        self.svkm.add_vk(vk)
        self.kn1s.append(vk.kname)
        self.bdic.setdefault(bit, []).insert(0, vk.kname)
        return True
    # end of def add_vk1(self, vk) ----------------------------------

    def add_vk2(self, vk):
        if self.debug:
            print(f"adding vk2: {vk.kname}")
        # if an existing vk1 covers vk?
        for kn in self.kn1s:
            b = self.svkm.vk12dic[kn].bits[0]
            if b in vk.bits:
                if self.svkm.vk12dic[kn].dic[b] == vk.dic[b]:
                    # vk not added. but valid is this still
                    if self.debug:
                        self.info.append(f"{vk.kname} blocked by {kn}")
                        print(self.info[-1])
                    self.svkm.add_shadowed(vk, self.svkm.vk12dic[kn])
                    # return (self.valid, False, ("shadowed-by", kn))
                else:  # vk1 has diff value on this bit
                    # drop this bit, this vk2 becomes a vk1. Add this vk1
                    if self.debug:
                        self.info.append(f"{kn} makes {vk.kname} vk1")
                        print(self.info[-1])
                    self.svkm.add_shadowed(vk, self.svkm.vk12dic[kn])
                    return True
            else:
                pass
        # find vk2s withsame bits
        pair_kns = []
        for kn in self.kn2s:
            if self.svkm.vk12dic[kn].bits == vk.bits:
                pair_kns.append(kn)
        bs = vk.bits
        for pk in pair_kns:
            pvk = self.svkm.vk12dic[pk]
            if pvk.bits != vk.bits:  # pvk may have been modified, and
                continue  # is no more a pair with vk. In that case, jump over
            if vk.dic[bs[0]] == pvk.dic[bs[0]]:
                if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    if self.debug:
                        self.info.append(
                            f"{vk.kname} douplicates {kn}. not added")
                        print(self.info[-1])
                    return False  # vk not added
                else:  # b0: same value, b1 diff value
                    msg = f"{vk.kname} + {pvk.kname}: {pvk.kname}->vk1"
                    if self.debug:
                        self.info.append(msg)
                        self.info.append(f"{vk.kname} not added")
                        print(self.info[-1])
                        print(self.info[-2])
                    # remove pvk, it becomes a vk1
                    vk2 = self.remove_vk2(pvk.kname)
                    vk1 = vk2.clone([bs[1]])
                    self.add_vk1(vk1)  # validity updated when add vk1
                    return False  # vk not added.
            else:  # b0 has diff value
                if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    # b1 has the same value
                    msg = f"{vk.kname} + {pvk.kname}: {pvk.kname}->vk1"
                    if self.debug:
                        self.info.append(msg)
                        self.info.append(f"{vk.kname} not added")
                        print(self.info[-1])
                        print(self.info[-2])
                    # remove pvk
                    vk2 = self.remove_vk2(pvk.kname)
                    # drop a bit(bs[1]), add the resulting vk1
                    vk1 = vk2.clone([bs[0]])
                    return self.add_vk(vk1)
                else:  # non bit from vk has the same value as pvk's
                    pass
        for b in bs:
            self.bdic.setdefault(b, []).append(vk.kname)
        self.kn2s.append(vk.kname)
        self.svkm.add_vk(vk)
        return True
    # end of def add_vk2(self, vk): --------------------------

    def bits_kns(self, bits):
        kns = set([])
        for b in bits:
            if b in self.bdic:
                for k in self.bdic[b]:
                    kns.add(k)
        return kns

    def clone(self, deep=True):
        vk12m = VK12Manager(self.svkm, None, True)
        vk12m.bdic = {k: lst[:] for k, lst in self.bdic.items()}
        vk12m.kn1s = self.kn1s[:]
        vk12m.kn2s = self.kn2s[:]
        return vk12m

    def vk1s(self):
        return [self.svkm.vk12dic[kn] for kn in self.kn1s]

    def add_vkdic(self, vkdic):
        for vk in vkdic.values():
            self.add_vk(vk)
            if not self.valid:
                return False
        return self.valid

    def add_vk(self, vk):
        if vk.nob == 1:
            return self.add_vk1(vk)  # self.add_vk1(vk.clone())
        elif vk.nob == 2:
            return self.add_vk2(vk)  # self.add_vk2(vk.clone())
    # end of def add_vk(self, vk):

    def reset(self):
        self.bdic = {}  # dict keyed by bit, value: list of knames
        # self.vkdic = {}
        self.kn1s = []
        self.kn2s = []
