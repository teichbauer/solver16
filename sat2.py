class Sat2:
    def __init__(self, vk12m):
        self.vk12m = vk12m

    def get_sats(self):
        sats = []
        sat = {}
        for kn in self.vk12m.kn1s:
            vk = self.vk12m.remove_vk1(kn)
            b, v = vk.hbit_value()
            sat[vk.bits[0]] = int(not v)
        if len(self.vk12m.kn2s) == 0:
            return [sat]
        ss = self.getsats()
        for s in ss:
            s.update(sat)
            sats.append(s)
        return sats

    def getsats(self):
        ' make list of sats out of vk2s from self.vk12m '
        for kn in self.vk12m.kn2s:
            pass
