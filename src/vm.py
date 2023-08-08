from typing import Tuple

OP_TYPES = [
    "&", # -> MOV
    "#", # -> LOAD
    "+", # -> ADD
    "-", # -> SUB
    "?", # -> INP
    "\"", # -> OUT
    "@", # -> JUMP_TO_IF_!0
    "!", # -> Terminate
    ">", # -> MOV_FRONT
    "<", # -> MOV_BACK,
    "$", # -> JUMP_TO_IF_0,
]

KEYWORDS = OP_TYPES + list(map(lambda x: str(x), range(0, 10)))

class Instruction:
    def __init__(self, instruction_type:str, info1:int=None, info2:int = None) -> None:
        if instruction_type not in OP_TYPES:
            print(f"InvalidOPCode |> {instruction_type!r} is not a valid OP Code type.")
            exit()

        self.instruction_type = instruction_type
        self.info1: int|None = info1
        self.info2: int|None = info2

    def __str__(self):
        return f"'{self.instruction_type} {self.info1} {self.info2}'"

    def __repr__(self) -> str:
        return self.__str__()

class Parser:
    def __init__(self, file_name) -> None:
        try:
            with open(file_name, "rb") as file:
                self.content = file.read().decode("ascii")
        except Exception as e:
            print(f"InvalidBKBFile |> Could not find the file {file_name!r}. Please input a valid filename.")
            exit()
        #self.content: str = file_name
        self.char_idx: int = 0

    def increment(self) -> None:
        self.char_idx += 1
        while self.char_idx < len(self.content) and self.content[self.char_idx] not in KEYWORDS:
            self.char_idx += 1

    def convert_to_instructions(self) -> list[Instruction]:

        inst_list: list[Instruction] = []

        while self.char_idx < len(self.content):
            char = self.content[self.char_idx]
            if char not in OP_TYPES:
                print(f"InvalidOPCode |> {char!r} is not a valid OP Code type.")
                exit()

            instr = self.construct_instruction(char)
            #print(instr)
            inst_list.append(instr)

        return inst_list

    def construct_instruction(self, char: str) -> Instruction:
        try:
            if (self.char_idx + 1) < len(self.content) and self.content[self.char_idx + 1].isdecimal():
                info1 = self.construct_info()
            else:
                self.increment()
                return Instruction(char)

            if (self.char_idx) < len(self.content) and self.content[self.char_idx].isdecimal():
                info2 = self.construct_info()
                return Instruction(char, info1, info2)

            return Instruction(char, info1)
        except Exception:
            print(f"InvalidSequence |> Invalid Sequence of characters for instruction: {char!r}, char num: {self.char_idx - 1}")
            exit()

    def construct_info(self) -> int:
        self.increment()
        new_int = ""
        while self.char_idx < len(self.content) and (self.content[self.char_idx]).isdecimal():
            new_int += self.content[self.char_idx]
            self.increment()

        return int(new_int)

class VM:
    def __init__(self, instructions: list[Instruction]) -> None:
        self.r_memory: list[int] = [0]
        self.l_memory: list[int] = []

        self.pointer: int = 0

        self.instructions: list[Instruction] = instructions

    def run(self) -> int:

        i = 0 #instruction_pointer

        while True:
            
            if i >= len(self.instructions):
                print(f"InvalidInstructionID |> There is no instruction in the {i!r}th* position. Maybe terminate the program?")
                exit()
            instruction = self.instructions[i]

            #print(instruction)

            if instruction.instruction_type == OP_TYPES[0]: # -> MOV
                self.JUMP_MEMORY(instruction.info1)

            elif instruction.instruction_type == OP_TYPES[1]: # -> LOAD
                self.LOAD_MEMORY_TO_POINTER(instruction.info1, instruction.info2)

            elif instruction.instruction_type == OP_TYPES[2]: # -> ADD
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.ADD_MEMORY_TO_POINTER(instruction.info1, instruction.info2)

            elif instruction.instruction_type == OP_TYPES[3]: # -> SUB
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.SUB_MEMORY_FROM_POINTER(instruction.info1, instruction.info2)

            elif instruction.instruction_type == OP_TYPES[4]: # -> INP
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.USER_INP_TO_POINTER(instruction.info1)

            elif instruction.instruction_type == OP_TYPES[5]: # -> OUT
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.OUT_FROM_POINTER(instruction.info1, instruction.info2)

            elif instruction.instruction_type == OP_TYPES[6]: # -> JUMP_TO_IF_!0
                lis, loc = self.get_loc_pointer()
                if lis[loc] != 0: i = instruction.info1 - 1

            elif instruction.instruction_type == OP_TYPES[7]: # -> Terminate
                return 0

            elif instruction.instruction_type == OP_TYPES[8]: # -> MOV_FRONT
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.JUMP_RELATIVE(instruction.info1)

            elif instruction.instruction_type == OP_TYPES[9]: # -> MOV_BACK
                if instruction.info1 is None:
                    instruction.info1 = 1
                self.JUMP_RELATIVE(-instruction.info1)

            elif instruction.instruction_type == OP_TYPES[10]: # -> JUMP_TO_IF_0
                lis, loc = self.get_loc_pointer()
                if lis[loc] == 0: i = instruction.info1 - 1

            i += 1

    def get_loc_pointer(self, loc:int=None) -> Tuple[list[int], int]:
        if loc is None:
            loc = self.pointer

        else:    
            self.JUMP_MEMORY(loc, False)

        if loc >= 0:
            return self.r_memory, loc
        else:
            return self.l_memory, (-1 * loc) - 1

    def JUMP_MEMORY(self, loc: int, jump: bool=True) -> None:
        if jump: self.pointer = loc
        if loc >= 0:
            if loc >= len(self.r_memory):
                self.r_memory += [0] * (loc - len(self.r_memory) + 1)
        else:
            loc = (-1 * loc) - 1
            if loc >= len(self.l_memory):
                self.l_memory += [0] * (loc - len(self.l_memory) + 1)

    def JUMP_RELATIVE(self, amt) -> None:
        self.JUMP_MEMORY(self.pointer + amt)

    def LOAD_MEMORY_TO_POINTER(self, amt: int, mem: int=None):
        lis, loc = self.get_loc_pointer(mem)
        lis[loc] = amt

        while lis[loc] > 255:
            lis[loc] -= 255
        while lis[loc] < 0:
            lis[loc] = 255 + lis[loc]

    def ADD_MEMORY_TO_POINTER(self, amt: int, mem: int=None):
        lis, loc = self.get_loc_pointer(mem)
        lis[loc] += amt

        while lis[loc] > 255:
            lis[loc] -= 255

    def SUB_MEMORY_FROM_POINTER(self, amt: int, mem: int=None):
        lis, loc = self.get_loc_pointer(mem)
        lis[loc] -= amt

        while lis[loc] < 0:
            lis[loc] = 255 + lis[loc]

    def USER_INP_TO_POINTER(self, times:int=None):
        for _ in range(times):
            inp = input("?")
            try:
                self.LOAD_MEMORY_TO_POINTER(ord(inp))
            except TypeError:
                print(f"InvalidInput |> Expected a character, got: {inp!r}")
                exit()

    def OUT_FROM_POINTER(self, times: int=None, mem: int=None):
        for _ in range(times):
            lis, loc = self.get_loc_pointer(mem)
            print(chr(lis[loc]), end="")

    def __str__(self):
        return "..." + str(self.l_memory)[1:] + str(self.r_memory)[:-1] + "...\n" + "pointer: " + str(self.pointer)

def main():
    import sys, os
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
        if not (file_name.endswith(".bkb") and os.path.exists(file_name)):
            print(f"File {file_name!r} doesn't exist. Please input a valid '.bkb' file.")
            return

        parser = Parser(file_name)
        vm = VM(parser.convert_to_instructions())
        vm.run()
        if ("--verbose" in sys.argv) or ("-v" in sys.argv):
            print("\n-----\nExtra Info:\n")
            print(vm)
    else:
        print(f"USAGE: `python {__file__} <file_name>.bkb` [--verbose/-v]")

if __name__ == "__main__":
    main()