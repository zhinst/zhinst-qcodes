Refactoring
===========

The zhinst-qcodes package exists for several years and as grown a lot in that
time. More and more device where added and the expectations and stability request
got stronger and stronger. zhinst-qcodes is based on zhinst-toolkit a high level
driver on top of the native LabOne ziPython package. Meaning it shares the same
functionalities but also the same problems.

To just mention a few of them:

* Long setup times
* Missing nodes
* Slow response times
* ...

Since more and more people start using python to interface with our instruments
we decided that zhinst-toolkit should become the package that can be used by
all of our customers for all of our devices. So ensure long term stability and
also full feature support a complete redesign of the architecture was necessary.
The new zhinst-toolkit now offer full feature support for all our devices, is
stable, properly tested and actively maintained by the LabOne team at Zurich
Instruments.

zhinst-qcodes also benefits from the redesign since it is based on zhinst-toolkit
since the beginning. The benefits include low setup times and fast responses,
similar to the low level ziPython API. But these benefits also come with the
price of a severe api changes. The architecture and the way to use zhinst-qcodes
from a user perspective more or less completely changes. In the following we
will try to help with the transition to the new zhinst-qcodes driver. But we
know that a lot of feature have been removed in order to align with LabOne and
if you encounter any functionality no longer accessible feel free to contact
the Zurich Instruments support so we can help you out.

The biggest change is probably the starting point. Instead of creating instances
of the instruments directly the user now starts by creating a session to a
data server. Since that is the underlying architecture of LabOne as well ist
seamlessly integrates into the Zurich Instruments ecosystem.

.. code-block:: python

    >>> from zhinst.qcodes import ZISession
    >>> session = ZISession("localhost")

The individual device objects can be created from that session. Either by
accessing them directly, in case they are already connected, or by connecting
them.

.. code-block:: python

    >>> session.devices.visible()
    ['dev1234', 'dev5678']
    >>> session.devices.connected()
    ['dev1234']
    >>> session.devices['dev1234']
    <ZIBaseInstrument: zi_XXXX_dev1234>
    >>> session.connect_device('dev5678')
    <ZIBaseInstrument: zi_XXXX_dev5678>

Since all devices share the same session the resource consumption is kept to
a minimum. Of course one can create multiple data server sessions at once if
necessary.

The instrument classes behave similar to the one from the old toolkit. But now
they by default automatically expose **all** available nodes from the device.
Meaning if the firmware updates and provides new nodes, users can, without the
need of an update, also use these nodes in zhinst-qcodes immediately. The naming
of the nodes in zhinst-qcodes is identical to LabOne, making it easy to find the
correct nodes or applying examples form LabOne to QCoDeS.

Since the old zhinst-qcodes hardcoded the available nodes and also used custom
names for them code written for the old zhinst-qcodes will not work any longer,
at least not without replacing the node names. The list below lists all the old
node names and their correct successors.

zhinst-qcodes also forwards all helper functions from zhinst-toolkit. During the
refactoring the name of these functions where normalized and the content was
refactored. The list below lists all the old functions and their their correct
successors.

.. toctree::
   :maxdepth: 1
   :caption: Device specific changes:

   hdawg
   mfli
   pqsc
   shfqa
   shfsg
   uhfli
   uhfqa

Automatic sequencer code generation
------------------------------------

A big part of the old zhinst-qcodes/-toolkit was the automatic sequence and
waveform generation for a predefined set of applications. Although these predefined
sets may give a easy entry point they where not suited for real measurements.
We decided to remove these and instead offer an easy way of uploading sequencer
code, waveforms and command table instead. Check out the examples of LabOne and
zhinst-toolkit to see predefined sequencer code.
