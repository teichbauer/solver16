from center import Center

class Branch:
    def __init__(self, bdic, snode):
        self.bdic = bdic
        self.snode = snode


    def split(self, splitbit):
        tail = self.snode.tail
        bd = tail.bdic.copy()
        kn2s = bd.pop(splitbit)
        dic0 = { 'sats': [{splitbit: 0}], 'vk12dic': tail.vk12dic.copy()}
        dic1 = { 'sats': [{splitbit: 1}], 'vk12dic': tail.vk12dic.copy()}

        for kn2 in kn2s:
            pass


        x = 1


    def get_splitbit(self, choose_tail=False): # choose max tail or max vk2
        max_dic = {}  # {bid:[max-tails, max-vk2s]}
        for b, lst in self.bdic.items():
            m = 0
            for pair in lst:
                m +=  pair[1]
            max_dic[b] = (len(lst), m)
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
