
class Branch:
    def __init__(self):
        self.sumbdic = {}
        self.chain = {}
        self.sat = {}

    def add_tail(self, nov, tail):
        self.chain[nov] = tail
        for b, kns in tail.bdic.items():
            cnt = len(kns)
            if b in self.sumbdic:
                self.sumbdic[b] += cnt
            else:
                self.sumbdic[b] = cnt
        self.show_bdic()

    def get_bestbit(self):
        max_cnt = 0
        bit = -1
        for b, cnt in self.sumbdic.items():
            if cnt > max_cnt:
                bit = b
                max_cnt = cnt
        return bit

    def split(self, bit):
        self.bit = bit
        ssat0 = {bit: 0}
        ssat1 = {bit: 1}
        b0 = Branch()
        chain0 = self.clone_chain(ssat0)
        for nv, tail in chain0.items():
            b0.add_tail(nv, tail)

        b1 = Branch()
        chain1 = self.clone_chain(ssat1)
        for nv, tail in chain1.items():
            b1.add_tail(nv, tail)
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

    def show_bdic(self):
        bits = sorted(self.sumbdic.keys())
        print(f'sumbdic({len(self.sumbdic)}):')
        for b in bits:
            print(f"{b}:{self.sumbdic[b]}", end=" ")
        print()

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
