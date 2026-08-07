import inspect
import argparse
import logging
       
class CommandBuilder() :
    def __init__(self, prog = "classroom", description= "GitHub course administration tool", **args):
        self.parser = argparse.ArgumentParser(prog=prog, description=description, formatter_class=argparse.RawDescriptionHelpFormatter, **args)
        self.subparsers = self.parser.add_subparsers(dest="command",required=True)

    def addCommand(self, handler, **args)->SubCommandBuilder: 
        return SubCommandBuilder(self, handler, **args)

    def run(self):
        try:
            args = self.parser.parse_args()
            sig = inspect.signature(args.run)

            kwargs = {
                name: getattr(args, name)
                for name in sig.parameters
                if hasattr(args, name)
            }

            return args.run(**kwargs)
        except SystemExit:
            raise
        except:
            logging.exception("Error!")
            raise

class SubCommandBuilder():
    def __init__(self, commandBuilder, handler, **args):
        self.sub = commandBuilder.subparsers.add_parser(handler.__name__,  formatter_class=argparse.RawDescriptionHelpFormatter, **args)
        self.sub.set_defaults(run=handler)
        self.parameters = inspect.signature(handler).parameters
        self.handler_name = handler.__name__

    def _validate_param(self, name):
        if name.replace("-", "_") not in self.parameters:
            raise ValueError(
                f"Argument '{name}' is not a parameter of {self.handler_name}"
            )

    def add_argument(self, *args, **kargs):
        self._validate_param(args[0].lstrip("-"))
        self.sub.add_argument(*args, **kargs)
        return self

from pathlib import Path


class File:
    def __init__(self, path):
        self.path = Path(path).expanduser()

        if not self.path.exists():
            raise ValueError(f"File does not exist: {self.path}")

        if not self.path.is_file():
            raise ValueError(f"Not a file: {self.path}")

    def read(self):
        return self.path.read_bytes()

    def __call__(self):
        return self.read()

    def __str__(self):
        return str(self.path)


class LineFile(File):
    def read(self):
        return self.path.read_text(encoding="utf-8").splitlines()
