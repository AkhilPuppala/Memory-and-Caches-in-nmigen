from amaranth import *
from amaranth.sim import*
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner

class Instruction_memory( Elaboratable ):
    def __init__(self):
        self.RWA = Signal(9)
        self.RWI = Signal(32)
        self.instruction_mem = Array([Signal(unsigned(9)) for i in range(512)])


    def elaborate(self,platform):
        m = Module()
        #m.d.comb += self.instruction_mem[0b111111111].eq(0x000000111)
        #m.d.comb += self.instruction_mem[0b000000010].eq(0x000000011)
        m.d.sync += [self.RWI.eq(self.instruction_mem[self.RWA])]
        return m

    def ports(self):
        return [self.RWA,self.RWI]

        
if __name__ == "__main__":

    m=Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.instruction_memory1 = instruction_memory1 = Instruction_memory()
    RWA = Signal(9)
    m.d.comb += instruction_memory1.RWA.eq(RWA)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        yield RWA.eq(0b111111111)
        yield Delay(1e-5)
        yield RWA.eq(0b000000010)
        yield Delay(1e-5)
        yield RWA.eq(0b111111111)

    sim.add_sync_process(process, domain="sync")   
    with sim.write_vcd("test.vcd", "test.gtkw", traces=instruction_memory1.ports()):
        sim.run_until(100e-6, run_passive=True)
 


            