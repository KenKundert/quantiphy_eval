#!/usr/bin/env python3

# encoding: utf8

from quantiphy_eval import evaluate, initialize, rm_commas
from inform import Error
from pytest import raises, approx
from quantiphy import Quantity
import math

my_constants = dict(
    pi = math.pi,
    π = math.pi,
    tau = math.tau,
    τ = math.tau,
)
for name in 'h ħ k q c ε₀ eps0 μ₀ mu0'.split():
    my_constants[name] = Quantity(name)
my_constants['T₀'] = Quantity('0°C')

def median(*args):
    args = sorted(args)
    l = len(args)
    m = l//2
    if l % 2:
        return args[m]
    return (args[m] + args[m-1])/2

def average(*args):
    return sum(args)/len(args)

my_funcs = dict(
    average = average,
    median = median,
    max = max,
    min = min,
    abs = abs,
    two_pi = lambda: math.tau,
)

cases = [
    (rm_commas('$164,921.77 + $161,840.03'), '$', '$326.76k'),
    ('1MHz', None, '1 MHz'),
    ('1GiB', None, '1 GiB'),
    ('1MHz + 1MHz', 'Hz', '2 MHz'),
    ('abs(1+1)', None, '2'),
    ('abs(1MHz)', 'Hz', '1 MHz'),
    ('abs($161840.03)', '$', '$161.84k'),
    ('abs(1e-9)', 'F', '1 nF'),
    ('max(1MHz, 4MHz)', 'Hz', '4 MHz'),
    ('max(1+1, 2+2)', None, '4'),
    ('max(1+1, 2+2, 3+3)', None, '6'),
]

def test_cases():
    initialize(my_constants, my_funcs)
    for expr, units, expected in cases:
        result = str(evaluate(expr, units))
        print(f'given={expr}, {units}, expected = {expected}, result = {result}')
        assert result == expected

def test_quantities():
    assert evaluate('$2.5M').render() == '$2.5M'
    assert evaluate('$1.3M + $1.2M', '$').render() == '$2.5M'
    assert evaluate('($1.3M + $1.2M)/2', '$').render() == '$1.25M'
    assert evaluate('($1.3M - $1.2M)/2', '$').render() == '$50k'
    assert evaluate('($1.3M + -$1.2M)/2', '$').render() == '$50k'
    assert evaluate('2*pi*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate('2*π*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate('tau*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate('τ*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate('two_pi()*1420.405751786MHz', 'Hz').render() == '8.9247 GHz'
    assert evaluate(rm_commas('($1,220,317 + $1,293,494)/2'), '$').render() == '$1.2569M'
    assert evaluate('($1_220_317 + $1_293_494)/2', '$').render() == '$1.2569M'
    with raises(Error) as exception:
        evaluate("2*x")
    assert str(exception.value) == "x: variable unknown."

def test_functions():
    assert evaluate('abs(-1+-1)').render() == '2'
    #assert evaluate('abs(-1 MHz)', 'Hz').render() == '1 MHz'
    assert evaluate('abs($161840.03)', '$').render() == '$161.84k'
    assert evaluate('abs(1e-9)', 'F').render() == '1 nF'
    #assert evaluate('max(1MHz, 4MHz)').render() == '4 MHz'
    assert evaluate('max(1+1, 2+2)').render() == '4'
    assert evaluate('max(1+1, 2+2, 3+3)').render() == '6'
    with Quantity.prefs(prec=2, strip_zeros=False, show_commas=True):
        res = evaluate(rm_commas('($1,220,317 + $1,293,494)/2'), '$')
        assert res.fixed() == '$1,256,905.50'
    with raises(Error) as exception:
        evaluate("two_pi(0.1)")
    assert str(exception.value) == "two_pi: <lambda>() takes 0 positional arguments but 1 was given."
    with raises(Error) as exception:
        evaluate("abs()")
    assert str(exception.value) == "abs: abs() takes exactly one argument (0 given)."
    with raises(Error) as exception:
        evaluate("abs(1, 2)")
    assert str(exception.value) == "abs: abs() takes exactly one argument (2 given)."
    with raises(Error) as exception:
        evaluate("three_pi()")
    assert str(exception.value) == "three_pi: function unknown."

def test_original():
    assert evaluate("9") == 9
    assert evaluate("-9") == -9
    assert evaluate("--9") == 9
    #assert evaluate("-e") == -math.e
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
    assert evaluate("pi**2") == math.pi**2
    assert evaluate("6.02E23 * 8.048") == 6.02E23 * 8.048
    #assert evaluate("e / 3") == math.e / 3
    #assert evaluate("sin(pi/2)") == math.sin(math.pi/2)
    #assert evaluate("trunc(e)") == int(math.e)
    #assert evaluate("trunc(-e)") == int(-math.e)
    #assert evaluate("e^pi") == math.e**math.pi
    assert evaluate("2**3**2") == 2**3**2
    assert evaluate("2**3+2") == 2**3+2
    assert evaluate("2**3+5") == 2**3+5
    assert evaluate("2**9") == 2**9
    #assert evaluate("sgn(-2)") == -1
    #assert evaluate("sgn(0)") == 0
    with raises(Error) as exception:
        evaluate("foo(0.1)")
    assert str(exception.value) == "foo: function unknown."
    #assert evaluate("sgn(0.1)") == 1
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
