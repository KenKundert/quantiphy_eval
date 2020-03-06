# Description {{{1
# Imports {{{1
from pyparsing import (
    Literal, Word, Group, Optional, ZeroOrMore, Forward,
    nums, alphas, delimitedList, Regex, ParseException, ParseResults
)
import math
import operator
from quantiphy import Quantity
from inform import Error, full_stop

# Parameters {{{1
OPERATORS = {
    "+" : operator.add,
    "-" : operator.sub,
    "*" : operator.mul,
    "/" : operator.truediv,
    "^" : operator.pow,
}
FUNCTIONS  = {
    "sin" : math.sin,
    "cos" : math.cos,
    "tan" : math.tan,
    "sqrt" : math.sqrt,
    "abs" : abs,
    "trunc" : lambda a: int(a),
    "round" : round,
    "sgn" : lambda a: (a > 0) - (a < 0) or 0,
}
CONSTANTS  = {
    "e" : math.e,
    "pi" : math.pi,
    "tau" : math.tau,
}


# Globals {{{1
expr_stack = []
bnf = None
active_operators = None
active_functions = None
active_constants = None
__released__ = '2020-02-14'
__version__ = '0.0.0'

# Parser {{{1
def rm_commas(s):
    return s.replace(',', '')

# push_first {{{2
def push_first(strg, loc, toks):
    expr_stack.append(toks[0])

# push_unary_minus {{{2
def push_unary_minus(strg, loc, toks):
    for t in toks:
        if t == '-':
            expr_stack.append('unary -')
        else:
            break

# BNF {{{2
def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: number | function '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        fnumber = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")

        def named_regex(name, regex):
            return '(?P<%s>%s)' % (name, regex)

        input_sf = 'kMGTPEZYmunpfazy'
        UNIT_SYMBOLS = '°ÅΩ℧'
        CURRENCY_SYMBOLS = '$€¥£₩₺₽₹ɃΞȄ'

        sign = named_regex('sign', '[-+−＋]?')
        space = r'[\s ]'  # the space in this regex is a non-breaking space
        required_digits = r'(?:[0-9][0-9_]*[0-9]|[0-9]+)'  # allow interior underscores
        optional_digits = r'(?:[0-9][0-9_]*[0-9]|[0-9]*)'
        mantissa = named_regex(
            'mant',
            r'(?:{od}\.?{rd})|(?:{rd}\.?{od})'.format(
                rd=required_digits, od=optional_digits
            ),  # leading or trailing digits are optional, but not both
        )
        exponent = named_regex('exp', '[eE][-+]?[0-9]+')
        scale_factor = named_regex('sf', '[%s]' % input_sf)
        units = named_regex(
            r'units', r'(?:[a-zA-Z%√{us}][-^/\w·⁻⁰¹²³⁴⁵⁶⁷⁸⁹√{us}]*)?'.format(
                us=UNIT_SYMBOLS
            )
            # examples: Ohms, V/A, J-s, m/s^2, H/(m-s), Ω, %, m·s⁻², V/√Hz
            # leading char must be letter to avoid 1.0E-9s -> (1e18, '-9s')
        )
        currency = named_regex('currency', '[%s]' % CURRENCY_SYMBOLS)

        number_with_exponent = Regex(r'{sign}{mantissa}{exponent}{space}*{units}'.format(**locals()))
        simple_number = Regex(r'{sign}{mantissa}{space}*{units}'.format(**locals()))
        currency_with_scale_factor = Regex(r'{sign}{currency}{mantissa}{space}*{scale_factor}'.format(**locals()))
        currency_with_exponent = Regex(r'{sign}{currency}{mantissa}{exponent}'.format(**locals()))
        simple_currency = Regex(r'{sign}{currency}{mantissa}'.format(**locals()))

        ident = Word(alphas, alphas+nums+"_")

        plus  = Literal("+")
        minus = Literal("-")
        mult  = Literal("*")
        div   = Literal("/")
        lpar  = Literal("(").suppress()
        rpar  = Literal(")").suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal("^")

        expr = Forward()
        atom = (
            (0,None)*minus + (
                number_with_exponent |
                simple_number |
                currency_with_exponent |
                currency_with_scale_factor |
                simple_currency |
                Group(ident + lpar + Optional(delimitedList(Group(expr), delim=',')) + rpar) |
                ident
            ).setParseAction(push_first) | Group(lpar + expr + rpar)
        ).setParseAction(push_unary_minus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(push_first))
        term = factor + ZeroOrMore((multop + factor).setParseAction(push_first))
        expr << term + ZeroOrMore((addop + term).setParseAction(push_first))
        bnf = expr
    return bnf

# Calculator {{{1
# evaluate_stack {{{2
def evaluate_stack(s):
    op = s.pop()
    if op == 'unary -':
        return -evaluate_stack(s)
    if op in active_operators:
        op2 = evaluate_stack(s)
        op1 = evaluate_stack(s)
        return active_operators[op](op1, op2)
    elif op in active_constants:
        return active_constants[op]
    elif op[0] in active_functions:
        name = op[0]
        args = op[1:]
        ops = reversed([evaluate_stack(s) for arg in args])
        x= active_functions[name](*ops)
        return x
    elif op[0].isalpha():
        if isinstance(op, ParseResults):
            op = op[0]
        raise Error("invalid identifier '%s'." % op)
    else:
        return Quantity(op)

# evaluate {{{2
def evaluate(
    expr,
    units = None,
    constants = None,
    functions = None,
):
    """
    Evaulate an expression.

    The expression may contain numbers with units and SI scale factors.

    expr (str):
        The expression to evaluate.
    units (str):
        The units of the final result.
    constants (dict):
        Values you wish to predefine.
        If not given you get the base set: pi = π, tau=2π
    functions (dict):
        Functions you wish to predefine.
        If not given you get the base set: sin, cos, tan, sqrt, abs, trunc, round, sgn
    """
    global expr_stack, active_constants, active_functions, active_operators
    expr_stack = []
    active_constants = CONSTANTS.copy()
    active_functions = FUNCTIONS.copy()
    active_operators = OPERATORS
    if constants:
        active_constants.update(constants)
    if functions:
        active_functions.update(functions)
    dups = (
        (active_constants.keys() & active_functions.keys()) |
        (active_functions.keys() & active_operators.keys()) |
        (active_operators.keys() & active_constants.keys())
    )
    if dups:
        raise Error("duplicate name.", culprit=', '.join(dups))

    try:
        tokens = BNF().parseString(expr, parseAll=True)
        result = evaluate_stack(expr_stack[:])
        return Quantity(result, model=units)
    except ParseException as e:
        raise Error(full_stop(e.msg), codicil=[e.line, " " * (e.column - 0) + "^"])

        #ParseExceptions have attributes loc, msg, line, lineno, and column
        # to view the text line and location where the reported ParseException occurs, use:
        #except ParseException as err:
        #    print(err.line)
        #    print(" " * (err.column - 1) + "^")
        #    print(err)



