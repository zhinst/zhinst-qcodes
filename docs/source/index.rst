.. image:: images/zhinst_logo_sep_horiz_2019_1000.png
   :width: 400
   :target: https://www.zhinst.com

|

Zurich Instruments QCoDeS driver 0.3 Documentation
=========================================================

The Zurich Instruments drivers for QCoDeS (zhinst-qcodes) is a package of
instrument drivers for devices produced by
`Zurich Instruments <https://www.zhinst.com>`_ for QCoDeS.
`QCoDeS <http://qcodes.github.io/Qcodes>`_ is a Python-based data acquisition
framework developed to serve the needs of nanoelectronic device experiments,
but not limited to that.

The drivers are based on `zhinst-toolkit <https://github.com/zhinst/zhinst-toolkit>`,
a generic high level python driver for LabOne. Except for the node tree which in
case for the zhinst-qcodes driver is implemented with the native QCoDeS
Parameters both driver behave the same. To be even more precise the
zhinst-qcodes forwards all calls (functions, parameters ...) to zhinst qcodes
and has no logic builtin what so ever.

For the most cases the
`zhinst-toolkit documentation <https://docs.zhinst.com/zhinst-toolkit/en/latest/>`_
will therefor serve as a reference for this package as well. If you can not find
a answer to your question here please refer to the
`zhinst-toolkit documentation <https://docs.zhinst.com/zhinst-toolkit/en/latest/>`_
instead.

Get started with the :ref:`first_steps/installation:Installation` and then get
an overview with the :ref:`first_steps/quickstart:Quickstart` guide.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   first_steps/index
   examples/index
   refactoring/index
   package_documentation
   changelog/index
   license/index
   about/index



Index
=====

* :ref:`genindex`

