from __future__ import annotations #Para compatibilidad con 3.10
import inspect
import argparse
import logging
from .config import config


class CommandBuilder() :
    def __init__(self, prog = "classroom", description= "GitHub course administration tool", **args):
        self.parser = argparse.ArgumentParser(prog=prog, description=description, formatter_class=argparse.RawDescriptionHelpFormatter, **args)
        self.parser.add_argument("--log", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.subparsers = self.parser.add_subparsers(dest="command",required=True)

    def addCommand(self, handler, **args)->SubCommandBuilder: 
        return SubCommandBuilder(self, handler, **args)

    def run(self):
        try:
            args = self.parser.parse_args()
            configure_logging(log_level=args.log)
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


def line_file(path):
    path = Path(path).expanduser()

    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    return path.read_text(encoding="utf-8").strip().splitlines()

#Esto suena a una hackeada que tengo que repensar. la unica salida que estoy escribiendo 
#es por log, eso hace que el INFO se le remueva el header para que parezca stdout, pero 
#sigue siendo stderr. Quizás debería cambiar todos los logging.info por print
class ClassroomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return super().format(record)


def configure_logging(log_level = None):
    level_name = log_level or config.get("log_level", "INFO")
    log_format = config.get("log_format", "%(levelname)s: %(message)s")

    level = getattr(logging, level_name.upper(), logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(ClassroomFormatter(log_format))

    logging.basicConfig(level=level, handlers=[handler])
