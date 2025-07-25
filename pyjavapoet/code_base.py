from abc import ABC, abstractmethod

from pyjavapoet.code_writer import CodeWriter


class Code[C: "Code"](ABC):

    @abstractmethod
    def emit(self, code_writer: "CodeWriter") -> None:
        ...

    @abstractmethod
    def to_builder(self) -> "Code.Builder[C]":
        ...

    def copy(self) -> C:
        return self.to_builder().build()
    
    def __deepcopy__(self, memo: dict) -> C:
        return self.copy()
    
    def __copy__(self) -> C:
        return self.copy()
    
    def __str__(self) -> str:
        writer = CodeWriter()
        self.emit(writer)
        return str(writer)

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Code):
            return False
        return str(self) == str(other)

    class Builder [T: "Code"](ABC):
        @abstractmethod
        def build(self) -> T:
            ...
