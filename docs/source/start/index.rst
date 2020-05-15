Getting Started
===============

LabOne software
^^^^^^^^^^^^^^^

As prerequisite, the LabOne software version 20.01 or later must be installed. 
It can be downloaded for free `here <https://www.zhinst.com/labone>`_. Follow 
the installation instructions specific to your platform. Verify that you can 
connect to your instrument(s) using the web interface of LabOne. If you are 
upgrading from an older version, be sure to update the firmware of al your 
devices using the web interface before continuing.

In principle LabOne can be installed in a remote machine, but we highly 
recommend to install on the local machine where you intend to run the 
experiment.

Install QCoDeS
^^^^^^^^^^^^^^

QCodes will be automatically installed as dependency, but it's advised to 
install it manually before according to the `QCoDeS documentation 
<https://qcodes.github.io/Qcodes/start/index.html#installation>`_.

Install :mod:`zhinst-qcodes`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This installation methos is recommended for the majority of the users that don't need to modify the zhinst-qcodes package.
zhinst-qcodes is packaged on PyPI, so it's enough to write in the prompt

.. code-block:: bash

    pip install zhinst-qcodes


Upgrade
^^^^^^^

The upgrade is very similar to the installation; from the prompt type

.. code-block:: bash

    pip install --upgrade zhinst-qcodes


The upgrade is highly recommended if you are upgrading LabOne as well.

Install from source
^^^^^^^^^^^^^^^^^^^

If you need to modify the zhinst-qcodes package or you need a fature that it's 
not in the release yet, you may install the development version. This is 
recommended only to advanced users with advanced knowledge of Python and Git.
Clone the `zhinst-qcodes GitHub repository 
<https://github.com/zhinst/zhinst-qcodes>`_. Then move to the root of repository 
and install it with

.. code-block:: bash

    python setup.py install


Please not that the installation in editable mode (i.e. setuptools "develop 
mode") is not supported, so the commands `pip install -e .` or 
`python setup.py develop` will create a non-working installation. This is a 
restriction of the namespace Python package as defined in PEP420 (see also 
`<https://github.com/pypa/pip/issues/7265>`_).
