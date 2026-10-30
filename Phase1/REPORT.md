# Mini Java Compiler — Phase 01: Lexical Analyzer

**Course:** CSCI415 Compiler Design — Fall 2026
**Phase:** 01 — Lexical Analysis
**Language used:** Python 3 (standard library only — `sys` for the file path, nothing else)

**Team members:**

| Name | ID 
|Rana Hany Mohamed|231001595
|Alaa Husein Mahmoud|231001493
|Mariam Hesham |231000 
|Sara Qandil |24100 

---

## 1. Overview

The scanner is hand-written and reads the source file character by character. No regular
expressions, no lexer generators, and no ready-made tokenizing functions are used — only string
indexing and character comparisons.

The source file is read once into a single string and walked with one index, `pos`. A helper
function, `advance()`, is the only place that moves that index, and it updates the line and column
counters at the same time: a newline increments the line and resets the column to 1, any other
character increments the column. Because every character in the file passes through this one
function, reported positions cannot drift out of sync with the source.

The main loop looks at the current character and dispatches to the matching case: whitespace,
comment, string literal, identifier or keyword, number, operator, delimiter — and if nothing
matches, the character is recorded as a lexical error. Each case saves `start_line` and
`start_column` before it consumes anything, so every token and every error reports the position
where its lexeme *began*, not where the scanner happened to stop.

The phase produces the three outputs Phase 02 will need: a **token stream**, a **symbol table**,
and a **list of lexical errors**.

**How to run:** `python lexer.py test_input.txt`

---

## 2. Tokens Implemented

**Keywords (15).** Held in a dictionary and matched by exact string lookup *after* a complete word
has been read, so `classRoom` is one identifier rather than `class` followed by `Room`. Because the
lookup is an exact string comparison, case sensitivity is automatic: `class` → `CLASS`, while
`Class` is not found in the dictionary and falls through to `IDENTIFIER`.

| Lexeme | Token | Lexeme | Token |
|---|---|---|---|
| `class` | CLASS | `char` | CHAR |
| `public` | PUBLIC | `String` | STRING_TYPE |
| `static` | STATIC | `if` | IF |
| `void` | VOID | `else` | ELSE |
| `main` | MAIN | `while` | WHILE |
| `int` | INT | `for` | FOR |
| `float` | FLOAT | `return` | RETURN |
| `boolean` | BOOLEAN_TYPE | | |

**Identifiers** → `IDENTIFIER`. A word starting with a letter or `_`, continuing with letters,
digits or `_`.

**Literals.** `NUMBER` for integers and floats (`20`, `85.5`); `STRING` for text in single or
double quotes (`"Ali"`, `'A'`); `BOOLEAN` for `true` and `false`.

**Operators.** `MATHOP` for `+ - * / %`; `LOGOP` for `== != < > <= >=`; `ASSIGN` for `=`.

**Delimiters.** `( LPAR`, `) RPAR`, `{ LCUR`, `} RCUR`, `[ LSQU`, `] RSQU`, `; SEMICOLON`,
`, COMMA`, `. DOT`

**Skipped entirely.** Whitespace, `//` line comments, and `/* … */` block comments produce no
token at all.

**Symbol table.** Each time an `IDENTIFIER` is produced, its name and the line and column of its
first appearance are recorded. A parallel `set` of names already seen prevents duplicates, so a
variable used ten times appears once. Keywords and literals are deliberately excluded — they are
not user-defined names. In Phase 03 the same structure will be extended with type and scope
fields for semantic checking.

---

## 3. Error Handling

Errors never halt the scan. Each one is appended to an error list, the offending text is skipped,
and tokenizing continues — so a single run reports every problem in the file instead of only the
first. All four required error classes are detected, each with its line, column and a descriptive
message:

| Error | Example | Message produced |
|---|---|---|
| Invalid character | `int x = 10 @ 5;` | `Error: invalid character '@' at line 1, column 12.` |
| Invalid identifier | `1name = 5;` | `Error: invalid identifier '1name' at line 1, column 1.` |
| Unclosed string | `String name = "Ali;` | `Error: unclosed string literal starting at line 1, column 15.` |
| Unterminated comment | `/* This comment does not end` | `Error: unclosed comment starting at line 1, column 1.` |

Two details in the recovery are worth noting. For an invalid identifier, the **whole** bad lexeme
is consumed before the error is recorded — stopping after the digits would leave `name` behind to
be scanned as a perfectly valid identifier and would hide the real problem. For an unclosed
string, a newline is treated as a hard stop: without it, a missing closing quote would swallow the
rest of the file, and every following line would go unchecked.

---

## 4. Testing

The scanner was tested on a single input file combining a valid Mini Java program with a block of
deliberate error cases. The valid portion produced the expected token stream, including
`String` → `STRING_TYPE` while `"Ali"` → `STRING`, and `>=` as one `LOGOP` rather than two
tokens. The checks that follow it confirmed that `true` → `BOOLEAN`, `'A'` → `STRING`,
`Class` → `IDENTIFIER` (case sensitivity), and that a closed block comment produced no tokens.

The four error lines at the end produced exactly four errors, at the correct positions:

```
Error: invalid character '@' at line 17, column 12.
Error: invalid identifier '1name' at line 18, column 1.
Error: unclosed string literal starting at line 19, column 17.
Error: unclosed comment starting at line 20, column 1.
```

The symbol table listed ten identifiers, each once, with the line and column of its first use —
and contained no keywords and no literals.

---

## 5. Challenges Faced and How They Were Solved

**Telling a comment from a division operator.** `/` is a valid arithmetic operator, so the first
character alone is not enough to decide. Solved with a one-character lookahead: the main loop
tests for `//` and `/*` *before* it ever reaches the operator table, so a comment is always
recognised first and a lone `/` still becomes `MATHOP`.

**Two-character operators.** Reading one character at a time, `>=` would naturally come out as
`>` then `=`. Solved with maximal munch: the scanner builds the two-character string first and
looks it up, and only falls back to a single character if that lookup fails. This is what keeps
`>=` and `==` as single `LOGOP` tokens instead of splitting `==` into two `ASSIGN`s.

**Invalid identifiers versus valid numbers.** `20` is a `NUMBER` but `1name` is an error, and both
start with a digit. Solved by scanning the digit run first, then inspecting the character that
follows: a letter or `_` means the whole run is an invalid identifier; anything else means a
legal number.

**Floats versus the DOT delimiter.** A `.` can belong to a number (`85.5`) or be a delimiter
(`s.length`). Solved by extending a number across a dot only when the dot is followed by at least
one digit; otherwise the dot is left to be scanned as `DOT`.

**Keeping line and column accurate.** Updating the counters at each scanning site would have meant
many chances to forget one. Solved by routing every position change through the single `advance()`
function, which makes correct tracking structural rather than something to remember.

**Case sensitivity.** Comparing keywords case-insensitively would have made `Class` a keyword.
Using exact string lookup keeps `Class`, `INT` and `If` as ordinary identifiers, as required.

**Non-ASCII characters.** Python's built-in `isalpha()` accepts Arabic and other Unicode letters,
which would have allowed a non-ASCII identifier to pass as valid. Explicit range checks
(`"a" <= c <= "z"`) were used instead, so any non-ASCII character is correctly reported as invalid.

---

## 6. Known Limitations and Notes for Phase 02

Lexically valid does not mean syntactically valid — the scanner judges one lexeme at a time.
`int total-marks = 7;` yields a perfectly legal token stream (`INT`, `IDENTIFIER`, `MATHOP`,
`IDENTIFIER`, `ASSIGN`, `NUMBER`, `SEMICOLON`); rejecting it is the parser's job in Phase 02.
Unbalanced braces are likewise outside the scanner's scope.

Two cases fall outside the Phase 01 specification and are handled accordingly. A number with a
second decimal point (`1.2.3`) is not flagged as an error; it scans as `1.2`, `DOT`, `3` and will
be rejected by the parser. A lone `!` is reported as an invalid character, since the specification
lists `!=` but not `!` on its own as an operator.

The token stream already carries no positional data into Phase 02 in its printed form, but the
line and column are tracked during scanning and can be attached to each token with a one-line
change when the parser needs them for error messages.
