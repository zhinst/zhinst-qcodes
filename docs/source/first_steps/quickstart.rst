Quickstart
==========

Eager to get started? This page gives a good introduction to zhinst-qcodes.
Follow :doc:`installation` to install zhinst-qcodes first.

Preparation
-----------

Before you can spin up zhinst-qcodes LabOne® needs to installed and running.
For a complete reference see the dedicated `user manual <http://docs.zhinst.com/>`_
page for your instrument(s).

Before you continue make sure a LabOne® data server is running in your network and
all of your devices are visible.

Device connection
------------------

Although all Zurich Instruments follow a session based approach the zhinst-qcodes
tries to adapt this to the QCoDeS native device based one. The following guide will
follow the device based approach. However it is still possible to use the
session based approach through the exported `ZISession` object. Please take a
look at the
`zhinst-toolkit documentation <https://docs.zhinst.com/zhinst-toolkit/en/latest/first_steps/quickstart.html>`_
for more information on the usage of the session based approach.

To create a Zurich Instruments device the following information's are needed:

* Serial (Can be found on the back of the instrument)
* server host address (e.g. "localhost" if LabOne is running on the local computer)

.. code-block:: python

    >>> from zhinst.qcodes import HDAWG
    >>> device = HDAWG("DEV1234", "localhost", name="optional_qcodes_name")

.. note::

    If the instrument you are using does not have a dedicated helper class yet
    you can use the generic one ``ZIDevice``.

Under the hood the helper class just creates a session (if necessary),
connects the device to it and returns the device class. It is therefore
identical to:

.. code-block:: python

    >>> from zhinst.qcodes import ZISession
    >>> session = ZISession("localhost")
    >>> device = session.connect_device("DEV1234")

To avoid creating a new session to data server every time when using these helper
classes, zhinst-qcodes by default only creates one session to a data server.
Meaning if one connects two devices to e.g. ``localhost`` they will share the
same session. For most use cases this is the desired behavior since it saves
resources and avoids unintended edge cases. In the rare cases where you need
to have a separate session for a device one can use the ``new_session`` flag.

If necessary (e.g. for polling data) on can access the underlying session object
through the ``session`` attribute.

.. code-block:: python

    >>> from zhinst.qcodes import HDAWG
    >>> device = HDAWG("DEV1234", "localhost", name="optional_qcodes_name")
    >>> data = device.session.poll(1)

Node Tree
---------

All settings and data in LabOne® are organized by the Data Server in a file-system-like
hierarchical structure called the node tree. zhinst-qcodes implements the node tree in
the by QCoDeS provided nested dictionary like structure. All leaf nodes are
``qcodes.instrument.parameter.Parameter`` nested in
``qcodes.instrument.baseInstrumentChannel`` s. Please refer to the
`QCoDeS Documentation <https://qcodes.github.io/Qcodes//>`_ for a detailed
explanation of Parameter work in QCoDeS.

.. code-block:: python

    >>> device.session.debug.level()
    'status'

So what did that code do?

1. The ``session`` represents the session to the data server and therefor gives access to its nodes (``/zi/*`` in ziPython).
2. One of these nodes is ``zi/debug/level``. zhinst-qcodes allows it to access that node by attributes.
3. To get the current value of the node simply make a call operation.

Changing the value of a node can be done in a similar way. Simply add the value
to the call operation.

.. code-block:: python

    >>> session.debug.level('warning')
    >>> session.debug.level()
    'warning'

LabOne® modules
---------------

In addition to the usual API commands available for instrument configuration and data
retrieval the LabOne® API also provides a number of so-called *modules*: high-level
interfaces that perform common tasks such as sweeping data or performing FFTs.
(See the
`LabOne Programming Manual <https://docs.zhinst.com/labone_programming_manual/introduction_labone_modules.html>`_
For a complete documentation of all modules available)

In zhinst-qcodes these modules can be accessed through the ``session``. Similar to the
devices each module can be controlled through a node tree. Some of the modules have
toolkit specific functionalities (e.g. reading the acquired data automatically).
To see an overview of the module specific functionalities take a look at the dedicated
examples.

.. note::

    The underlying LabOne® module (zhinst.ziPython object) can be accessed with the
    ``raw_module`` property

.. code-block:: python

    >>> daq_module = device.session.modules.daq
    >>> daq_module.grid.mode()
    4
    >>> daq_module.raw_module
    <zhinst.ziPython.DataAcquisitionModule at 0x10edc5630>

Please take a look at the examples in the
`zhinst-toolkit examples <https://docs.zhinst.com/zhinst-toolkit/en/latest/examples/index.html>`_
to see some of the modules in action.
