from dataclasses import dataclass
from typing import List

from compiler.ast import Program, MoveCommand, TurnCommand

# ==========================================
# IR Instructions
# ==========================================


@dataclass
class IRInstruction:
    opcode: str
    operand: object = None

    def __str__(self):
        if self.operand is None:
            return self.opcode

        return f"{self.opcode} {self.operand}"


# ==========================================
# IR Program
# ==========================================


@dataclass
class IRProgram:
    instructions: List[IRInstruction]

    def __str__(self):

        if not self.instructions:
            return "(empty IR)"

        lines = []

        for index, instruction in enumerate(self.instructions):
            lines.append(f"{index}: {instruction}")

        return "\n".join(lines)


# ==========================================
# IR Generator
# ==========================================


class IRGenerator:

    def __init__(self):
        self.instructions = []

    # --------------------------------------
    # Generate IR
    # --------------------------------------

    def generate(self, program):

        self.instructions = []

        if not isinstance(program, Program):
            raise TypeError("IR Generator expected a Program AST.")

        for statement in program.statements:
            self.visit(statement)

        return IRProgram(self.instructions)

    # --------------------------------------
    # Visit AST node
    # --------------------------------------

    def visit(self, node):

        if isinstance(node, MoveCommand):

            self.instructions.append(
                IRInstruction(opcode="MOVE", operand=node.distance)
            )

        elif isinstance(node, TurnCommand):

            self.instructions.append(
                IRInstruction(opcode="TURN", operand=node.direction)
            )

        else:

            raise TypeError(f"Unsupported AST node: " f"{type(node).__name__}")


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.semantic import SemanticAnalyzer

    source = """
    START

    MOVE 100
    TURN RIGHT
    MOVE 50
    TURN LEFT
    MOVE 30

    STOP
    """

    try:

        # ----------------------------------
        # Lexer
        # ----------------------------------

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        print("✓ Lexical Analysis Successful")

        # ----------------------------------
        # Parser
        # ----------------------------------

        parser = Parser(tokens)
        program = parser.parse()

        print("✓ Syntax Analysis Successful")

        # ----------------------------------
        # Semantic Analysis
        # ----------------------------------

        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)

        print("✓ Semantic Analysis Successful")

        # ----------------------------------
        # IR Generation
        # ----------------------------------

        generator = IRGenerator()
        ir_program = generator.generate(program)

        print("✓ IR Generation Successful")
        print()
        print("Generated Intermediate Representation:")
        print("--------------------------------------")
        print(ir_program)

    except Exception as error:

        print(f"❌ {error}")
