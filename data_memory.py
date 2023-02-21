from amaranth import *
from amaranth.sim import*
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner

#read = 0, write = 1
class data_mem( Elaboratable ):
    def __init__(self):
        self.read_or_write = Signal(1)
        self.address = Signal(9)
        self.data = Signal(9)
        self.data_memory = Array([Signal(unsigned(9)) for i in range(512)])

    def elaborate(self,platform):
        m = Module()
        with m.If(self.read_or_write.matches(0b0)):
            m.d.sync += [self.data.eq(self.data_memory[self.address])]
        with m.Else():
            m.d.sync += [self.data_memory[self.address].eq(self.data)]
        return m

    def ports(self):
        return [self.read_or_write,self.address,self.data] 
        
if __name__ == "__main__":

    m=Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.data_mem1 = data_mem1 = data_mem()
   

    read_or_write = Signal(1)
    address = Signal(9)
    data = Signal(9)

    m.d.comb += data_mem1.read_or_write.eq(read_or_write)
    m.d.comb += data_mem1.address.eq(address)
    m.d.comb += data_mem1.data.eq(data)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        yield read_or_write.eq(0b1)
        yield address.eq(0b111111111)
        yield data.eq(0b000000010)

        yield Delay(1e-5)
        yield read_or_write.eq(0b1)
        yield address.eq(0b111111110)
        yield data.eq(0b000000111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield address.eq(0b111111110)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield address.eq(0b111111111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b1)
        yield address.eq(0b111111101)
        yield data.eq(0b000001111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield address.eq(0b111111101)


    sim.add_sync_process(process, domain="sync")   
    with sim.write_vcd("test.vcd", "test.gtkw", traces=data_mem1.ports()):
        sim.run_until(100e-6, run_passive=True)


            



