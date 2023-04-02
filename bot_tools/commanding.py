import re
from inspect import signature, Parameter

from typing import Any, Callable, Self, Iterable, Iterator, Coroutine, Optional

from .context import Context


class CommandArgumentsMatchError(Exception):
    """Raised when command function arguments don't match names of command pattern groups"""
    pass


class CommandArgumentsTypesError(Exception):
    """Raised when command function arguments have disallowed types"""
    pass


class Command:

    pattern: re.Pattern
    function: Callable
    arg_type_map: dict[str, type]

    allowed_argtypes: set[type] = {str, int, bool, Optional[str], Optional[int], Optional[bool]}

    def __init__(self, pattern: str, function: Callable) -> None:
        self.pattern = re.compile(pattern)
        function_params = list(signature(function).parameters.values())[1:]
        self.arg_type_map = {p.name: str if p.annotation == Parameter.empty else p.annotation for p in function_params}
        for argtype in self.arg_type_map.values():
            if argtype not in Command.allowed_argtypes:
                raise CommandArgumentsTypesError
        if set(self.arg_type_map) != set(self.pattern.groupindex):
            raise CommandArgumentsMatchError
        self.function = function
        
    @staticmethod
    def _optional_argtype(argtype: type) -> type | None:
        if argtype in (Optional[str], Optional[int], Optional[bool]):
            argtype_0, argtype_1 = argtype.__args__
            return argtype_0 if argtype_1 is type(None) else argtype_1
        return None

    def parse(self, text: str) -> dict[str, Any] | None:
        match = self.pattern.fullmatch(text)
        if match is None:
            return None
        parsed_args_dict = match.groupdict()
        for argname, argvalue in parsed_args_dict.items():
            argtype = self.arg_type_map[argname]
            if argtype == str:
                continue
            optional_argtype = self._optional_argtype(argtype)
            if optional_argtype is None:
                parsed_args_dict[argname] = argtype(argvalue)
                continue
            if argvalue is not None:
                parsed_args_dict[argname] = optional_argtype(argvalue)
        return parsed_args_dict
    
    def execute(self, context: Context, **kwargs) -> Coroutine | None:
        return self.function(context, **kwargs)
    

class Commander:

    _data: list[Command]

    def __init__(self, commands: Iterable[Command] = None) -> None:
        self._data = [] if commands is None else list(commands)

    def __iter__(self) -> Iterator[Command]:
        return self._data.__iter__()

    def register(self, pattern: str) -> Callable[[Callable], Callable]:
        def decorator(function: Callable) -> Callable:
            self._data.append(Command(pattern, function))
            return function
        return decorator
    
    def append(self, command: Command) -> None:
       self._data.append(command)
    
    def extend(self, other: Self) -> None:
        self._data.extend(other._data)
