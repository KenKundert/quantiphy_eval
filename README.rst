QuantiPhy Eval — Computations with Physical Quantities
======================================================

.. image:: https://pepy.tech/badge/quantiphy_eval/month
    :target: https://pepy.tech/project/quantiphy_eval

..  image:: https://github.com/KenKundert/quantiphy_eval/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/KenKundert/quantiphy_eval/actions/workflows/build.yaml

.. image:: https://coveralls.io/repos/github/KenKundert/quantiphy_eval/badge.svg?branch=master
    :target: https://coveralls.io/github/KenKundert/quantiphy_eval?branch=master

.. image:: https://img.shields.io/pypi/v/quantiphy_eval.svg
    :target: https://pypi.python.org/pypi/quantiphy_eval

.. image:: https://img.shields.io/pypi/pyversions/quantiphy_eval.svg
    :target: https://pypi.python.org/pypi/quantiphy_eval/

:Author: Ken Kundert
:Version: 0.4.0
:Released: 2021-01-27


A companion to `QuantiPhy <https://quantiphy.readthedocs.io>`_, *quantiphy_eval* 
evaluates strings containing simple algebraic expressions that involve 
quantities. It returns a quantity.  For example::

    >>> from quantiphy_eval import evaluate

    >>> avg_price = evaluate('($1.2M + $1.3M)/2', '$')
    >>> print(avg_price)
    $1.25M

    >>> avg_freq = evaluate('(122.317MHz + 129.349MHz)/2', 'Hz')
    >>> print(avg_freq)
    125.83 MHz

*QuantiPhy Eval* is used in `networth <https://github.com/KenKundert/networth>`_ 
to allow you to give your estimated values using expressions that include 
numbers that have units, SI scale factors, and commas.  That allows you the 
convenience of copy-and-pasting your numbers from websites without being forced 
to reformat them.

With *QuantiPhy* the units do not survive operations, so you can specify the 
resolved units using the second argument.  In fact, the second argument is 
passed to *QuantiPhy* as the `model 
<https://quantiphy.readthedocs.io/en/stable/user.html#the-second-argument-the-model>`_, 
which allows you to give the return value a name and description along with 
units, as demonstrated in the next example.

By default *QuantiPhy Eval* provides no built-in constants.
However, you can add your own constants::

    >>> from quantiphy import Quantity
    >>> from quantiphy_eval import evaluate, initialize
    >>> import math

    >>> my_constants = dict(
    ...     k = Quantity('k'),
    ...     q = Quantity('q'),
    ...     T = Quantity('25°C', scale='K'),
    ...     π = Quantity(math.pi),
    ...     τ = Quantity(math.tau),
    ... )
    >>> initialize(variables=my_constants)

    >>> Vt = evaluate('k*T/q', 'Vt V thermal voltage')
    >>> print(Vt.render(show_label='f'))
    Vt = 25.693 mV -- thermal voltage

Alternatively, you can specify the model directly in the text passed to 
*evaluate*. Simply append it in the form of a double-quoted string.

    >>> Vt = evaluate('k*T/q "Vt V thermal voltage"')
    >>> print(Vt.render(show_label='f'))
    Vt = 25.693 mV -- thermal voltage

You can also use *evaluate* to assign values to names directly, *QuantiPhy Eval* 
remembers these values between calls to *evaluate*::

    >>> f_0 = evaluate('f₀ = 1MHz')
    >>> omega_0 = evaluate('ω₀ = τ*f₀ "rads/s"')
    >>> print(omega_0.render(show_label=True))
    ω₀ = 6.2832 Mrads/s

Similarly, *QuantiPhy Eval* provides no built-in functions by default, but you 
can add any you need::

    >>> def median(*args):
    ...    args = sorted(args)
    ...    l = len(args)
    ...    m = l//2
    ...    if l % 2:
    ...        return args[m]
    ...    return (args[m] + args[m-1])/2

    >>> initialize(functions = dict(median=median))
    >>> median_price = evaluate('median($636122, $749151, $706781)', '$')
    >>> print(median_price.fixed(show_commas=True))
    $706,781

*initialize* takes three arguments, *variables*, *functions* and *quantity*.  
Both *arguments* and *functions* take dictionaries that overwrite any previously 
saved values. *quantity* takes a *quantiphy* *Quantity* class. The return value 
of *evaluate* will be an object of this class.

*rm_commas* is a function for removing commas from an expression. This is used 
if your number contain commas. Simply stripping the commas it would prevent you 
from using multi-argument functions.  However after removing the commas 
*rm_commas* also converts semicolons to commas.  So the previous example could 
be rewritten as::

    >>> from quantiphy_eval import evaluate, rm_commas

    >>> median_price = evaluate(
    ...     rm_commas('median($636,122; $749,151; $706,781)'),
    ...     '$',
    ... )
    >>> print(median_price.fixed(show_commas=True))
    $706,781

*QuantiPhy Eval* supports comments. A ``#`` and anything that follows it to the 
end of the line is ignored::

    >>> average_price = evaluate(
    ...     rm_commas('''
    ...         median(
    ...             $636,122 +   # Zillow
    ...             $749,151 +   # Redfin
    ...             $706,781     # Trulia
    ...         )/3
    ...     '''),
    ...     '$'
    ... )
    >>> print(average_price.fixed(show_commas=True, prec=2, strip_zeros=False))
    $697,351.33

Finally, *QuantiPhy Eval* uses `inform.Error <https://inform.readthedocs.io>`_ 
for error reporting.

    >>> from inform import Error

    >>> try:
    ...     Vt = evaluate('kT/q', 'V')
    ...     print(Vt)
    ... except Error as e:
    ...     print(str(e))
    kT: variable unknown.


Releases
--------

**Latest development release**:
    | Version: 0.4.0
    | Released: 2021-01-27

**0.4 (2021-01-27)**:
    - Add ability to explicitly specify units (or model) in evaluated string.

**0.3 (2020-08-12)**:
    - complete re-write, parser now implemented with ply rather than pyparsing.
    - all built-in constants and functions have been removed.
    - split *evaluate* into two: *evaluate* and *initialize*.

**0.2 (2020-03-06)**:
    - *rm_commas* now converts semicolons to commas
    - support comments

**0.1 (2020-03-05)**:
    - Add support for user-defined constants and functions.
    - add *rm_commas* function.

**0.0 (2020-02-14)**:
    Initial version.
