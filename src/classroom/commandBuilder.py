import inspect
import argparse
       
class CommandBuilder() :
    def __init__(self, prog = "classroom", description= "GitHub course administration tool", **args):
        self.parser = argparse.ArgumentParser(prog=prog, description=description, formatter_class=argparse.RawDescriptionHelpFormatter, **args)
        self.subparsers = self.parser.add_subparsers(dest="command",required=True)

    def addCommand(self, handler, **args)->SubCommandBuilder: 
        return SubCommandBuilder(self, handler, **args)

    def run(self):

        args = self.parser.parse_args()
        sig = inspect.signature(args.run)

        kwargs = {
            name: getattr(args, name)
            for name in sig.parameters
            if hasattr(args, name)
        }

        return args.run(**kwargs)

class SubCommandBuilder():
    def __init__(self, commandBuilder, handler, **args):
        self.sub = commandBuilder.subparsers.add_parser(handler.__name__,  formatter_class=argparse.RawDescriptionHelpFormatter, **args)
        self.sub.set_defaults(run=handler)
        self.parameters = inspect.signature(handler).parameters

    def _validate_param(self, name):
        if name.replace("-", "_") not in self.parameters:
            raise ValueError(
                f"Argument '{name}' is not a parameter of {self.handler.__name__}"
            )

    def add_argument(self, *args, **kargs):
        self._validate_param(args[0].lstrip("-"))
        self.sub.add_argument(*args, **kargs)
        return self
