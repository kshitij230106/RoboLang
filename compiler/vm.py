from compiler.codegen import BytecodeProgram, OP_MOVE, OP_TURN, DIR_LEFT, DIR_RIGHT

# ==========================================
# Robot State
# ==========================================


class RobotState:

    def __init__(self):

        # Starting position
        self.x = 0
        self.y = 0

        # Starting direction
        self.direction = "NORTH"

        # Complete movement history
        self.path = [(self.x, self.y)]

    def __str__(self):

        return f"Position: ({self.x}, {self.y})\n" f"Direction: {self.direction}"


# ==========================================
# RoboLang Virtual Machine
# ==========================================


class RoboLangVM:

    def __init__(self):

        self.robot = RobotState()

        # Program Counter
        self.pc = 0

        # Execution status
        self.running = False

    # --------------------------------------
    # Run bytecode
    # --------------------------------------

    def run(self, bytecode):

        if not isinstance(bytecode, BytecodeProgram):
            raise TypeError("VM expected a BytecodeProgram.")

        self.pc = 0
        self.running = True

        instructions = bytecode.instructions

        while self.pc < len(instructions):

            opcode = instructions[self.pc]

            # --------------------------------
            # MOVE
            # --------------------------------

            if opcode == OP_MOVE:

                distance = instructions[self.pc + 1]

                self.move(distance)

                self.pc += 2

            # --------------------------------
            # TURN
            # --------------------------------

            elif opcode == OP_TURN:

                direction = instructions[self.pc + 1]

                self.turn(direction)

                self.pc += 2

            # --------------------------------
            # Unknown opcode
            # --------------------------------

            else:

                raise RuntimeError(f"Unknown opcode {opcode} " f"at position {self.pc}")

        self.running = False

        return self.robot

    # --------------------------------------
    # Execute MOVE
    # --------------------------------------

    def move(self, distance):

        if self.robot.direction == "NORTH":

            self.robot.y += distance

        elif self.robot.direction == "EAST":

            self.robot.x += distance

        elif self.robot.direction == "SOUTH":

            self.robot.y -= distance

        elif self.robot.direction == "WEST":

            self.robot.x -= distance

        else:

            raise RuntimeError(f"Invalid robot direction: " f"{self.robot.direction}")

        # Save new position
        self.robot.path.append((self.robot.x, self.robot.y))

    # --------------------------------------
    # Execute TURN
    # --------------------------------------

    def turn(self, direction):

        directions = ["NORTH", "EAST", "SOUTH", "WEST"]

        current_index = directions.index(self.robot.direction)

        if direction == DIR_RIGHT:

            new_index = (current_index + 1) % 4

        elif direction == DIR_LEFT:

            new_index = (current_index - 1) % 4

        else:

            raise RuntimeError(f"Invalid turn code: {direction}")

        self.robot.direction = directions[new_index]


# ==========================================
# Test Complete Pipeline
# ==========================================

if __name__ == "__main__":

    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.semantic import SemanticAnalyzer
    from compiler.ir import IRGenerator
    from compiler.codegen import CodeGenerator

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

        # ==============================
        # 1. LEXER
        # ==============================

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        print("✓ Lexical Analysis")

        # ==============================
        # 2. PARSER
        # ==============================

        parser = Parser(tokens)
        program = parser.parse()

        print("✓ Syntax Analysis")

        # ==============================
        # 3. SEMANTIC ANALYSIS
        # ==============================

        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)

        print("✓ Semantic Analysis")

        # ==============================
        # 4. IR GENERATION
        # ==============================

        ir_generator = IRGenerator()
        ir_program = ir_generator.generate(program)

        print("✓ IR Generation")

        # ==============================
        # 5. CODE GENERATION
        # ==============================

        code_generator = CodeGenerator()
        bytecode = code_generator.generate(ir_program)

        print("✓ Code Generation")

        print("\nBytecode:")
        print("--------------------------------")
        print(bytecode)

        # ==============================
        # 6. VIRTUAL MACHINE
        # ==============================

        vm = RoboLangVM()

        robot = vm.run(bytecode)

        print("\n✓ Virtual Machine Execution")

        # ==============================
        # FINAL STATE
        # ==============================

        print("\nFinal Robot State:")
        print("--------------------------------")

        print(robot)

        print("\nRobot Path:")
        print("--------------------------------")

        for step, position in enumerate(robot.path):

            print(f"Step {step}: {position}")

    except Exception as error:

        print(f"\n❌ Error: {error}")
