KEYWORDS = {
    ">":">",
    "<":"<",
    "+":"+",
    "-":"-",
    ".":"\"",
    ",":"?",
    "[":"$",
    "]":"@",
}

def get_key(dict: dict[int, int], val:int) -> int:
    for key, value in dict.items():
        if val == value:
            return key

    return -1

class Token:
    def __init__(self, token_type:str=None, instruction1:int="") -> None:
        self.token_type = token_type
        self.instruction1 = instruction1

    def __str__(self):
        return f"'{self.token_type}{self.instruction1}'"

    def __repr__(self) -> str:
        return self.__str__()

class Tokeniser:
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        try:
            with open(file_name, "r") as file:
                self.content = file.read()
        except Exception as e:
            print(f"FileOpeningError |> Could not find the file {file_name}. Please input a valid filename.")
            exit()

    def convert_to_tokens(self) -> list[Token]:

        token_list: list[Token] = []

        if len(self.content) <= 0:
            print(f"EOFError |> End of file reached while reading the {self.file_name} file. Is the file empty?")
            exit()

        chars_chain = None
        chars_count = None

        for char in (self.content + "\0"):
            if char not in KEYWORDS.keys():
                continue

            if chars_chain is None:
                if char in ["[", "]"]:
                    token_list.append(Token(char, 1))
                    continue
                chars_chain = char
                chars_count = 1
                continue

            if chars_chain == char:
                chars_count += 1
                continue

            token_list.append(Token(chars_chain, chars_count))
            if char in ["[", "]"]:
                token_list.append(Token(char, 1))
                chars_chain = None
                continue
            chars_chain, chars_count = char, 1

        if chars_chain in KEYWORDS.keys():
            token_list.append(Token(chars_chain, chars_count))

        return token_list

class Compiler:
    def __init__(self, token_list: list[Token]) -> None:
        self.token_list: list[Token] = token_list
        self.brackets_pairs = {}

    def validate_brackets(self) -> None:

        temp_start = []
        for i, token in enumerate(self.token_list):
            if token.token_type not in ["[", "]"]:
                continue

            if token.token_type == "[":
                temp_start.append(i)

            if token.token_type == "]":
                try:
                    last_i = temp_start.pop()
                    self.brackets_pairs[last_i] = i
                except IndexError:
                    display_list = self.token_list[i-min(3, i):i+3]
                    construct_str = '"' + "".join(list(map(lambda token: token.token_type+str(token.instruction1), display_list))) + '"\n ' + ("~~"*(min(3, i))) + "^^"
                    print("InvalidBFSyntax |> ']' Closed without opening.\n" + construct_str)
                    exit()

        if len(temp_start) != 0:
            i = temp_start[-1]
            display_list = self.token_list[i-min(3, i):i+3]
            construct_str = '"' + "".join(list(map(lambda token: token.token_type+str(token.instruction1), display_list))) + '"\n ' + ("~~"*(min(3, i))) + "^^"
            print("InvalidBFSyntax |> '[' Not closed.\n"+construct_str)
            exit()

    def compile(self, file_name):
        self.validate_brackets()

        compiled = ""
        for i, token in enumerate(self.token_list):
            if token.token_type not in ["[", "]"]:
                compiled += KEYWORDS[token.token_type] + ("" if token.instruction1 == 1 else str(token.instruction1))

            if token.token_type == "[":
                compiled += KEYWORDS[token.token_type] + str(self.brackets_pairs[i] + 1)
            if token.token_type == "]":
                start_i = get_key(self.brackets_pairs, i)
                if start_i == -1:
                    print(f"InvalidBFSyntax |> An Unexpected error has occured. Please try again.")
                compiled += KEYWORDS[token.token_type] + str(start_i + 1)

        compiled += "!"
        with open(file_name, "wb") as file:
            file.write(compiled.encode("ascii"))

def main():
    import sys, os
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
        if not (file_name.endswith(".bf") and os.path.exists(file_name)):
            print(f"File {file_name!r} doesn't exist. Please input a valid '.bf' file.")
            return

        token_machine = Tokeniser(file_name)
        token_list = token_machine.convert_to_tokens()
        compiler = Compiler(token_list)
        compiler.compile(file_name[:-3] + ".bkb")
    else:
        print(f"USAGE: `python {__file__} <file_name>.bkb`")

if __name__ == "__main__":
    main()