from nmigen import *
from instruction_memory import *
from instruction_cache import *

class Imem(Elaboratable):
    def __init__(self):
        self.IC = Instruction_cache(9)
        self.IM = Instruction_memory()
        self.req_addr = Signal(9)
        self.instruction = Signal(32)
        self.branch = Signal(1)    #branch = 1 if branch is taken
        self.target_add = Signal(9)
    def elaborate(self):
        m = Module()
        m.submodules.IC = self.IC
        m.submodules.IM = self.IM
        
        m.d.sync += self.IC.ReadWrite_port_A.eq(self.req_addr)
        #Create Delay 
        with m.If(self.IC.hit == 0b1):
            m.d.sync += self.instruction.eq(self.IC.ReadWrite_port_I)
        with m.Else():
            m.d.sync += self.IM.RWA.eq(self.req_addr)
            #Create Delay
            m.d.sync += self.IC.load_inst.eq(0b1)
            m.d.sync += [self.instruction.eq(self.IM.RWI),self.IC.ReadWrite_port_A.eq(self.RWA),self.IC.ReadWrite_port_I.eq(self.IM.RWI)]
            

        with m.If(self.branch == 0b1):
            m.d.sync += self.IM.RWA.eq(self.target_add)
            #create delay
            m.d.sync += [self.IC.load.eq(0b0)]
            m.d.sync += [self.IC.load_inst.eq(0b1),self.IC.ReadWrite_port_A.eq(self.target_add),self.IC.ReadWrite_port_I.eq(self.IM.RWI)]

            m.d.sync += self.IM.RWA.eq(self.target_add + 1)
            #create delay
            m.d.sync += [self.IC.load.eq(0b0)]
            m.d.sync += [self.IC.load_inst.eq(0b1),self.IC.ReadWrite_port_A.eq(self.target_add +1),self.IC.ReadWrite_port_I.eq(self.IM.RWI)]

            m.d.sync += self.IM.RWA.eq(self.target_add +2)
            #create delay
            m.d.sync += [self.IC.load.eq(0b0)]
            m.d.sync += [self.IC.load_inst.eq(0b1),self.IC.ReadWrite_port_A.eq(self.target_add+2),self.IC.ReadWrite_port_I.eq(self.IM.RWI)]

            m.d.sync += self.IM.RWA.eq(self.target_add +3)
            #create delay
            m.d.sync += [self.IC.load.eq(0b0)]
            m.d.sync += [self.IC.load_inst.eq(0b1),self.IC.ReadWrite_port_A.eq(self.target_add+3),self.IC.ReadWrite_port_I.eq(self.IM.RWI)]

            m.d.comb += self.branch.eq(0b0)
            










            


    
        
    
