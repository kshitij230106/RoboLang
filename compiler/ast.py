from dataclasses import dataclass
from typing import List

# ==========================================
# Base AST Node
# ==========================================


class ASTNode:
    pass


# ==========================================
# Program
# ==========================================


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


# ==========================================
# Commands
# ==========================================


@dataclass
class MoveCommand(ASTNode):
    distance: int
    line: int


@dataclass
class TurnCommand(ASTNode):
    direction: str
    line: int
