Installation
=============

Python version
--------------

We recommend using the latest version of Python. zhinst-qcodes supports Python
3.7 and newer.

Dependencies
------------

These distributions will be installed automatically when installing zhinst-qcodes.

* `numpy <https://pypi.org/project/numpy/>`_ adds support for large, multi-dimensional
  arrays and matrices, along with a large collection of high-level mathematical
  functions to operate on these arrays.
* `qcodes <https://pypi.org/project/qcodes/>`_ is a Python-based data acquisition
  framework developed by the Copenhagen / Delft / Sydney / Microsoft quantum
  computing consortium. zhinst-qcodes is a third party driver for this framework.
* `zhinst <https://pypi.org/project/zhinst/>`_ is the low level python api for Zurich
  Instruments devices.
* `zhinst-toolkit <https://pypi.org/project/zhinst-toolkit/>`_ is a high level
  driver on top of the LabOne® python api.

Install zhinst-qcodes
----------------------

Use the following command to install zhinst-qcodes:

.. code-block:: sh

    $ pip install zhinst-qcodes

zhinst-qcodes is now installed. Check out the :ref:`first_steps/quickstart:Quickstart` or
go back to the :doc:`Documentation Overview <index>`.
