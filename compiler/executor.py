from compiler.ir import IRProgram


class RobotState:

    def __init__(self):
        self.x = 0
        self.y = 0

        # Robot initially faces NORTH
        self.direction = "NORTH"

        # Store every position for the simulator later
        self.path = [(self.x, self.y)]

    def __str__(self):
        return f"Position: ({self.x}, {self.y})\n" f"Direction: {self.direction}"


class RobotExecutor:

    def __init__(self):
        self.robot = RobotState()

    # --------------------------------------
    # Execute IR program
    # --------------------------------------

    def execute(self, ir_program):

        if not isinstance(ir_program, IRProgram):
            raise TypeError("Executor expected an IRProgram.")

        for instruction in ir_program.instructions:

            if instruction.opcode == "MOVE":
                self.execute_move(instruction.operand)

            elif instruction.opcode == "TURN":
                self.execute_turn(instruction.operand)

            else:
                raise RuntimeError(f"Unknown instruction: " f"{instruction.opcode}")

        return self.robot

    # --------------------------------------
    # MOVE
    # --------------------------------------

    def execute_move(self, distance):

        if self.robot.direction == "NORTH":
            self.robot.y += distance

        elif self.robot.direction == "EAST":
            self.robot.x += distance

        elif self.robot.direction == "SOUTH":
            self.robot.y -= distance

        elif self.robot.direction == "WEST":
            self.robot.x -= distance

        self.robot.path.append((self.robot.x, self.robot.y))

    # --------------------------------------
    # TURN
    # --------------------------------------

    def execute_turn(self, direction):

        directions = ["NORTH", "EAST", "SOUTH", "WEST"]

        current_index = directions.index(self.robot.direction)

        if direction == "RIGHT":

            new_index = (current_index + 1) % 4

        elif direction == "LEFT":

            new_index = (current_index - 1) % 4

        else:

            raise RuntimeError(f"Invalid turn direction: {direction}")

        self.robot.direction = directions[new_index]


# ==========================================
# Complete Compiler + Executor Test
# ==========================================

if __name__ == "__main__":

    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.semantic import SemanticAnalyzer
    from compiler.ir import IRGenerator

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
        # 1. LEXER
        # ----------------------------------

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        print("✓ Lexical Analysis Successful")

        # ----------------------------------
        # 2. PARSER
        # ----------------------------------

        parser = Parser(tokens)
        program = parser.parse()

        print("✓ Syntax Analysis Successful")

        # ----------------------------------
        # 3. SEMANTIC ANALYSIS
        # ----------------------------------

        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)

        print("✓ Semantic Analysis Successful")

        # ----------------------------------
        # 4. IR GENERATION
        # ----------------------------------

        generator = IRGenerator()
        ir_program = generator.generate(program)

        print("✓ IR Generation Successful")

        print("\nIntermediate Representation:")
        print("----------------------------")
        print(ir_program)

        # ----------------------------------
        # 5. EXECUTION
        # ----------------------------------

        executor = RobotExecutor()
        robot = executor.execute(ir_program)

        print("\n✓ Execution Successful")

        print("\nFinal Robot State:")
        print("------------------")
        print(robot)

        print("\nRobot Path:")
        print("-----------")

        for index, position in enumerate(robot.path):
            print(f"Step {index}: {position}")

    except Exception as error:

        print(f"\n❌ Error: {error}")
