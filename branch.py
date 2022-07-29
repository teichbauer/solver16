from center import Center

class Branch:
    def __init__(self, parent, name='R', sat=None):  # R:Root
        self.parent = parent
        self.name = name
        self.sumbdic = {}
        self.novs = []  # list of descending novs
        self.chain = {}
        self.single_vk_bdic = {} # {nov: [bit, bit, ..], nov:[],...}  
        if sat == None:
            self.sat = {}
        else:
            self.sat = sat

    def add_tail(self, nov, tail):
        self.novs.append(nov)
        self.chain[nov] = tail
        # {bit: tail} - on the bit tail has only ONE kn
        sbits = []
        for b, kns in tail.bdic.items():
            cnt = len(kns)
            if cnt == 1:
                sbits.append(b)
            if b in self.sumbdic:
                self.sumbdic[b] += cnt
            else:
                self.sumbdic[b] = cnt
        if len(sbits) > 0:
            self.single_vk_bdic[tail.snode.nov] = sbits
        # self.show_sumbdic()

    # process bits where tails of any nov has 1 vk2 sitting on it
    def crunch_svks(self):
        for nov, bits in self.single_vk_bdic.items():
            self.chain[nov].proc_svks(bits)
        x = 1

    def get_bestbit(self):
        max_cnt = 0
        bit = -1
        for b, cnt in self.sumbdic.items():
            if cnt > max_cnt:
                bit = b
                max_cnt = cnt
        return bit

    def split(self):
        # self.get_svk_bit()
        self.get_splitbit()
        sbit = self.sbits.pop(0)
        ssat0 = {sbit: 0}
        ssat1 = {sbit: 1}

        b1 = Branch(self, f"{self.name}-{sbit}.1", self.sat)
        b1.sat.update(ssat1)
        chain1 = self.clone_chain(ssat1, sbit)
        for nv, tail in chain1.items():
            b1.add_tail(nv, tail)
        if not b1.done():
            b1.split()

        b0 = Branch(self, f"{self.name}-{sbit}.0", self.sat)
        b0.sat.update(ssat0)
        # chain0 = self.clone_chain(ssat0, sbit)
        # for nv, tail in chain0.items():
        #     b0.add_tail(nv, tail)

        return b0, b1
    
    def done(self):
        return False

    def clone_chain(self, ssat, sbit):
        nchain = {}
        for nov, tail in self.chain.items():
            if sbit in tail.bdic:
                nchain[nov] = tail.clone(ssat, sbit)
                inf = nchain[nov].metrics()
                print("{nov}:")
                print(inf)
            else:
                print(f"after: not cloned")
                nchain[nov] = tail
        return nchain

    def get_svk_bit(self):
        nv = self.novs[0]
        while nv not in self.single_vk_bdic:
            nv -= 3
            if nv == self.novs[-1]:
                raise Exception("no more single-vk bit.")
        self.sbits = sorted(self.single_vk_bdic.pop(nv))
        
    def show_chain(self):
        print(self.name)
        for nv in self.novs:
            msg = self.chain[nv].metrics()
            print(msg)

    def show_sumbdic(self):
        bits = sorted(self.sumbdic.keys())
        print(f'sumbdic({len(self.sumbdic)}):')
        for b in bits:
            print(f"{b}:{self.sumbdic[b]}", end=" ")
        print()

    def get_splitbit(self, choose_tail=False): # choose max tail or max vk2
        # max_dic = {}  # {bid:[max-tails, max-vk2s]}
            
            # for b, lst in dic.items():
            #     m = len(lst)
            #     pair = max_dic.setdefault(b, [0,0])
            #     pair[0] += 1
            #     pair[1] += m
            # x = 0
        # make choice based on max-tail, or max-vk2
        max_bit = -1
        val = 0
        for b, sz in self.sumbdic.items():
            if sz > val:
                max_bit = b
                val = sz
        self.sbits = [max_bit]
