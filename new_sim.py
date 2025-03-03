import m5
from m5.objects import *

# Define L1 Instruction Cache
class L1ICache(Cache):
    def __init__(self, size='32kB', assoc=2):
        super().__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20

# Define L1 Data Cache
class L1DCache(Cache):
    def __init__(self, size='32kB', assoc=2):
        super().__init__()
        self.size = size
        self.assoc = assoc
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20

# Create the system
system = System()

# Set the clock frequency
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Memory setup
system.mem_mode = 'timing'  # Use 'atomic' for a faster, less detailed simulation
system.mem_ranges = [AddrRange('512MB')]

# Define CPU (Basic Pipeline)
system.cpu = TimingSimpleCPU()

# Create memory bus
system.membus = SystemXBar()

system.cpu.createInterruptController()

if isinstance(system.cpu, (DerivO3CPU, TimingSimpleCPU)):
    system.cpu.interrupts[0].pio = system.membus.master
    system.cpu.interrupts[0].int_requestor = system.membus.slave

# Add a Branch Predictor
system.cpu.branchPred = TournamentBP()

# Create L1 instruction and data caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Connect caches to CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Connect caches to memory bus
system.cpu.icache.mem_side = system.membus.slave
system.cpu.dcache.mem_side = system.membus.slave

# Create memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]

# Connect memory controller to the system memory bus
system.mem_ctrl.port = system.membus.master

# Create system workload
system.workload = SEWorkload.init_compatible('tests/test-progs/hello/bin/x86/linux/hello')

# Define the process to run
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process
system.cpu.createThreads()

# Create root and instantiate the simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting the simulation...")

# Ensure statistics are reset before running
m5.stats.reset()

# Run the simulation
exit_event = m5.simulate()

# Ensure statistics are dumped at the end
m5.stats.dump()

print(f"Simulation finished at tick {m5.curTick()} due to {exit_event.getCause()}")
