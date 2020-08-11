QuantiPhy Eval — Computations with Physical Quantities
======================================================

:Author: Ken Kundert
:Version: 0.2.1
:Released: 2020-08-11


A companion to `QuantiPhy <https://quantiphy.readthedocs.io>`_, *quantiphy_eval* 
evaluates strings containing simple algebraic expressions that involve 
quantities. It returns a quantity.  For example::

    >>> from quantiphy_eval import evaluate

    >>> average = evaluate('($1.2M + $1.3M)/2', '$')
    >>> print(f'{average}')
    $1.25M

    >>> f_avg = evaluate('(122.317MHz + 129.349MHz)/2', 'Hz')
    >>> print(f'{f_avg}')
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

Or, you can use *evaluate* to assign values to names directly, *QuantiPhy Eval* 
remembers these values between calls to *evaluate*::

    >>> f_0 = evaluate('f₀ = 1MHz')
    >>> omega_0 = evaluate('ω₀ = τ*f₀', 'rads/s')
    >>> print(omega_0.render(show_label='f'))
    ω₀ = 6.2832 Mrads/s

Similarly, *QuantiPhy Eval* provides no built-in functions by default, but you 
can add any you need.

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

*rm_commas* function for removing commas from an expression. This is used if 
your number contain commas. Simply stripping the commas it would prevent you 
from using multi-argument functions, however after removing the commas 
*rm_commas* also converts semicolons to commas.  So the previous example could 
be rewritten as::

    >>> from quantiphy_eval import evaluate, rm_commas

    >>> median_price = evaluate(
    ...     rm_commas('median($636,122; $749,151; $706,781)'),
    ...     '$',
    ... )
    >>> print(median_price.fixed(show_commas=True))
    $706,781

Finally, *QuantiPhy Eval* supports comments. A ``#`` and anything that follows 
it to the end of the line is ignored::

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


Releases
--------

**Latest development release**:
    | Version: 0.2.1
    | Released: 2020-08-11

**0.3 (2020-03-06)**:
    - complete re-write
    - split *evaluate* into *evaluate* and *initialize*.

**0.2 (2020-03-06)**:
    - *rm_commas* now converts semicolons to commas
    - support comments

**0.1 (2020-03-05)**:
    - Add support for user-defined constants and functions.
    - add *rm_commas* function.

**0.0 (2020-02-14)**:
    Initial version.
