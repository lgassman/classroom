from .commandBuilder import CommandBuilder, SubCommandBuilder

def hello():
    print("Hello!")


def pepe(titulo, fin):
    print(f"{titulo} Pepe {fin}")

def main():
     builder = CommandBuilder()
     builder.addCommand(pepe, help="saluda a pepe").add_argument("--titulo", type=str, default="Dr.").add_argument("--fin", type=str, default="!!")
     builder.addCommand(hello, help="say hello")
     builder.run()


if __name__ == "__main__":
    raise SystemExit(main())