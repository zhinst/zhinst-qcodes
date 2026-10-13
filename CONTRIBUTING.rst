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

Building the documentation
--------------------------

Zhinst-qcodes uses `Sphinx <https://pypi.org/project/Sphinx/>`_ to build the package documentation.

- Install the package in editable mode

    .. code-block:: sh

        $ pip install -e .

Change to docs directory

    .. code-block:: sh

        $ cd docs

- Install the docs dependencies

    .. code-block:: sh

        $ uv pip install --group docs -e .

- Build the HTML documentation along with examples with Sphinx

    .. code-block:: sh

        $ make html [local | remote]

The generated documentation can be seen in your browser by opening `docs/html/index.html`.

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

Adding to documentation
-----------------------

To include an example in the HTML documentation, create an NB link in `docs <https://github.com/zhinst/zhinst-qcodes/tree/main/docs/source/examples>`_.
