import sys  # Provides access to the command-line source-file path.

# Maps reserved words to their token names.
keywords = {
    "class": "CLASS", "public": "PUBLIC", "static": "STATIC", "void": "VOID",
    "main": "MAIN", "int": "INT", "float": "FLOAT", "boolean": "BOOLEAN_TYPE",
    "char": "CHAR", "String": "STRING_TYPE", "if": "IF", "else": "ELSE",
    "while": "WHILE", "for": "FOR", "return": "RETURN"
}

# Maps operators to their token names, including two-character operators.
operators = {
    "==": "LOGOP", "!=": "LOGOP", "<=": "LOGOP", ">=": "LOGOP",
    "<": "LOGOP", ">": "LOGOP", "=": "ASSIGN",
    "+": "MATHOP", "-": "MATHOP", "*": "MATHOP", "/": "MATHOP", "%": "MATHOP"
}

# Maps punctuation characters to their delimiter token names.
delimiters = {
    "(": "LPAR", ")": "RPAR", "{": "LCUR", "}": "RCUR", "[": "LSQU", "]": "RSQU",
    ";": "SEMICOLON", ",": "COMMA", ".": "DOT"
}

source = open(sys.argv[1]).read()  # Reads the complete source file.
tokens = []  # Stores recognized lexemes and token names in order.
symbols = []  # Stores each identifier's first location.
symbol_names = set()  # Prevents duplicate symbol-table entries.
errors = []  # Stores lexical errors without stopping the scan.
pos = 0  # Points to the next source character.
line = 1  # Tracks the current 1-based line number.
column = 1  # Tracks the current 1-based column number.

# Advances through source text and updates line and column consistently.
def advance(count=1):
    global pos, line, column
    for _ in range(count):
        if source[pos] == "\n":
            line += 1
            column = 1
        else:
            column += 1
        pos += 1

# Scans until the end of the source file.
while pos < len(source):
    character = source[pos]  # Reads the character at the current position.

    # Skips whitespace and updates position information.
    if character == " " or character == "\t" or character == "\r" or character == "\n":
        advance()
        continue

    start_line = line  # Saves the lexeme's starting line.
    start_column = column  # Saves the lexeme's starting column.

    # Skips a line comment before treating slash as an operator.
    if character == "/" and pos + 1 < len(source) and source[pos + 1] == "/":
        advance(2)
        while pos < len(source) and source[pos] != "\n":
            advance()
        continue

    # Skips a block comment and reports it if it reaches end of file.
    if character == "/" and pos + 1 < len(source) and source[pos + 1] == "*":
        advance(2)
        closed = False  # Records whether the closing comment marker was found.
        while pos < len(source):
            if source[pos] == "*" and pos + 1 < len(source) and source[pos + 1] == "/":
                advance(2)
                closed = True
                break
            advance()
        if not closed:
            errors.append("Error: unclosed comment starting at line " + str(start_line) + ", column " + str(start_column) + ".")
        continue

    # Scans a single-quoted or double-quoted string literal.
    if character == "\"" or character == "'":
        quote = character  # Remembers which quote must close the string.
        begin = pos  # Saves the opening quote position for the lexeme.
        advance()
        closed = False  # Records whether a matching closing quote was found.
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

    # Scans identifiers, keywords, and boolean literals.
    if ("a" <= character <= "z") or ("A" <= character <= "Z") or character == "_":
        begin = pos  # Saves the first character of the word.
        while pos < len(source):
            current = source[pos]
            if not (("a" <= current <= "z") or ("A" <= current <= "Z") or ("0" <= current <= "9") or current == "_"):
                break
            advance()
        lexeme = source[begin:pos]  # Extracts the complete word.
        token = keywords.get(lexeme, "BOOLEAN" if lexeme == "true" or lexeme == "false" else "IDENTIFIER")  # Selects its token type.
        tokens.append((lexeme, token))
        # Records only the first occurrence of an identifier.
        if token == "IDENTIFIER" and lexeme not in symbol_names:
            symbol_names.add(lexeme)
            symbols.append((lexeme, start_line, start_column))
        continue

    # Scans integer and decimal number literals.
    if "0" <= character <= "9":
        begin = pos  # Saves the first digit.
        while pos < len(source) and "0" <= source[pos] <= "9":
            advance()
        # Rejects a digit run immediately followed by identifier characters.
        if pos < len(source) and (("a" <= source[pos] <= "z") or ("A" <= source[pos] <= "Z") or source[pos] == "_"):
            while pos < len(source):
                current = source[pos]
                if not (("a" <= current <= "z") or ("A" <= current <= "Z") or ("0" <= current <= "9") or current == "_"):
                    break
                advance()
            errors.append("Error: invalid identifier '" + source[begin:pos] + "' at line " + str(start_line) + ", column " + str(start_column) + ".")
            continue
        # Extends the number when a dot is followed by at least one digit.
        if pos < len(source) and source[pos] == "." and pos + 1 < len(source) and "0" <= source[pos + 1] <= "9":
            advance()
            while pos < len(source) and "0" <= source[pos] <= "9":
                advance()
        tokens.append((source[begin:pos], "NUMBER"))
        continue

    # Matches two-character operators before one-character operators.
    if pos + 1 < len(source) and source[pos:pos + 2] in operators:
        tokens.append((source[pos:pos + 2], operators[source[pos:pos + 2]]))
        advance(2)
        continue

    # Matches a one-character operator.
    if character in operators:
        tokens.append((character, operators[character]))
        advance()
        continue

    # Matches a delimiter.
    if character in delimiters:
        tokens.append((character, delimiters[character]))
        advance()
        continue

    # Records an invalid character and continues scanning.
    errors.append("Error: invalid character '" + character + "' at line " + str(line) + ", column " + str(column) + ".")
    advance()

# Prints the token stream in the required format.
for lexeme, token in tokens:
    print("Lexeme: " + lexeme + ", Token: " + token)

# Prints the first location of every identifier.
print("Symbol Table:")
for name, symbol_line, symbol_column in symbols:
    print(name + " at line " + str(symbol_line) + ", column " + str(symbol_column))

# Prints every recorded lexical error after scanning is complete.
print("Lexical Errors:")
for error in errors:
    print(error)
