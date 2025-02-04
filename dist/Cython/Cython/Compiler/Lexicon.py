#
#   Pyrex Scanner - Lexical Definitions
#
#   Changing anything in this file will cause Lexicon.pickle
#   to be rebuilt next time pyrexc is run.
#

string_prefixes = "cCrRuU"

def make_lexicon():
    from Cython.Plex import \
        Str, Any, AnyBut, AnyChar, Rep, Rep1, Opt, Bol, Eol, Eof, \
        TEXT, IGNORE, State, Lexicon
    from Scanning import Method

    letter = Any("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_")
    digit = Any("0123456789")
    octdigit = Any("01234567")
    hexdigit = Any("0123456789ABCDEFabcdef")
    indentation = Bol + Rep(Any(" \t"))
    
    decimal = Rep1(digit)
    dot = Str(".")
    exponent = Any("Ee") + Opt(Any("+-")) + decimal
    decimal_fract = (decimal + dot + Opt(decimal)) | (dot + decimal)
    
    name = letter + Rep(letter | digit)
    intconst = decimal | (Str("0x") + Rep1(hexdigit))
    longconst = intconst + Str("L")
    fltconst = (decimal_fract + Opt(exponent)) | (decimal + exponent)
    imagconst = (intconst | fltconst) + Any("jJ")
    
    sq_string = (
        Str("'") + 
        Rep(AnyBut("\\\n'") | (Str("\\") + AnyChar)) + 
        Str("'")
    )
    
    dq_string = (
        Str('"') + 
        Rep(AnyBut('\\\n"') | (Str("\\") + AnyChar)) + 
        Str('"')
    )
    
    non_sq = AnyBut("'") | (Str('\\') + AnyChar)
    tsq_string = (
        Str("'''")
        + Rep(non_sq | (Str("'") + non_sq) | (Str("''") + non_sq)) 
        + Str("'''")
    )
    
    non_dq = AnyBut('"') | (Str('\\') + AnyChar)
    tdq_string = (
        Str('"""')
        + Rep(non_dq | (Str('"') + non_dq) | (Str('""') + non_dq)) 
        + Str('"""')
    )
    stringlit = Opt(Any(string_prefixes)) + (sq_string | dq_string | tsq_string| tdq_string)
    
    beginstring = Opt(Any(string_prefixes)) + (Str("'") | Str('"') | Str("'''") | Str('"""'))
    two_oct = octdigit + octdigit
    three_oct = octdigit + octdigit + octdigit
    two_hex = hexdigit + hexdigit
    four_hex = two_hex + two_hex
    escapeseq = Str("\\") + (two_oct | three_oct | two_hex |
                             Str('u') + four_hex | Str('x') + two_hex | AnyChar)
    
    bra = Any("([{")
    ket = Any(")]}")
    punct = Any(":,;+-*/|&<>=.%`~^?")
    diphthong = Str("==", "<>", "!=", "<=", ">=", "<<", ">>", "**", "+=", "-=", "*=", "/=", "%=", "|=", "^=", "&=", "//")
    spaces = Rep1(Any(" \t\f"))
    comment = Str("#") + Rep(AnyBut("\n"))
    escaped_newline = Str("\\\n")
    lineterm = Eol + Opt(Str("\n"))
    
    return Lexicon([
        (name, 'IDENT'),
        (intconst, 'INT'),
        (longconst, 'LONG'),
        (fltconst, 'FLOAT'),
        (imagconst, 'IMAG'),
        (punct | diphthong, TEXT),
        
        (bra, Method('open_bracket_action')),
        (ket, Method('close_bracket_action')),
        (lineterm, Method('newline_action')),
    
        #(stringlit, 'STRING'),
        (beginstring, Method('begin_string_action')),
        
        (comment, IGNORE),
        (spaces, IGNORE),
        (escaped_newline, IGNORE),
        
        State('INDENT', [
            (Opt(spaces) + Opt(comment) + lineterm, IGNORE),
            (indentation, Method('indentation_action')),
            (Eof, Method('eof_action'))
        ]),
        
        State('SQ_STRING', [
            (escapeseq, 'ESCAPE'),
            (Rep1(AnyBut("'\"\n\\")), 'CHARS'),
            (Str('"'), 'CHARS'),
            (Str("\n"), Method('unclosed_string_action')),
            (Str("'"), Method('end_string_action')),
            (Eof, 'EOF')
        ]),
        
        State('DQ_STRING', [
            (escapeseq, 'ESCAPE'),
            (Rep1(AnyBut('"\n\\')), 'CHARS'),
            (Str("'"), 'CHARS'),
            (Str("\n"), Method('unclosed_string_action')),
            (Str('"'), Method('end_string_action')),
            (Eof, 'EOF')
        ]),
        
        State('TSQ_STRING', [
            (escapeseq, 'ESCAPE'),
            (Rep1(AnyBut("'\"\n\\")), 'CHARS'),
            (Any("'\""), 'CHARS'),
            (Str("\n"), 'NEWLINE'),
            (Str("'''"), Method('end_string_action')),
            (Eof, 'EOF')
        ]),
        
        State('TDQ_STRING', [
            (escapeseq, 'ESCAPE'),
            (Rep1(AnyBut('"\'\n\\')), 'CHARS'),
            (Any("'\""), 'CHARS'),
            (Str("\n"), 'NEWLINE'),
            (Str('"""'), Method('end_string_action')),
            (Eof, 'EOF')
        ]),
        
        (Eof, Method('eof_action'))
        ],
        
        # FIXME: Plex 1.9 needs different args here from Plex 1.1.4
        #debug_flags = scanner_debug_flags,
        #debug_file = scanner_dump_file
        )

