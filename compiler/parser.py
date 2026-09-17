from compiler.lexer import Lexer
from compiler.ast import Program, MoveCommand, TurnCommand


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    # ==========================================
    # Current Token
    # ==========================================

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]

        return None

    # ==========================================
    # Consume Token
    # ==========================================

    def consume(self, expected_type):

        token = self.current()

        if token is None:
            raise SyntaxError(
                f"Expected {expected_type}, " f"but reached end of program"
            )

        if token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type} "
                f"at line {token.line}, "
                f"but found {token.type}"
            )

        self.position += 1

        return token

    # ==========================================
    # Parse Program
    # ==========================================

    def parse(self):

        # START
        self.consume("START")

        # Statements
        statements = self.parse_statements()

        # STOP
        self.consume("STOP")

        # Anything after STOP is an error
        if self.current() is not None:

            token = self.current()

            raise SyntaxError(
                f"Unexpected token '{token.value}' " f"at line {token.line}"
            )

        return Program(statements)

    # ==========================================
    # Parse Statements
    # ==========================================

    def parse_statements(self):

        statements = []

        while self.current() is not None:

            # STOP marks the end of the program
            if self.current().type == "STOP":
                break

            statements.append(self.parse_statement())

        return statements

    # ==========================================
    # Parse Single Statement
    # ==========================================

    def parse_statement(self):

        token = self.current()

        if token.type == "MOVE":

            return self.parse_move()

        elif token.type == "TURN":

            return self.parse_turn()

        else:

            raise SyntaxError(
                f"Unexpected token '{token.value}' " f"at line {token.line}"
            )

    # ==========================================
    # Parse MOVE
    # ==========================================

    def parse_move(self):

        # Save MOVE token so we know its line
        move_token = self.consume("MOVE")

        # MOVE must be followed by NUMBER
        distance = self.consume("NUMBER")

        return MoveCommand(distance=distance.value, line=move_token.line)

    # ==========================================
    # Parse TURN
    # ==========================================

    def parse_turn(self):

        # Save TURN token so we know its line
        turn_token = self.consume("TURN")

        token = self.current()

        # TURN must have a direction
        if token is None:

            raise SyntaxError(
                f"Expected LEFT or RIGHT " f"after TURN at line {turn_token.line}"
            )

        # Only LEFT and RIGHT are valid
        if token.type not in ["LEFT", "RIGHT"]:

            raise SyntaxError(
                f"Expected LEFT or RIGHT "
                f"at line {token.line}, "
                f"but found {token.value}"
            )

        self.position += 1

        return TurnCommand(direction=token.value, line=turn_token.line)


# ==========================================
# Test Parser
# ==========================================

if __name__ == "__main__":

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
        # Print AST
        # --------------------------------------

        print()
        print("AST:")
        print("--------------------------------------")

        for statement in program.statements:

            print(statement)

    except SyntaxError as error:

        print()
        print(f"❌ Syntax Error: {error}")
