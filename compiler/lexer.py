from dataclasses import dataclass

# -----------------------------------
# Token
# -----------------------------------


@dataclass
class Token:
    type: str
    value: object
    line: int


# -----------------------------------
# Lexer
# -----------------------------------


class Lexer:

    KEYWORDS = {
        "START": "START",
        "STOP": "STOP",
        "MOVE": "MOVE",
        "TURN": "TURN",
        "LEFT": "LEFT",
        "RIGHT": "RIGHT",
    }

    def __init__(self, source):
        self.source = source
        self.tokens = []

    def tokenize(self):

        lines = self.source.splitlines()

        for line_number, line in enumerate(lines, start=1):

            words = line.strip().split()

            for word in words:

                # Keyword
                if word.upper() in self.KEYWORDS:

                    token_type = self.KEYWORDS[word.upper()]

                    self.tokens.append(Token(token_type, word.upper(), line_number))

                # Number
                elif word.isdigit():

                    self.tokens.append(Token("NUMBER", int(word), line_number))

                # Unknown word
                else:

                    raise SyntaxError(
                        f"Unknown token '{word}' " f"at line {line_number}"
                    )

        return self.tokens


# -----------------------------------
# Test
# -----------------------------------

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

    lexer = Lexer(source)

    tokens = lexer.tokenize()

    for token in tokens:
        print(token)
