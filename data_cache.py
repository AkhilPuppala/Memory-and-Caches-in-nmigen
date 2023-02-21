from amaranth import *
from amaranth.sim import*
from amaranth.build import Platform
from amaranth.cli import main_parser, main_runner
from amaranth.cli import *
#read_or_write = 0 = read
class data_cache( Elaboratable ):
    def __init__(self):
        self.load_data = Signal(1)
        self.hit = Signal(1)
        self.read_port = Signal(9)
        self.output = Signal(9)
        self.read_or_write = Signal(1)
        self.instr_addr_width = 9
        self.size = 16 #number of instructions
        self.num_of_index_bits = 4
        self.index_bits = self.read_port[:self.num_of_index_bits]
        self.num_of_tag_bits = self.instr_addr_width - self.num_of_index_bits
        self.tag_bits = self.read_port[self.num_of_index_bits:]
        self.data_mem_cache = Array([Signal(unsigned(self.num_of_tag_bits + 9 +1))for i in range(self.size)])
        self.write_index_bits = Signal(self.num_of_index_bits)
        self.write_tag_bits = Signal(self.num_of_tag_bits)
        self.write_data = Signal(9)
        self.valid = Signal(1)

    def elaborate(self,platform):
        m = Module()
        #m.d.comb += self.data_mem_cache[self.index_bits].eq(0b111111000000011)
        with m.If(self.read_or_write.matches(0b0)):
            m.d.comb += [self.valid.eq(self.data_mem_cache[self.index_bits][-1])]
            with m.If(self.valid.matches(0b1) & (self.data_mem_cache[self.index_bits][9:-1]==(self.tag_bits)) ):
                m.d.comb += [self.hit.eq(0b1)]
                m.d.sync += [self.output.eq(self.data_mem_cache[self.index_bits][0:9])]
            with m.Else():       
                m.d.comb += [self.hit.eq(0b0)]
                m.d.comb += [self.load_data.eq(0b0)]

        with m.Else():
            with m.If(self.load_data.matches(0b1)):
                m.d.comb += [self.write_tag_bits.eq(self.read_port[self.num_of_index_bits:]),self.write_index_bits.eq(self.index_bits)]
                #m.d.sync += [self.write_data.eq(self.read_port)]
                m.d.sync += [self.data_mem_cache[self.index_bits].eq(Cat(self.write_data,self.write_tag_bits,0b1))]
        
        return m
        
    def ports(self):
        
        return [self.read_port,self.output,self.write_data,self.read_or_write]


if __name__ == "__main__":

    m=Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.data_cache1 = data_cache1 = data_cache()
   

    read_port = Signal(9)
    output = Signal(9)
    write_data = Signal(9)
    read_or_write = Signal(1)

    m.d.comb += data_cache1.read_or_write.eq(read_or_write)
    m.d.comb += data_cache1.read_port.eq(read_port)
    m.d.comb += data_cache1.write_data.eq(write_data)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        yield read_or_write.eq(0b1)
        yield read_port.eq(0b111111111)
        yield write_data.eq(0b000000010)

        yield Delay(1e-5)
        yield read_or_write.eq(0b1)
        yield read_port.eq(0b111111110)
        yield write_data.eq(0b000000111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield read_port.eq(0b111111110)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield read_port.eq(0b111111111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b1)
        yield read_port.eq(0b111111101)
        yield write_data.eq(0b000001111)

        yield Delay(1e-5)
        yield read_or_write.eq(0b0)
        yield read_port.eq(0b111111101)

    sim.add_sync_process(process, domain="sync")   
    with sim.write_vcd("test.vcd", "test.gtkw", traces=data_cache1.ports()):
        sim.run_until(100e-6, run_passive=True)
 
