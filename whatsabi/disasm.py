from typing import Dict, List, Optional
from .abi import ABI, ABIFunction, ABIEvent
from .utils import hexlify, arrayify, zero_pad, bytes_to_int

OpCode = int

# Some opcodes we care about, doesn't need to be a complete list
opcodes: Dict[str, OpCode] = {
    "STOP": 0x00,
    "EQ": 0x14,
    "ISZERO": 0x15,
    "CALLVALUE": 0x34,
    "CALLDATASIZE": 0x36,
    "JUMPI": 0x57,
    "JUMPDEST": 0x5B,
    "PUSH1": 0x60,
    "PUSH4": 0x63,
    "PUSH32": 0x7F,
    "DUP1": 0x80,
    "LOG1": 0xA1,
    "LOG4": 0xA4,
}

# Return PUSHN width of N if PUSH instruction, otherwise 0
def push_width(instruction: OpCode) -> int:
    if not opcodes["PUSH1"] <= instruction <= opcodes["PUSH32"]:
        return 0
    return instruction - opcodes["PUSH1"] + 1


def is_push(instruction: OpCode) -> bool:
    return opcodes["PUSH1"] <= instruction <= opcodes["PUSH32"]


def is_log(instruction: OpCode) -> bool:
    return opcodes["LOG1"] <= instruction <= opcodes["LOG4"]


# BytecodeIter takes EVM bytecode and handles iterating over it with correct
# step widths, while tracking N buffer of previous offsets for indexed access.
# This is useful for checking against sequences of variable width
# instructions.
class BytecodeIter:
    bytecode: bytes
    next_step: int
    next_pos: int
    pos_buffer: List[int]
    pos_buffer_size: int

    def __init__(self, bytecode: str, config: Optional[Dict[str, int]] = {}):
        self.next_step = 0
        self.next_pos = 0
        self.pos_buffer_size = max(config.get("buffer_size", 1), 1)
        self.pos_buffer = []

        self.bytecode = arrayify(bytecode)

    def has_more(self) -> bool:
        return len(self.bytecode) > self.next_pos

    def next(self) -> OpCode:
        if len(self.bytecode) <= self.next_pos:
            return opcodes["STOP"]

        instruction = self.bytecode[self.next_pos]
        width = push_width(instruction)

        # TODO: Optimization: Could use a circular buffer
        if len(self.pos_buffer) >= self.pos_buffer_size:
            self.pos_buffer.pop(0)
        self.pos_buffer.append(self.next_pos)

        self.next_step += 1
        self.next_pos += 1 + width

        return instruction

    # step is the current instruction position that we've iterated over. If
    # iteration has not begun, then it's -1.
    def step(self) -> int:
        return self.next_step - 1

    # pos is the byte offset of the current instruction we've iterated over

    # If iteration has not begun then it's -1.
    def pos(self) -> int:
        if not self.pos_buffer:
            return -1
        return self.pos_buffer[-1]

    # at returns instruction at an absolute byte position or relative negative
    # buffered step offset. Buffered step offsets must be negative and start
    # at -1 (current step).
    def at(self, pos_or_relative_step: int) -> OpCode:
        pos = pos_or_relative_step
        if pos < 0:
            pos = self.pos_buffer[len(self.pos_buffer) + pos]
            if pos is None:
                raise Exception("buffer does not contain relative step")
        return self.bytecode[pos]

    # value of last next-returned OpCode (should be a PUSHN intruction)
    def value(self):
        return self.value_at(-1)

    # value_at returns the variable width value for PUSH-like instructions (or
    # empty value otherwise), at pos pos can be a relative negative count for
    # relative buffered offset.
    def value_at(self, pos_or_relative_step):
        pos = pos_or_relative_step
        if pos < 0:
            pos = self.pos_buffer[len(self.pos_buffer) + pos]
            if pos is None:
                raise Exception("buffer does not contain relative step")
        instruction = self.bytecode[pos]
        width = push_width(instruction)
        return self.bytecode[pos + 1 : pos + 1 + width]


def abi_from_bytecode(bytecode: str) -> ABI:
    abi: ABI = []

    # JUMPDEST lookup
    jumps = {}  # function hash -> instruction offset
    dests = {}  # instruction offset -> bytes offset
    not_payable = {}  # instruction offset -> bytes offset

    last_push32 = bytes()  # Track last push32 to find log topics
    in_jump_table = True

    code = BytecodeIter(bytecode, {"buffer_size": 4})

    # TODO: Optimization: Could optimize finding jumps by loading JUMPI first
    # (until the jump table window is reached), then sorting them and seeking
    # to each JUMPDEST.

    while code.has_more():
        inst = code.next()
        pos = code.pos()
        step = code.step()

        # Track last PUSH32 to find LOG topics
        # This is probably not bullet proof but seems like a good starting point
        if inst == opcodes["PUSH32"]:
            last_push32 = code.value()
            continue
        elif is_log(inst) and last_push32:
            abi.append({"type": "event", "hash": hexlify(last_push32)})
            continue

        # Find JUMPDEST labels
        if inst == opcodes["JUMPDEST"]:
            # Index jump destinations so we can check against them later
            dests[pos] = step

            # Check whether a JUMPDEST has non-payable guards
            #
            # We look for a sequence of instructions that look like:
            # JUMPDEST CALLVALUE DUP1 ISZERO
            #
            # We can do direct positive indexing because we know that there
            # are no variable-width instructions in our sequence.
            if (
                code.at(pos + 1) == opcodes["CALLVALUE"]
                and code.at(pos + 2) == opcodes["DUP1"]
                and code.at(pos + 3) == opcodes["ISZERO"]
            ):
                not_payable[pos] = step
                # TODO: Optimization: Could seek ahead 3 pos/count safely

            # Check whether we've reached the end of the selector jump table,
            # first time we see: JUMPDEST CALLDATASIZE
            if in_jump_table and code.at(pos + 1) == opcodes["CALLDATASIZE"]:
                in_jump_table = False

            continue

        if not in_jump_table:
            continue  # Skip searching for function selectors at this point

        # Find callable function selectors:
        #
        # https://github.com/ethereum/solidity/blob/242096695fd3e08cc3ca3f0a7d2e06d09b5277bf/libsolidity/codegen/ContractCompiler.cpp#L333
        #
        # We're looking for a sequence of opcodes that looks like:
        #
        #    DUP1 PUSH4 0x2E64CEC1 EQ PUSH1 0x37    JUMPI
        #    DUP1 PUSH4 <BYTE4>    EQ PUSHN <BYTEN> JUMPI
        #    80   63    ^          14 60-7f ^       57
        #               Selector            Dest
        #
        # We can reliably skip checking for DUP1 if we're only searching
        # within `inJumpTable` range#
        if (
            code.at(-1) == opcodes["JUMPI"]
            and is_push(code.at(-2))
            and code.at(-3) == opcodes["EQ"]
            and is_push(code.at(-4))
        ):
            value = code.value_at(-4)
            if len(value) < 4:
                value = zero_pad(value, 4)
            selector = hexlify(value)
            offset_dest = bytes_to_int(code.value_at(-2))
            jumps[selector] = offset_dest
            continue

        if (
            code.at(-1) == opcodes["JUMPI"]
            and is_push(code.at(-2))
            and code.at(-3) == opcodes["ISZERO"]
        ):
            selector = "0x00000000"
            offset_dest = bytes_to_int(code.value_at(-2))
            jumps[selector] = offset_dest
            continue

    for selector, offset in jumps.items():
        if offset not in dests:
            continue
        abi.append(
            {
                "type": "function",
                "selector": selector,
                "payable": offset not in not_payable,
            }
        )
    return abi
