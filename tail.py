
class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        self.bdic = bitdic
        self.sdic = {}  # {cv:[], cv:[],...}
        self.sbmap = {} # {bit:[], bit:[]}
        self.sort_vks(snode.bgrid, knss)

    def test_conflict(self, sat):
        bit, val = tuple(sat.items())[0]  # {3:1} => (3,1) => 3,1
        blst = self.sbmap.setdefault(bit, [])
        for cv, ind in blst:
            esat = self.sdic[cv][ind]
            if esat[bit] == val:
                return 0
            elif esat[bit] != val:
                return -1




    def update_sdic(self, sdic, sbs):
        for cv, sats in sdic.items():
            lst = self.sdic.setdefault(cv, [])
            for sat in sats:
                tu = tuple(sat.items())[0]  # {3:1} => (3,1)
                blst = self.sbmap.setdefault(tu[0], [])
                lst.append(sat)
        

    def sort_vks(self, bgrid, knss):
        self.cvks_dic = {v: {} for v in bgrid.chvset }
        for kn in knss[2]:
            for kn, vk in self.vk12dic.items():
                for cv in vk.cvs:
                    self.cvks_dic[cv][kn] = vk

        # vk1a=s turned to sats, and the sat-bits will make other vk2s
        # become vk1s: this will loop on, until all vk1s are gone
        sdic = {}
        bs = []
        for kn in knss[1]:
            vk1 = self.vk12dic.pop(kn)
            bit, val = list(vk1.dic.items())[0]
            bs.append(bit)
            self.bdic[bit].remove(vk1.kname)
            sat = {bit: int(not val)}
            for cv in vk1.cvs:
                sdic.setdefault(cv,[]).append(sat)

        while len(bs) > 0:
            self.update_sdic(sdic, bs)
            sdic, bs = self._proc_sats(sdic, bs)


    def _proc_sats(self, sdic, sat_bits):
        new_sbits = []
        new_sdic = {}

        for sb in sat_bits:
            kns = self.bdic[sb]
            for kn in kns:
                vk2 = self.vk12dic[kn]
                comm_cvs = vk2.cvs.intersection(sdic)
                if len(comm_cvs):
                    vk2.pop_cvs(comm_cvs)
                    d = vk2.dic.copy()
                    d.pop(sb)
                    b, v = list(d.items())[0]
                    sat = {b: int(not v)}
                    new_sbits.append(b)
                    for cv in comm_cvs:
                        if kn in self.cvks_dic[cv]:
                            self.cvks_dic[cv].pop(kn)
                        new_sdic.setdefault(cv, []).append(sat)

        return new_sdic, new_sbits


