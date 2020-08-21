from inform import display, Error, full_stop, get_culprit
from quantiphy import Quantity
import operator
from sly import Lexer, Parser

# Globals {{{1
VARIABLES = {}
FUNCTIONS = {}
QUANTITY = Quantity
__version__ = '0.3.0'
__released__ = '2020-08-12'
__all__ = ['evaluate', 'initialize', 'rm_commas', 'Error']


# QELexer {{{1
class QELexer(Lexer):

    tokens = (
        NAME,
        POW,
        SIMPLE_NUMBER,
        NUMBER_WITH_EXPONENT,
        CURRENCY_WITH_SCALE_FACTOR,
        CURRENCY_WITH_EXPONENT,
        SIMPLE_CURRENCY,
    )
    literals = "=+-*/(),"
    ignore = " \t"
    POW = r'\*\*'

    # numbers
    _SCALE_FACTORS = 'kMGTPEZYmµμunpfazy'
    _UNIT_SYMBOLS = '°ÅΩƱΩ℧'
    _CURRENCY_SYMBOLS = '$€¥£₩₺₽₹ɃΞȄ'

    _required_digits = r'([0-9][0-9_]*[0-9]|[0-9]+)'  # allow interior underscores
    _optional_digits = r'([0-9][0-9_]*[0-9]|[0-9]*)'
    _mantissa = r'(({od}\.?{rd})|({rd}\.?{od}))'.format(
        rd=_required_digits, od=_optional_digits
    )   # leading or trailing digits are optional, but not both
    _exponent = '[eE][-+]?[0-9]+'
    _scale_factor = f'[{_SCALE_FACTORS}]'
    _units = r'[ ]?[a-zA-Z{us}]*'.format(us=_UNIT_SYMBOLS)  # examples: Ohms, Ω
    _currency = f'[{_CURRENCY_SYMBOLS}]'

    NUMBER_WITH_EXPONENT = f'{_mantissa}{_exponent}{_units}'
    SIMPLE_NUMBER = f'{_mantissa}{_units}'
    CURRENCY_WITH_EXPONENT = f'{_currency}{_mantissa}{_exponent}'
    CURRENCY_WITH_SCALE_FACTOR = f'{_currency}{_mantissa}{_scale_factor}'
    SIMPLE_CURRENCY = f'{_currency}{_mantissa}'

    # names
    _greek = "αβγδεζηθικλνξοπρςστµμυφχψω"
    _Greek = "ΑΒΓΔΕΖΗΘΙΚΛΝΞΟΠΡΣΣΤΜΜΥΦΧΨΩ"
    _special = "ħ"
    NAME = f"[a-zA-Z_{_greek}{_Greek}{_special}][a-zA-Z0-9_₀]*"

    # special tokens
    ignore_comment = r'\#.*'

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)


    def error(self, t):
        raise Error(f"Illegal character '{t.value[0]}'.", culprit=get_culprit())


# QEParser {{{1
class QEParser(Parser):
    tokens = QELexer.tokens

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
    @_("NAME '=' expr")
    def statement(self, p):
        VARIABLES[p.NAME] = p.expr
        return p.NAME, p.expr


    @_("expr")
    def statement(self, p):
        return None, p.expr


    @_("expr '+' expr",
       "expr '-' expr",
       "expr '*' expr",
       "expr '/' expr",
       "expr POW expr"
    )
    def expr(self, p):
        op = self.binary_operators[p[1]]
        return op(p.expr0, p.expr1)


    @_("'-' expr %prec UMINUS")
    def expr(self, p):
        return -p.expr


    @_("'(' expr ')'")
    def expr(self, p):
        return p.expr


    @_("SIMPLE_NUMBER",
       "NUMBER_WITH_EXPONENT",
       "CURRENCY_WITH_SCALE_FACTOR",
       "CURRENCY_WITH_EXPONENT",
       "SIMPLE_CURRENCY")
    def expr(self, p):
        return QUANTITY(p[0])


    @_("NAME")
    def expr(self, p):
        try:
            return VARIABLES[p.NAME]
        except LookupError:
            raise Error("variable unknown.", culprit=get_culprit(p.NAME))


    @_("function")
    def expr(self, p):
        return p.function


    @_("NAME '(' arg_list ')'")
    def function(self, p):
        try:
            func = FUNCTIONS[p.NAME]
        except LookupError:
            raise Error("function unknown.", culprit=get_culprit(p.NAME))
        try:
            return func(*p.arg_list)
        except Exception as e:
            raise Error(full_stop(e), culprit=get_culprit(p.NAME))


    @_("arg ',' arg_list")
    def arg_list(self, p):
        return [p.arg] + p.arg_list


    @_("arg")
    def arg_list(self, p):
        return [p.arg]


    @_("")
    def arg_list(self, p):
        return []


    @_("expr")
    def arg(self, p):
        return p.expr


    def error(self, p):
        if p:
            raise Error(f"Syntax error at '{p.value}'.", culprit=get_culprit())
        else:
            raise Error("Syntax error at EOF.", culprit=get_culprit())


# Build the parser {{{1

lexer = QELexer()
parser = QEParser()



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

    name, value = parser.parse(lexer.tokenize(expr))
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
        1e-9, F ==> 1 nF
        1 MHz ==> 1 MHz
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
