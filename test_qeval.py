# encoding: utf8

from quantiphy_eval import evaluate, rm_commas
from inform import Error
from pytest import raises, approx
from quantiphy import Quantity
import math

#!/usr/bin/env python3

my_funcs = dict(
    two_pi = lambda: math.tau,
    max = max,
    min = min,
)

cases = [
    ([rm_commas('$164,921.77 + $161,840.03')], dict(units='$')),
    (['1MHz'], dict()),
    (['1GiB'], dict()),
    (['1MHz + 1MHz', 'Hz'], dict()),
    (['1 MHz + 1 MHz', 'Hz'], dict()),
    (['rand()'], dict(functions=my_funcs)),
    (['abs(1+1)'], dict(functions=my_funcs)),
    (['abs(1 MHz)', 'Hz'], dict(functions=my_funcs)),
    (['abs($161840.03)', '$'], dict(functions=my_funcs)),
    (['abs(1e-9)', 'F'], dict(functions=my_funcs)),
    (['max(1MHz, 4MHz)'], dict(functions=my_funcs)),
    (['max(1+1, 2+2)'], dict(functions=my_funcs)),
    (['max(1+1, 2+2, 3+3)'], dict(functions=my_funcs)),
]

def test_quantities():
    assert evaluate('$2.5M').render() == '$2.5M'
    assert evaluate('$1.3M + $1.2M', '$').render() == '$2.5M'
    assert evaluate('($1.3M + $1.2M)/2', '$').render() == '$1.25M'
    assert evaluate('($1.3M - $1.2M)/2', '$').render() == '$50k'
    assert evaluate('($1.3M + -$1.2M)/2', '$').render() == '$50k'
    assert evaluate('2*pi*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate('2*pi*1420.405751786 MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate(rm_commas('($1,220,317 + $1,293,494)/2'), '$').render() == '$1.2569M'
    assert evaluate('($1_220_317 + $1_293_494)/2', '$').render() == '$1.2569M'

def test_functions():
    assert evaluate('two_pi()', functions=my_funcs).render() == '6.2832'
    assert evaluate('abs(-1+-1)', functions=my_funcs).render() == '2'
    #assert evaluate('abs(-1 MHz)', 'Hz', functions=my_funcs).render() == '1 MHz'
    assert evaluate('abs($161840.03)', '$', functions=my_funcs).render() == '$161.84k'
    assert evaluate('abs(1e-9)', 'F', functions=my_funcs).render() == '1 nF'
    #assert evaluate('max(1MHz, 4MHz)', functions=my_funcs).render() == '4 MHz'
    assert evaluate('max(1+1, 2+2)', functions=my_funcs).render() == '4'
    assert evaluate('max(1+1, 2+2, 3+3)', functions=my_funcs).render() == '6'
    with Quantity.prefs(prec=2, strip_zeros=False, show_commas=True):
        res = evaluate(rm_commas('round(($1,220,317 + $1,293,494)/2)'), '$')
        assert res.fixed() == '$1,256,906.00'

def test_original():
    assert evaluate("9") == 9
    assert evaluate("-9") == -9
    assert evaluate("--9") == 9
    assert evaluate("-e") == -math.e
    assert evaluate("9 + 3 + 6") == 9 + 3 + 6
    assert evaluate("9 + 3 / 11") == 9 + 3.0 / 11
    assert evaluate("(9 + 3)") == (9 + 3)
    assert evaluate("(9+3) / 11") == (9+3.0) / 11
    assert evaluate("9 - 12 - 6") == 9 - 12 - 6
    assert evaluate("9 - (12 - 6)") == 9 - (12 - 6)
    assert evaluate("2*3.14159") == 2*3.14159
    assert evaluate("3.1415926535*3.1415926535 / 10") == 3.1415926535*3.1415926535 / 10
    assert evaluate("pi * pi / 10") == math.pi * math.pi / 10
    assert evaluate("pi*pi/10") == math.pi*math.pi/10
    assert evaluate("pi^2") == math.pi**2
    assert evaluate("round(pi^2)") == round(math.pi**2)
    assert evaluate("6.02E23 * 8.048") == 6.02E23 * 8.048
    assert evaluate("e / 3") == math.e / 3
    assert evaluate("sin(pi/2)") == math.sin(math.pi/2)
    assert evaluate("trunc(e)") == int(math.e)
    assert evaluate("trunc(-e)") == int(-math.e)
    assert evaluate("round(e)") == round(math.e)
    assert evaluate("round(-e)") == round(-math.e)
    assert evaluate("e^pi") == math.e**math.pi
    assert evaluate("2^3^2") == 2**3**2
    assert evaluate("2^3+2") == 2**3+2
    assert evaluate("2^3+5") == 2**3+5
    assert evaluate("2^9") == 2**9
    assert evaluate("sgn(-2)") == -1
    assert evaluate("sgn(0)") == 0
    with raises(Error) as exception:
        evaluate("foo(0.1)")
    assert str(exception.value) == "invalid identifier 'foo'."
    assert evaluate("sgn(0.1)") == 1
    assert evaluate("$1.3M + $1.2M") == 2.5e6
    assert evaluate("($1.3M + $1.2M)/2") == 1.25e6


if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.
    from inform import Error

    defined = dict(globals())
    for k, v in defined.items():
        try:
            if callable(v) and k.startswith('test_'):
                print()
                print('Calling:', k)
                print((len(k)+9)*'=')
                v()
        except Error as e:
            e.report()
