class Tail:
    def __init__(self, snode, vk12dic, bitdic, knss):
        self.snode = snode
        self.vk12dic = vk12dic
        self.bdic = bitdic
        self.initial_satdic(snode.bgrid, knss)

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
                vks = self.chdic[cv]['vks']

                for kn in self.bdic[vk1_bit]:
                    if kn == vk1.kname: 
                        continue
                    vk2 = self.vk12dic[kn]
                    if vk2.dic[vk1_bit] == vk1_value:
                        mvk1 = vk2.clone([vk1_bit])
                        vks.remove(vk2)
                        vks.append(mvk1)
                        new_kns.append(mvk1.kname)
                        self.vk12dic[mvk1.kname] = mvk1
                    else:  # vk2.dic[vk1_bit] != vk1_value
                        self.chdic[cv]['vks'].pop(vk2.kname)
        return new_kns



            


