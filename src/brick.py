import sys, os
import vm, bf_compiler

""" parser = vm.Parser(
    '+8$30>+4$16>+2>+3>+3>+<4-@5>+>+>->2+$27<@25<-@2>2">-3"+7""+3">2"<-"<"+3"-6"-8">2+">+2"!'
) """

def run(file_name):
    parser = vm.Parser(file_name)
    main_vm = vm.VM(parser.convert_to_instructions())
    main_vm.run()

def compile(file_name):
    token_machine = bf_compiler.Tokeniser(file_name)
    token_list = token_machine.convert_to_tokens()
    compiler = bf_compiler.Compiler(token_list)
    compiler.compile(file_name[:-3] + ".bkb")

def main():
    if len(sys.argv) >= 3:
        main_arg = sys.argv[2]
        file_name = sys.argv[1]
        if main_arg in ["--run", "-r"]:
            if not (file_name.endswith(".bkb") and os.path.exists(file_name)):
                print(f"FileOpeningError |> File {file_name!r} doesn't exist. Please input a valid '.bkb' file.")
                return
            run(file_name)
            return

        elif main_arg in ["--compile", "-c"]:
            if not (file_name.endswith(".bf") and os.path.exists(file_name)):
                print(f"FileOpeningError |> File {file_name!r} doesn't exist. Please input a valid '.bf' file.")
                return
            
            compile(file_name)
            return

        elif main_arg in ["--compile-run", "-cr"]:
            if not (file_name.endswith(".bf") and os.path.exists(file_name)):
                print(f"FileOpeningError |> File {file_name!r} doesn't exist. Please input a valid '.bf' file.")
                return
            
            compile(file_name)
            run(file_name[:-3] + ".bkb")
            return
    
    print(f"USAGE: `python {__file__} <file_name> (--compile, -c)/(--run, -r)/(--compile-run, -cr)`")

if __name__ == "__main__":
    main()