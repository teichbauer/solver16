from center import Center

class Branch:
    def __init__(self, sumbdic, snode):
        self.sumbdic = sumbdic
        self.snode = snode


    def split(self, splitbit):
        tail0 = self.snode.tail.clone({splitbit: 0})
        tail1 = self.snode.tail.clone({splitbit: 1})

        x = 1


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
