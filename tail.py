from jinja2 import pass_environment

class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        self.bdic = bitdic
        sdic, bs = self.sort_vks(snode.bgrid, knss)
        while len(bs) > 0:
            sdic, bs = self.proc_sats(sdic, bs)

    def sort_vks(self, bgrid, knss):
        self.vkdic = {v: {} for v in bgrid.chvset }
        for kn in knss[2]:
            for kn, vk in self.vk12dic.items():
                for cv in vk.cvs:
                    self.vkdic[cv][kn] = vk
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
        return sdic, bs

    def proc_sats(self, sdic, sat_bits):
        new_sbits = []
        new_sdic = {}
        mvks = []       # list of modified vk2s

        for sb in sat_bits:
            kns = self.bdic[sb]
            for kn in kns:
                vk2 = self.vk12dic[kn]
                comm_cvs = vk2.cvs.intersection(sdic)
                if len(comm_cvs):
                    vk2.pop_cvs(comm_cvs)
                    mvks.append(vk2)
                    d = vk2.dic.copy()
                    d.pop(sb)
                    b, v = list(d.items())[0]
                    sat = {b: int(not v)}
                    new_sbits.append(b)
                    for v in comm_cvs:
                        new_sdic.setdefault(v, []).append(sat)
                else:
                    break
        for vk in mvks:
            if len(vk.cvs) == 0:
                x = 1
        return new_sdic, new_sbits

        # for cv, sats in sdic.items():
        #     vks = self.vkdic[cv]
        #     for sat in sats:
        #         b,v = list(sat.items())[0]
                
        #         kns = self.bdic[b]
        #         for kn in kns:
        #             vk2 = self.vk12dic[kn]
        #             if cv in vk2.cvs:
        #                 vk2.pop_cvs([cv])
        #                 d = vk2.dic.copy()
        #                 d.pop(b)
        #                 pair = list(d.items())[0]
        #                 new_sdic[cv] = {pair[0]: int(not pair[1])}
        #             else:
        #                 break                
        #             if vk2.dic[b] == v:
        #                 x = 9
        #             else:
        #                 x = 8
        #             x = 0
        #         x = 1


    def initial_satdic(self, bgrid, knss):
        # each child (keyed by cv)has a dic with content:
        # {'vks':[vk2-list], 'sats':[sat-list]}
        self.chdic = {v: {} for v in bgrid.chvset }
        
        for kn in knss[2]:
            for cvdic in self.chdic.values():
                cvdic['sats'] = []
                # each cvdic has a list of vk (ref) under the key 'vks'
                cvdic.setdefault('vks', []).append(self.vk12dic[kn])

        while len(knss[1]) > 0:
            knss[1] = self.process_vk1(knss[1])

    def process_vk1(self, kns):
        new_kns = []
        _kns = kns[:]
        while len(_kns) > 0:
            vk1 = self.vk12dic[_kns.pop()]
            vk1_bit = vk1.bits[0]
            vk1_value = vk1.dic[vk1_bit]
            sat_val = int(not vk1_value)

            for cv in vk1.cvs:
                self.chdic[cv]['sats'].append({vk1_bit: sat_val})

            # get a list of kns on vk1_bit, not including vk1.kname
            other_kns = self.bdic[vk1_bit] - {vk1.kname}
            for kname in other_kns:
                vk = self.vk12dic[kname]
                comm_cvs = vk1.cvs.intersection(vk.cvs)
                vk.pop_cvs(comm_cvs)
                for cv in comm_cvs:
                    vks = self.chdic[cv]['vks']
                    if vk.dic[vk1_bit] == vk1_value:
                        mvk1 = vk.clone([vk1_bit])


            for cv in vk1.cvs:
                self.chdic[cv]['sats'].append({vk1_bit: sat_val})
                vks = self.chdic[cv]['vks']

                while len(other_kns) > 0:
                    vk2 = self.vk12dic[other_kns.pop()]
                    if vk2.dic[vk1_bit] == vk1_value:
                        # if cv in 
                        mvk1 = vk2.clone([vk1_bit])
                        vks.remove(vk2)
                        vks.append(mvk1)
                        new_kns.append(mvk1.kname)
                        self.vk12dic[mvk1.kname] = mvk1
                    else:  # vk2.dic[vk1_bit] != vk1_value
                        self.chdic[cv]['vks'].pop(vk2.kname)
        return new_kns


