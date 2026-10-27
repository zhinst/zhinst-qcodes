Ways to contribute
==================

* Opening a new ticket to `Issues`_ or by commenting on existing one with new solutions or suggestions
* By improving the project documentation.
* By improving and adding new project examples.
* By contributing code; bug fixes, new features and so on.

.. _Issues: https://github.com/zhinst/zhinst-qcodes/issues

Code contributions
==================

* Follow `PEP8 <https://peps.python.org/pep-0008/>`_ and you should be fine.

* The project uses `Google Style Python docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_

* The project uses `ruff` (lint + format) and `mypy` to check for code style.

Development environment setup
-----------------------------

- Clone the `zhinst-qcodes` repository

    .. code-block:: sh

        $ git clone https://github.com/zhinst/zhinst-qcodes
        $ cd zhinst-qcodes

- Create a Python virtual environment

- Install the dependencies

    .. code-block:: sh

        $ pip install -r requirements.txt

- Add zhinst-qcodes to `zhinst` package namespace by running the script
  to create a symbolic link between development files and zhinst-package.

    .. note:: 

        Windows: Requires administration privileges.

    .. code-block:: sh
    
        $ python .\scripts\zhinst_qcodes_symlink.py

Running the tests
-----------------

Running all tests
~~~~~~~~~~~~~~~~~

    .. code-block:: sh

        $ pytest

Running lint and format checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code-block:: sh

        $ tox -e ruff

Running typing tests
~~~~~~~~~~~~~~~~~~~~

    .. code-block:: sh

        $ tox -e typing

Running coverage
~~~~~~~~~~~~~~~~

    .. code-block:: sh

        $ pip install coverage
        $ coverage run -m pytest
        $ coverage html

The report can be seen in your browser by opening `htmlcov/index.html`.

Type stubs for the device node trees
------------------------------------

The QCoDeS parameters and submodules of a device (e.g. ``mfli.demods[0].rate``)
are created at runtime from the node tree reported by the LabOne Data Server.
To make them visible to static type checkers and IDEs, ``.pyi`` stubs are
generated for selected devices (``STUB_DEVICES`` in ``generator/conf.py``) and
stored in ``src/zhinst/qcodes/driver/devices/_stubs``. The device classes in
``device_creator.py`` inherit from the generated ``<DEVICE>Nodes`` mixin while
type checking only.

The stubs are generated from the node documentation of the online user manual.
To update the stubs of a device (e.g. the MFLI):

    .. code-block:: sh

        $ python generator/nodedoc_scraper.py MFLI
        $ python generator/generator.py stubs MFLI

The first command downloads the node documentation into
``generator/nodedocs/mfli.json``, the second one creates the stub from it. To
add stubs for a new device, add it to ``STUB_DEVICES`` and regenerate
``device_creator.py`` with ``python generator/generator.py device-api``.

``tests/test_stubs.py`` verifies that the stubs match the node tree created at
runtime and ``tests/typing`` contains static typing checks run by ``tox -e typing``.

Pull requests
--------------

Use `Github pull requests <https://github.com/zhinst/zhinst-qcodes/pulls>`_ to contribute your code.

Use an existing Pull request template and follow it.


Writing examples
================

Examples are a good way to demonstrate on how the library is used to execute various 
experiments and measurements. Examples using `zhinst qcodes` are welcome.

File format
-----------

The examples are Jupyter Notebooks (`.ipynb`), committed as-is in `/examples`.

Structure
---------

Please see the existing examples in /examples and try to keep the same structure.
Including the output of Notebook cells is highly encouraged.
