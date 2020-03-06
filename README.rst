QuantiPhy Eval — Computations with Physical Quantities
======================================================

:Author: Ken Kundert
:Version: 0.0.0
:Released: 2020-02-14


A companion to *QuantiPhy*, *quantiphy_eval* evaluates strings that contains 
a simple algebraic expression that involves quantities and returns a quantity.  
For example::

    >>> from quantiphy_eval import evaluate

    >>> average = evaluate('($1.2M + $1.3M)/2', '$')
    >>> print(f'{average}')
    $1.25M

    >>> f_avg = evaluate('(122.317MHz + 129.349MHz)/2', 'Hz')
    >>> print(f'{f_avg}')
    125.83 MHz

With *QuantiPhy* the units do not survive operations, so you can specify the 
resolved units using the second argument.

*QuantiPhy Eval* provides three constants built-in: ``pi``, ``tau``, and ``e``.  
However, you can pass in additional constants::

    >>> from quantiphy import Quantity

    >>> my_constants = dict(
    ...     k = Quantity('k'),
    ...     q = Quantity('q'),
    ...     T = Quantity('25°C', scale='K'),
    ... )
    >>> vt = evaluate('k*T/q', 'V', constants=my_constants)
    >>> print(vt)
    25.693 mV

*QuantiPhy Eval* provides the following functions built-in: ``sin``, ``cos``, 
``tan``, ``sqrt``, ``abs``, ``trunc``, ``round`` and ``sgn``.  However, you can 
pass in additional functions::

    >>> def median(*args):
    ...    args = sorted(args)
    ...    l = len(args)
    ...    m = l//2
    ...    if l % 2:
    ...        return args[m]
    ...    return (args[m] + args[m-1])/2

    >>> my_functions = dict(median=median)
    >>> median_price = evaluate('median($636122, $749151, $706781)', '$', functions=my_functions)
    >>> print(median_price.fixed(show_commas=True))
    $706,781

Finally, *QuantiPhy Eval* provides ``rm_commas`` function for removing commas 
from an expression. Using it would prevent you from using multi-argument 
functions, however it would allow you to have commas in your numbers::

    >>> from quantiphy_eval import evaluate, rm_commas

    >>> average_price = evaluate(rm_commas('($636,122 + $749,151 + $706,781)/3'), '$')
    >>> print(average_price.fixed(show_commas=True, prec=2, strip_zeros=False))
    $697,351.33


Releases
--------

**Latest development release**:
    | Version: 0.0.0
    | Released: 2020-02-14

**0.1 (2019-09-03)**:
    - Add support for user-defined constants and functions.
    - add ``rm_commas`` function.

**0.0 (2020-02-14)**:
    Initial version.
