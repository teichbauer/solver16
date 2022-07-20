from center import Center

class Branch:
    def __init__(self, sumbdic, tail_chain, sat = None):
        self.sumbdic = sumbdic
        self.chain = tail_chain
        if sat == None:
            self.sat = {}
        else:
            self.sat = sat


    def split(self, bit):
        self.bit = bit
        ssat0 = {bit: 0}
        ssat1 = {bit: 1}
        b0 = Branch(None, self.clone_chain(ssat0), ssat0)
        b1 = Branch(None, self.clone_chain(ssat1), ssat1)
        return b0, b1

    def clone_chain(self, ssat):
        nchain = {}
        for nov, tail in self.chain.items():
            nchain[nov] = tail.clone(ssat, self.bit)
        return nchain

    def clone_sumbdic(self, ssat):
        sumbdic = {}
        for nv, dic in self.sumbdic.items():
            pass

    def get_splitbit(self, choose_tail=False): # choose max tail or max vk2
        max_dic = {}  # {bid:[max-tails, max-vk2s]}
        for nov, dic in self.sumbdic.items():
            for b, lst in dic.items():
                m = len(lst)
                pair = max_dic.setdefault(b, [0,0])
                pair[0] += 1
                pair[1] += m
            x = 0
        # make choice based on max-tail, or max-vk2
        max_bit = -1
        val = 0
        for b in max_dic:
            if choose_tail:
                xval = max_dic[b][0]
            else:
                xval = max_dic[b][1]
            if xval > val:
                max_bit = b
                val = xval
        return max_bit
