from amaranth import *
from amaranth.sim import*
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner
from data_cache import *
from data_memory import *
#r_or_w = 0 = read
class link(Elaboratable):
    def __init__(self):
        self.DM = data_mem()
        self.DC = data_cache()
        self.r_or_w = Signal(1)
        self.addre = Signal(9)
        self.data = Signal(9)
        self.num_in_bits = 4
        self.num_tag = 5
        self.in_bits = self.addre[:self.num_in_bits]
        self.tag = self.addre[self.num_in_bits:]
        self.val = Signal(1,reset = 0)
        self.out = Signal(9)

    def elaborate(self,platform):
        m = Module()
        m.submodules.DM = self.DM
        m.submodules.DC = self.DC
        with m.If(self.r_or_w.matches(0b0)):
            m.d.sync += [self.DC.read_or_write.eq(self.r_or_w),self.DC.read_port.eq(self.addre)]
            with m.If(self.val == 0b0):
                m.d.sync += [self.val.eq(0b1)]
            with m.If(self.val == 0b1):
                m.d.sync += [self.val.eq(0b0)]
            with m.If(self.DC.hit.matches(0b1)):        
                m.d.sync += [self.out.eq(self.DC.read_port)]

            with m.If(self.DC.hit.matches(0b0)):
                m.d.sync += [self.DM.read_or_write.eq(0b0), self.DM.address.eq(self.addre)]
                m.d.sync += [self.data.eq(self.DM.data)]
                m.d.sync += [self.DC.load_data.eq(0b1)]
                m.d.sync += [self.DC.read_or_write.eq(0b1), self.DC.read_port.eq(self.addre),self.DC.write_data.eq(self.data)]
                m.d.sync += [self.out.eq(self.data)]

        with m.Else():
            m.d.sync += [self.DC.load_data.eq(0b1),self.DC.read_or_write.eq(self.r_or_w),self.DC.read_port.eq(self.addre),self.DC.write_data.eq(self.data)]
            m.d.sync += [self.DM.read_or_write.eq(self.r_or_w),self.DM.address.eq(self.addre),self.DM.data.eq(self.data)]
        return m

    def ports(self):

        return [self.r_or_w,self.addre,self.data,self.out]


if __name__ == "__main__":

    m=Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.link= link1 = link()
   
    r_or_w = Signal(1)
    addre = Signal(9)
    data = Signal(9)

    m.d.comb += link1.r_or_w.eq(r_or_w)
    m.d.comb += link1.addre.eq(addre)
    m.d.comb += link1.data.eq(data)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        yield r_or_w.eq(0b1)
        yield addre.eq(0b111111111)
        yield data.eq(0b000000010)

        yield Delay(1e-5)
        yield r_or_w.eq(0b1)
        yield addre.eq(0b111111110)
        yield data.eq(0b000000111)

        yield Delay(1e-5)
        yield r_or_w.eq(0b0)
        yield addre.eq(0b111111110)

        yield Delay(1e-5)
        yield r_or_w.eq(0b0)
        yield addre.eq(0b111111111)

        yield Delay(1e-5)
        yield r_or_w.eq(0b1)
        yield addre.eq(0b111111101)
        yield data.eq(0b000001111)

        yield Delay(1e-5)
        yield r_or_w.eq(0b0)
        yield addre.eq(0b111111101)

    sim.add_sync_process(process, domain="sync")   
    with sim.write_vcd("test.vcd", "test.gtkw", traces=link1.ports()):
        sim.run_until(100e-6, run_passive=True)