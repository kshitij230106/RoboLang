from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer, SemanticError
from compiler.ir import IRGenerator
from compiler.codegen import CodeGenerator
from compiler.vm import RoboLangVM

# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(title="RoboLang Compiler Backend")


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Request Model
# ==========================================


class SourceProgram(BaseModel):
    source: str


# ==========================================
# Root
# ==========================================


@app.get("/")
def root():

    return {"message": "RoboLang Compiler Backend is running"}


# ==========================================
# Compiler Status
# ==========================================


@app.get("/compiler/status")
def compiler_status():

    return {
        "compiler": "RoboLang",
        "status": "ready",
        "pipeline": [
            "Lexer",
            "Parser",
            "AST",
            "Semantic Analysis",
            "IR Generation",
            "Code Generation",
            "Virtual Machine",
        ],
    }


# ==========================================
# Execute RoboLang Program
# ==========================================


@app.post("/execute")
def execute(program: SourceProgram):

    source = program.source

    # ======================================
    # 1. LEXICAL ANALYSIS
    # ======================================

    try:

        lexer = Lexer(source)

        tokens = lexer.tokenize()

    except Exception as error:

        return {
            "success": False,
            "stage": "lexer",
            "error": str(error),
            "errors": [
                {
                    "line": getattr(error, "line", 1),
                    "message": str(error),
                    "type": "lexer",
                }
            ],
        }

    # ======================================
    # 2. SYNTAX ANALYSIS
    # ======================================

    try:

        parser = Parser(tokens)

        program_ast = parser.parse()

    except SyntaxError as error:

        return {
            "success": False,
            "stage": "parser",
            "error": str(error),
            "errors": [
                {
                    "line": extract_line_number(str(error)),
                    "message": str(error),
                    "type": "syntax",
                }
            ],
            "tokens": serialize_tokens(tokens),
        }

    except Exception as error:

        return {
            "success": False,
            "stage": "parser",
            "error": str(error),
            "errors": [{"line": 1, "message": str(error), "type": "parser"}],
        }

    # ======================================
    # 3. AST
    # ======================================

    ast_string = str(program_ast)

    # ======================================
    # 4. SEMANTIC ANALYSIS
    # ======================================

    try:

        analyzer = SemanticAnalyzer()

        analyzer.analyze(program_ast)

    except SemanticError as error:

        return {
            "success": False,
            "stage": "semantic",
            "error": str(error),
            "errors": error.errors,
            "tokens": serialize_tokens(tokens),
            "ast": ast_string,
        }

    except Exception as error:

        return {
            "success": False,
            "stage": "semantic",
            "error": str(error),
            "errors": [{"line": 1, "message": str(error), "type": "semantic"}],
            "ast": ast_string,
        }

    # ======================================
    # 5. IR GENERATION
    # ======================================

    try:

        ir_generator = IRGenerator()

        ir_program = ir_generator.generate(program_ast)

        ir_string = str(ir_program)

    except Exception as error:

        return {
            "success": False,
            "stage": "ir",
            "error": str(error),
            "errors": [{"line": 1, "message": str(error), "type": "ir"}],
            "ast": ast_string,
        }

    # ======================================
    # 6. CODE GENERATION
    # ======================================

    try:

        code_generator = CodeGenerator()

        bytecode = code_generator.generate(ir_program)

    except Exception as error:

        return {
            "success": False,
            "stage": "codegen",
            "error": str(error),
            "errors": [{"line": 1, "message": str(error), "type": "codegen"}],
            "ir": ir_string,
        }

    # ======================================
    # 7. VIRTUAL MACHINE
    # ======================================

    try:

        # Your VM expects a BytecodeProgram
        vm = RoboLangVM()

        robot = vm.run(bytecode)

    except Exception as error:

        return {
            "success": False,
            "stage": "vm",
            "error": str(error),
            "errors": [{"line": 1, "message": str(error), "type": "vm"}],
            "bytecode": bytecode.instructions,
        }

    # ======================================
    # SUCCESS
    # ======================================

    return {
        "success": True,
        "stages": {
            "lexer": "success",
            "parser": "success",
            "ast": "success",
            "semantic": "success",
            "ir": "success",
            "codegen": "success",
            "vm": "success",
        },
        "tokens": serialize_tokens(tokens),
        "ast": ast_string,
        "ir": ir_string,
        "bytecode": bytecode.instructions,
        "robot": serialize_robot_state(robot),
    }


# ==========================================
# Serialize Tokens
# ==========================================


def serialize_tokens(tokens):

    result = []

    for token in tokens:

        result.append({"type": token.type, "value": token.value, "line": token.line})

    return result


# ==========================================
# Serialize Robot State
# ==========================================


def serialize_robot_state(robot):

    return {
        "x": robot.x,
        "y": robot.y,
        "direction": robot.direction,
        "path": [{"x": position[0], "y": position[1]} for position in robot.path],
    }


# ==========================================
# Extract Line Number
# ==========================================


def extract_line_number(message):

    import re

    match = re.search(r"line\s+(\d+)", message, re.IGNORECASE)

    if match:

        return int(match.group(1))

    return 1
