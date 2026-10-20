from dataclasses import dataclass
from typing import List

# ==========================================
# Base AST Node
# ==========================================


class ASTNode:

    def to_dict(self):
        return {"type": type(self).__name__}


# ==========================================
# Program
# ==========================================


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

    def to_dict(self):
        return {
            "type": "Program",
            "children": [
                statement.to_dict()
                for statement in self.statements
            ],
        }


# ==========================================
# Commands
# ==========================================


@dataclass
class MoveCommand(ASTNode):
    distance: int
    line: int

    def to_dict(self):
        return {
            "type": "MoveCommand",
            "distance": self.distance,
            "line": self.line,
        }


@dataclass
class TurnCommand(ASTNode):
    direction: str
    line: int

    def to_dict(self):
        return {
            "type": "TurnCommand",
            "direction": self.direction,
            "line": self.line,
        }
