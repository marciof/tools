Description
===========

.. automodule:: argf
    :exclude-members: __weakref__
    :members:
    :show-inheritance:
    :special-members:

    Reference
    =========

    ..
        TODO: Ensure special-members are included when using the
        ``special-members`` flag option. Doesn't seem to work otherwise.
    .. autodata:: __features__
    .. autodata:: __version__

Example
=======

Source code:

.. literalinclude:: ../examples/grep.py

Command line usage help:

.. command-output:: python examples/grep.py -h
    :cwd: ..

Error handling:

.. command-output:: python examples/grep.py --invert=false
    :cwd: ..
    :returncode: 2

User defined errors:

.. command-output:: python examples/grep.py ''
    :cwd: ..
    :returncode: 2
