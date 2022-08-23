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

Session To The Data Server
---------------------------

Zurich Instruments devices use a server-based connectivity methodology. Server-based
means that all communication between the user and the instrument takes place via a
computer program called a server, the Data Server. The Data Server recognizes available
instruments and manages all communication between the instrument and the host computer
on one side, and communication to all the connected clients on the other side.
(see `Architecture <https://docs.zhinst.com/labone_programming_manual/introduction.html#pm.intro.architecture>`_
in the LabOne Programming Manual)

The logical entry point into zhinst-qcodes would therefor be a API client session
to a data server.

However since QCoDeS by design normally creates device objects directly
zhinst-qcodes exposes the device class for each instrument type directly without
the need to create a session first.

.. code-block:: python

    >>> from zhinst.qcodes import HDAWG
    >>> device = HDAWG("DEV1234", "localhost", name="optional_qcodes_name")

.. note::

    If the instrument you are using does not have a dedicated helper class yet
    you can use the generic one ``ZIDevice``.

Under the hood the helper class just creates a session, connects the device to
it and returns the device class. It is therefore identical to:

.. code-block:: python

    >>> from zhinst.qcodes import ZISession
    >>> session = ZISession("localhost")
    >>> device = session.connect_device("DEV1234")

To avoid creating a new session to data server every time when using these helper
classes, zhinst-qcodes by default only creates one session to a data server.
Meaning if one connects two devices to e.g. ``localhost`` they will share the
same session. For most use cases this is the desired behavior since it saves
resources and avoids unintended edge cases. In the rare cases where one needs
to have a separate session for a device one can use the ``new_session`` flag.
But it is preferred to work in such cases with the session directly and not use
the helper classes, since it is simpler to understand and recreate.

The created device object holds all device specific nodes and depending on the device
type also implements additional functionalities (e.g. exposes the
``zhinst.utils`` functions).

.. code-block:: python

    >>> from zhinst.qcodes import MFLI
    >>> device = MFLI("DEV1234", "localhost")
    >>> device.demods[0].freq()
    10e6

The drivers are based on `zhinst-toolkit <https://github.com/zhinst/zhinst-toolkit>`_,
a generic high level python driver for LabOne. Except for the node tree which in
case for the zhinst-qcodes driver is implemented with the native QCoDeS
Parameters, both driver behave the same. To be even more precise the
zhinst-qcodes forwards all calls (functions, parameters ...) to zhinst-toolkit
and has no logic builtin what so ever.

For the device drivers this means that some device may have additional functionality
provided by zhinst-toolkit. zhinst-qcodes forwards these functionalities.
Please take a look at the examples in the
`zhinst-toolkit examples <https://docs.zhinst.com/zhinst-toolkit/en/latest/examples/index.html>`_
to see a list of all available functions. As already mentioned they can be used
with the exact same syntax, which also is the case for all the examples from
zhinst-toolkit (just replace the imports from zhinst-toolkit with zhinst-qcodes).

Node Tree
---------

All settings and data in LabOne® are organized by the Data Server in a file-system-like
hierarchical structure called the node tree. zhinst-qcodes implements the node tree in
the by QCoDeS provided nested dictionary like structure. All leaf nodes are
``qcodes.instrument.parameter.Parameter`` nested in
``qcodes.instrument.BaseInstrumentChannel`` s. Please refer to the
`QCoDeS Documentation <https://qcodes.github.io/Qcodes//>`_ for a detailed
explanation of how work Parameter in QCoDeS.

.. code-block:: python

    >>> device.session.debug.level()
    'status'

So what did that code do?

1. The ``session`` represents the session to the data server and therefor gives access to its nodes (``/zi/*`` in the LabOne API.).
2. One of these nodes is ``zi/debug/level``. zhinst-qcodes allows it to access that node by attributes.
3. To get the current value of the node simply make a call operation.

Changing the value of a node can be done in a similar way. Simply add the value
to the call operation.

.. code-block:: python

    >>> device.session.debug.level('warning')
    >>> device.session.debug.level()
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

    The underlying LabOne® module (zhinst.core object) can be accessed with the
    ``raw_module`` property

.. code-block:: python

    >>> daq_module = device.session.modules.daq
    >>> daq_module.grid.mode()
    4
    >>> daq_module.raw_module
    <zhinst.core.DataAcquisitionModule at 0x10edc5630>

Please take a look at the examples in the
`zhinst-toolkit examples <https://docs.zhinst.com/zhinst-toolkit/en/latest/examples/index.html>`_
to see some of the modules in action.
