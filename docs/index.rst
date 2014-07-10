Description
===========

.. automodule:: argf
    :exclude-members: __weakref__
    :members:
    :show-inheritance:
    :special-members:

    Reference
    =========

    .. autodata:: __features__
    .. autodata:: __version__

Example
=======

Source code:

.. literalinclude:: ../examples/grep.py

Command line usage help:

.. command-output:: python examples/grep.py -h
    :cwd: ..

Command line error handling:

.. command-output:: python examples/grep.py ''
    :cwd: ..
    :returncode: 2
