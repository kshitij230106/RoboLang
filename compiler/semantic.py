from compiler.ast import Program, MoveCommand, TurnCommand

# ==========================================
# Semantic Error
# ==========================================


class SemanticError(Exception):
    """
    Raised when semantic errors are found
    in a RoboLang program.
    """

    def __init__(self, errors):

        self.errors = errors

        message = "\n".join(
            f"Line {error['line']}: {error['message']}" for error in errors
        )

        super().__init__(message)


# ==========================================
# Semantic Analyzer
# ==========================================


class SemanticAnalyzer:

    def __init__(self):

        self.errors = []

    # ==========================================
    # Analyze Program
    # ==========================================

    def analyze(self, program):

        # Clear previous errors
        self.errors = []

        # --------------------------------------
        # Check Program AST
        # --------------------------------------

        if not isinstance(program, Program):

            self.errors.append(
                {
                    "line": 1,
                    "message": "Program must be a valid RoboLang AST.",
                    "type": "semantic",
                }
            )

            raise SemanticError(self.errors)

        # --------------------------------------
        # Check Empty Program
        # --------------------------------------

        if len(program.statements) == 0:

            self.errors.append(
                {"line": 1, "message": "Program cannot be empty.", "type": "semantic"}
            )

        # --------------------------------------
        # Visit Every Statement
        # --------------------------------------

        for statement in program.statements:

            self.visit(statement)

        # --------------------------------------
        # Raise Errors
        # --------------------------------------

        if self.errors:

            raise SemanticError(self.errors)

        return True

    # ==========================================
    # Visit AST Node
    # ==========================================

    def visit(self, node):

        if isinstance(node, MoveCommand):

            self.visit_move(node)

        elif isinstance(node, TurnCommand):

            self.visit_turn(node)

        else:

            line = getattr(node, "line", 1)

            self.errors.append(
                {
                    "line": line,
                    "message": (f"Unknown AST node: " f"{type(node).__name__}"),
                    "type": "semantic",
                }
            )

    # ==========================================
    # Validate MOVE
    # ==========================================

    def visit_move(self, node):

        # Distance must be numeric
        if not isinstance(node.distance, (int, float)):

            self.errors.append(
                {
                    "line": node.line,
                    "message": "MOVE distance must be a number.",
                    "type": "semantic",
                }
            )

            return

        # Distance must be greater than zero
        if node.distance <= 0:

            self.errors.append(
                {
                    "line": node.line,
                    "message": (
                        "MOVE distance must be greater than 0. "
                        f"Found: {node.distance}"
                    ),
                    "type": "semantic",
                }
            )

    # ==========================================
    # Validate TURN
    # ==========================================

    def visit_turn(self, node):

        valid_directions = ["LEFT", "RIGHT"]

        if node.direction not in valid_directions:

            self.errors.append(
                {
                    "line": node.line,
                    "message": (
                        f"Invalid turn direction "
                        f"'{node.direction}'. "
                        "Expected LEFT or RIGHT."
                    ),
                    "type": "semantic",
                }
            )


# ==========================================
# Test Semantic Analyzer
# ==========================================

if __name__ == "__main__":

    from compiler.lexer import Lexer
    from compiler.parser import Parser

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

        # --------------------------------------
        # Lexer
        # --------------------------------------

        lexer = Lexer(source)

        tokens = lexer.tokenize()

        print("✓ Lexical Analysis Successful")

        # --------------------------------------
        # Parser
        # --------------------------------------

        parser = Parser(tokens)

        program = parser.parse()

        print("✓ Syntax Analysis Successful")

        # --------------------------------------
        # Semantic Analysis
        # --------------------------------------

        analyzer = SemanticAnalyzer()

        analyzer.analyze(program)

        print("✓ Semantic Analysis Successful")

        print()
        print("🎉 Program is semantically valid!")

    except SemanticError as error:

        print()
        print("❌ Semantic Error")

        for item in error.errors:

            print(f"Line {item['line']}: " f"{item['message']}")

    except SyntaxError as error:

        print()
        print(f"❌ Syntax Error: {error}")
