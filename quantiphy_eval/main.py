from inform import display, Error, full_stop
from quantiphy import Quantity
import operator
from . import lex
from . import yacc

# Globals {{{1
VARIABLES = {}
FUNCTIONS = {}
QUANTITY = Quantity


# Lexer {{{1
# tokens {{{2
tokens = (
    "NAME",
    "POW",
    "SIMPLE_NUMBER",
    "NUMBER_WITH_EXPONENT",
    "CURRENCY_WITH_SCALE_FACTOR",
    "CURRENCY_WITH_EXPONENT",
    "SIMPLE_CURRENCY",
)
literals = "=+-*/(),"
t_ignore = " \t"
t_POW = r'\*\*'
greek = "αβγδεζηθικλνξοπρςστµμυφχψω"
Greek = "ΑΒΓΔΕΖΗΘΙΚΛΝΞΟΠΡΣΣΤΜΜΥΦΧΨΩ"
special = "ħ"
t_NAME = f"[a-zA-Z_{greek}{Greek}{special}][a-zA-Z0-9_₀]*"

# numbers {{{3
SCALE_FACTORS = 'kMGTPEZYmµμunpfazy'
UNIT_SYMBOLS = '°ÅΩƱΩ℧'
CURRENCY_SYMBOLS = '$€¥£₩₺₽₹ɃΞȄ'

required_digits = r'([0-9][0-9_]*[0-9]|[0-9]+)'  # allow interior underscores
optional_digits = r'([0-9][0-9_]*[0-9]|[0-9]*)'
mantissa = r'(({od}\.?{rd})|({rd}\.?{od}))'.format(
    rd=required_digits, od=optional_digits
)   # leading or trailing digits are optional, but not both
exponent = '[eE][-+]?[0-9]+'
scale_factor = f'[{SCALE_FACTORS}]'
units = r'[a-zA-Z{us}]*'.format(us=UNIT_SYMBOLS)  # examples: Ohms, Ω
currency = f'[{CURRENCY_SYMBOLS}]'

t_SIMPLE_NUMBER = f'{mantissa}{units}'
t_NUMBER_WITH_EXPONENT = f'{mantissa}{exponent}{units}'
t_CURRENCY_WITH_SCALE_FACTOR = f'{currency}{mantissa}{scale_factor}'
t_CURRENCY_WITH_EXPONENT = f'{currency}{mantissa}{exponent}'
t_SIMPLE_CURRENCY = f'{currency}{mantissa}'


# special tokens {{{3
def t_comment(t):
    r'\#.*'
    pass
    # No return value. Token discarded


def t_newline(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    raise Error(f"Illegal character '{t.value[0]}'.")
    t.lexer.skip(1)


# Parser {{{1
# globals {{{2
precedence = (
    ("left", "+", "-"),
    ("left", "*", "/"),
    ("right", "POW"),
    ("right", "UMINUS"),
)
binary_operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '**': operator.pow,
}


# rules {{{2
def p_statement_assign(p):
    'statement : NAME "=" expression'
    VARIABLES[p[1]] = p[3]
    p[0] = p[1], p[3]


def p_statement_expr(p):
    "statement : expression"
    p[0] = None, p[1]


def p_expression_binop(p):
    """expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression POW expression"""
    op = binary_operators[p[2]]
    p[0] = op(p[1], p[3])


def p_expression_function(p):
    "expression : function"
    p[0] = p[1]


def p_function(p):
    "function : NAME '(' arg_list ')'"
    try:
        func = FUNCTIONS[p[1]]
    except LookupError:
        raise Error("function unknown.", culprit=p[1])
    try:
        p[0] = func(*p[3])
    except Exception as e:
        raise Error(full_stop(e), culprit=p[1])


def p_arg_list_partial(p):
    "arg_list : arg ',' arg_list"
    p[0] = [p[1]] + p[3]


def p_arg_list_terminal(p):
    "arg_list : arg"
    p[0] = [p[1]]


def p_arg_list_empty(p):
    "arg_list :"
    p[0] = []


def p_arg_expression(p):
    "arg : expression"
    p[0] = p[1]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    """
    expression : SIMPLE_NUMBER
               | NUMBER_WITH_EXPONENT
               | CURRENCY_WITH_SCALE_FACTOR
               | CURRENCY_WITH_EXPONENT
               | SIMPLE_CURRENCY
    """
    p[0] = QUANTITY(p[1])


def p_expression_name(p):
    "expression : NAME"
    try:
        p[0] = VARIABLES[p[1]]
    except LookupError:
        raise Error("variable unknown.", culprit=p[1])
        p[0] = 0


def p_error(p):
    if p:
        raise Error(f"Syntax error at '{p.value}'.")
    else:
        raise Error("Syntax error at EOF.")


# Build the parser {{{1

lexer = lex.lex()
parser = yacc.yacc()


# Public functions {{{1
# Initialize evaluator {{{2
def initialize(variables = None, functions = None, quantity = None):
    """
    Initialize evaluator.

    variables (dict):
        Values you wish to pre-define.
    functions (dict):
        Functions you wish to pre-define.
    """
    global VARIABLES, FUNCTIONS, QUANTITY
    if variables is not None:
        VARIABLES = variables
    if functions is not None:
        FUNCTIONS = functions
    if quantity is not None:
        QUANTITY = quantity


# Evaluate expression {{{2
def evaluate(expr, units = None):
    """
    Evaulate an expression.

    The expression may contain numbers with units and SI scale factors.

    expr (str):
        The expression to evaluate.
    units (str):
        The units of the final result.
    """

    # # show output of lexer
    # lex.lexer.input(expr)
    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break      # No more input
    #     print(tok)

    name, value = yacc.parse(expr)
    return QUANTITY(value, model=units, name=name)


# Remove commas {{{2
def rm_commas(s):
    """
    Remove commas

    First removes any commas from the argument.
    Then convert all semicolons to commas.
    """
    return s.replace(',', '').replace(';', ',')


# Main {{{1
if __name__ == '__main__':
    from math import pi, tau
    variables = dict(
        pi = pi,
        π = pi,
        tau = tau,
        τ = tau,
    )
    for constant in 'h ħ k q c ε₀ eps0 μ₀ mu0'.split():
        variables[constant] = QUANTITY(constant)
    variables['T₀'] = Quantity('0°C')

    def median(*args):
        args = sorted(args)
        n = len(args)
        m = n//2
        if n % 2:
            return args[m]
        return (args[m] + args[m-1])/2

    # average {{{3
    def average(*args):
        return sum(args)/len(args)

    functions = dict(
        median = median,
        average = average,
        min = min,
        max = max,
    )
    initialize(variables, functions)

    cases = '''
        1MHz ==> 1 MHz
        1GiB ==> 1 GiB
        1MHz + 1MHz, Hz ==> 2 MHz
        $2.5M ==> $2.5M
        $250k*1.025**15, $ ==> $362.07k
        $1.3M + $1.2M, $ ==> $2.5M
        ($1.3M + $1.2M)/2, $ ==> $1.25M
        ($1.3M - $1.2M)/2, $ ==> $50k
        ($1.3M + -$1.2M)/2, $ ==> $50k
        2*pi*1420.405751786MHz, rads/s ==> 8.9247 Grads/s
        2*π*1420.405751786MHz, rads/s ==> 8.9247 Grads/s
        ($1_220_317 + $1_293_494)/2, $ ==> $1.2569M
        ($1_220_317 + $1_293_494)/2, $ ==> $1.2569M
        T = T₀ + 25, K ==> T = 298.15 K
        Vt = k*T/q, V ==> Vt = 25.693 mV
        max($1.5M; $1.3M; $1.2M), $ ==> $1.5M
        min($1.5M; $1.3M; $1.2M), $ ==> $1.2M
        average($1.5M; $1.3M; $1.2M), $ ==> $1.3333M
        median($1.5M; $1.3M; $1.2M), $ ==> $1.3M
    '''
    from inform import InformantFactory
    succeeds = InformantFactory(clone=display, message_color = 'green')
    fails = InformantFactory(clone=display, message_color = 'red')
    Quantity.set_prefs(show_label='f', known_units='K')
    for case in cases.splitlines():
        given, _, expected = case.partition('==>')
        expr, _, units = given.partition(',')
        expr = rm_commas(expr.strip())
        units = units.strip()
        expected = expected.strip()
        if expr:
            try:
                q = evaluate(expr, units)
                report = succeeds if str(q) == expected else fails
                report(f'{expr:>40} ==> {q}')
            except Error as e:
                e.report(codicil=f'Found on: {expr}.')
