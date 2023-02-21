from amaranth import *
from amaranth.sim import*
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner


class Instruction_cache():
    def __init__(self,addr_width):
        # number of instructions it can store
        self.size = 16
        #width of the instruction
        self.instr_width = 32
        #width of the instruction address
        self.instr_addr_width = addr_width
        # No of index bits
        self.index_bits = 4
        #No of tag bits 
        self.tag_bits = addr_width - self.index_bits
        self.mem = Array([Signal(unsigned(self.tag_bits+self.instr_width+1)) for _ in range(self.size)])
        self.ReadWrite_port_A = Signal(self.instr_addr_width)
        self.ReadWrite_port_I = Signal(self.instr_width)
        self.load = Signal(1,reset = 0b0)
        self.hit = Signal(1,reset=0b0)
        self.load_inst = Signal(1)
        self.index = self.ReadWrite_port_A[0:self.index_bits]
        self.valid = Signal(1)
        self.tag = self.ReadWrite_port_A[self.index_bits:-1]
        
    def elaborate(self,Platform):
        m = Module()
        m.d.comb += self.hit.eq(0b0)   
        m.d.sync += self.mem[self.index].eq(Const(0b10000000000000000000000000000001100011))
        #m.d.sync += self.mem[0b1110].eq(0b10000000000000000000000000000000000111)
        m.d.sync += self.valid.eq(self.mem[self.index][-1])

        with m.If(self.load == 0b0):

            with m.If(self.valid == 0b1 ):
                with m.If(self.mem[self.index][self.instr_width:-1] == self.tag):
                    m.d.sync += self.ReadWrite_port_I.eq(self.mem[self.index][0:self.instr_width])
                    m.d.comb += self.hit.eq(0b1)
                    m.d.comb += self.load.eq(0b0)
            with m.Else():
                m.d.comb += self.hit.eq(0b0)
                #m.d.sync += self.ReadWrite_port_I.eq(0x111111111)
                #m.d.comb += self.load.eq(0b1)
        with m.Else():
            with m.If(self.load_inst == 0b1):
                m.d.sync += self.mem[self.ReadWrite_port_A].eq(Cat(self.ReadWrite_port_I,self.ReadWrite_port_A[self.index_bits:],0b1))
                m.d.comb += self.load.eq(0b0)

        return m   

    def ports(self):
        return [self.ReadWrite_port_A,self.ReadWrite_port_I,self.load,self.hit,self.load_inst]  

if __name__ == "__main__":

    m=Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.instruction_cache1 = instruction_cache1 = Instruction_cache(9)

    ReadWrite_port_A = Signal(9)
    ReadWrite_port_I = Signal(32)

    m.d.comb += instruction_cache1.ReadWrite_port_A.eq(ReadWrite_port_A)
    m.d.comb += instruction_cache1.ReadWrite_port_I.eq(ReadWrite_port_I)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        #yield Delay(1e-5)
        yield ReadWrite_port_A.eq(0b000001111)
        #yield ReadWrite_port_I.eq(0b000000010)
        #yield Delay(1e-5)
        #yield ReadWrite_port_A.eq(0b1111)
        #yield Delay(1e-5)
        #yield ReadWrite_port_A.eq(0b1110)

    sim.add_sync_process(process, domain="sync")   
    with sim.write_vcd("test.vcd", "test.gtkw", traces=instruction_cache1.ports()):
        sim.run_until(100e-6, run_passive=True)   

