import sys

keywords = {
    "class": "CLASS", "public": "PUBLIC", "static": "STATIC", "void": "VOID",
    "main": "MAIN", "int": "INT", "float": "FLOAT", "boolean": "BOOLEAN_TYPE",
    "char": "CHAR", "String": "STRING_TYPE", "if": "IF", "else": "ELSE",
    "while": "WHILE", "for": "FOR", "return": "RETURN"
}

operators = {
    "==": "LOGOP", "!=": "LOGOP", "<=": "LOGOP", ">=": "LOGOP",
    "<": "LOGOP", ">": "LOGOP", "=": "ASSIGN",
    "+": "MATHOP", "-": "MATHOP", "*": "MATHOP", "/": "MATHOP", "%": "MATHOP"
}

delimiters = {
    "(": "LPAR", ")": "RPAR", "{": "LCUR", "}": "RCUR", "[": "LSQU", "]": "RSQU",
    ";": "SEMICOLON", ",": "COMMA", ".": "DOT"
}

source = open(sys.argv[1]).read()
tokens = []
symbols = []
symbol_names = set()
errors = []
pos = 0
line = 1
column = 1

def advance(count=1):
    global pos, line, column
    for _ in range(count):
        if source[pos] == "\n":
            line += 1
            column = 1
        else:
            column += 1
        pos += 1

while pos < len(source):
    character = source[pos]

    if character == " " or character == "\t" or character == "\r" or character == "\n":
        advance()
        continue

    start_line = line
    start_column = column

    if character == "/" and pos + 1 < len(source) and source[pos + 1] == "/":
        advance(2)
        while pos < len(source) and source[pos] != "\n":
            advance()
        continue

    if character == "/" and pos + 1 < len(source) and source[pos + 1] == "*":
        advance(2)
        closed = False
        while pos < len(source):
            if source[pos] == "*" and pos + 1 < len(source) and source[pos + 1] == "/":
                advance(2)
                closed = True
                break
            advance()
        if not closed:
            errors.append("Error: unclosed comment starting at line " + str(start_line) + ", column " + str(start_column) + ".")
        continue

    if character == "\"" or character == "'":
        quote = character
        begin = pos
        advance()
        closed = False
        while pos < len(source):
            if source[pos] == quote:
                advance()
                closed = True
                break
            if source[pos] == "\n":
                advance()
                break
            advance()
        if closed:
            tokens.append((source[begin:pos], "STRING"))
        else:
            errors.append("Error: unclosed string literal starting at line " + str(start_line) + ", column " + str(start_column) + ".")
        continue

    if ("a" <= character <= "z") or ("A" <= character <= "Z") or character == "_":
        begin = pos
        while pos < len(source):
            current = source[pos]
            if not (("a" <= current <= "z") or ("A" <= current <= "Z") or ("0" <= current <= "9") or current == "_"):
                break
            advance()
        lexeme = source[begin:pos]
        token = keywords.get(lexeme, "BOOLEAN" if lexeme == "true" or lexeme == "false" else "IDENTIFIER")
        tokens.append((lexeme, token))
        if token == "IDENTIFIER" and lexeme not in symbol_names:
            symbol_names.add(lexeme)
            symbols.append((lexeme, start_line, start_column))
        continue

    if "0" <= character <= "9":
        begin = pos
        while pos < len(source) and "0" <= source[pos] <= "9":
            advance()
        if pos < len(source) and (("a" <= source[pos] <= "z") or ("A" <= source[pos] <= "Z") or source[pos] == "_"):
            while pos < len(source):
                current = source[pos]
                if not (("a" <= current <= "z") or ("A" <= current <= "Z") or ("0" <= current <= "9") or current == "_"):
                    break
                advance()
            errors.append("Error: invalid identifier '" + source[begin:pos] + "' at line " + str(start_line) + ", column " + str(start_column) + ".")
            continue
        if pos < len(source) and source[pos] == "." and pos + 1 < len(source) and "0" <= source[pos + 1] <= "9":
            advance()
            while pos < len(source) and "0" <= source[pos] <= "9":
                advance()
        tokens.append((source[begin:pos], "NUMBER"))
        continue

    if pos + 1 < len(source) and source[pos:pos + 2] in operators:
        tokens.append((source[pos:pos + 2], operators[source[pos:pos + 2]]))
        advance(2)
        continue

    if character in operators:
        tokens.append((character, operators[character]))
        advance()
        continue

    if character in delimiters:
        tokens.append((character, delimiters[character]))
        advance()
        continue

    errors.append("Error: invalid character '" + character + "' at line " + str(line) + ", column " + str(column) + ".")
    advance()

for lexeme, token in tokens:
    print("Lexeme: " + lexeme + ", Token: " + token)

print("Symbol Table:")
for name, symbol_line, symbol_column in symbols:
    print(name + " at line " + str(symbol_line) + ", column " + str(symbol_column))

print("Lexical Errors:")
for error in errors:
    print(error)
