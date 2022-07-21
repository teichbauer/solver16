from center import Center

class SatManager:
    def __init__(self, owner, sat_cvs_dic=None):
        self.owner = owner
        self.sat_cvs_dic = {}
        if sat_cvs_dic:
            self.add(sat_cvs_dic)

    def add(self, sat_cvs_dic):
        for bit in sat_cvs_dic:
            for bv, xcvs in sat_cvs_dic[bit].items():
                bd = self.sat_cvs_dic.setdefault(bit, {})
                cvs = bd.setdefault(bv, set([]))
                for cv in xcvs:
                    if cv not in cvs:
                        cvs.add(cv)
        sat_cvs_dic = self.expand_bmap(sat_cvs_dic)
        if len(sat_cvs_dic) > 0:
            self.add(sat_cvs_dic)


    def expand_bmap(self, sat_cvs_dic):
        new_sat_cvs_dic = {}
        while len(sat_cvs_dic) > 0:  # bits is a set
            bit, bv_cvs_dic = sat_cvs_dic.popitem()
            # kn2s = bdic.get(bit, []) may ge modified, so use a copy
            kn2s = self.owner.bdic.get(bit, []).copy()
            if len(kn2s) == 0:
                continue
            for kn2 in kn2s:
                vk2 = self.owner.vk2dic[kn2]
                for bv,  xcvs in bv_cvs_dic.items():
                # for xcvs, xsat in cvs_sat_lst:
                    comm_cvs = vk2.cvs.intersection(xcvs)
                    if len(comm_cvs) > 0:
                        # since vk2 in vk2dic is a ref, and here the vk2
                        # is modified, replace this vk2 with a clone, so tha
                        # the modification will not harm the original vk2
                        vk2_clone = vk2.clone()
                        self.owner.vk2dic[kn2] = vk2_clone

                        vk2_clone.pop_cvs(comm_cvs)
                        if len(vk2_clone.cvs) == 0:
                            self.owner.remove_vk2(vk2_clone)

                        self.owner.remove_kn2_from_cvk_dic(comm_cvs, kn2)

                        # if vk2_clone.dic[bit] != xsat[bit]:
                        if vk2_clone.dic[bit] != bv:
                            continue
                        vk1 = vk2_clone.clone([bit])
                        b, v = vk1.sat1()
                        lst = new_sat_cvs_dic.setdefault(b,{})[v] = comm_cvs
        return new_sat_cvs_dic

