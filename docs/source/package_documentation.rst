Package Documentation
=====================

zhinst-qcodes exposes the following classes:

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ~zhinst.qcodes.session.ZISession
   ~zhinst.qcodes.device_creator.HDAWG
   ~zhinst.qcodes.device_creator.MFLI
   ~zhinst.qcodes.device_creator.MFIA
   ~zhinst.qcodes.device_creator.PQSC
   ~zhinst.qcodes.device_creator.SHFQA
   ~zhinst.qcodes.device_creator.SHFQC
   ~zhinst.qcodes.device_creator.SHFSG
   ~zhinst.qcodes.device_creator.UHFLI
   ~zhinst.qcodes.device_creator.UHFQA
   ~zhinst.qcodes.device_creator.HF2
   ~zhinst.qcodes.device_creator.ZIDevice
   ~zhinst.qcodes.device_creator.SHFLI
   ~zhinst.qcodes.device_creator.GHFLI

In addition the following classes are imported from
`zhinst-toolkit <https://docs.zhinst.com/zhinst-toolkit/en/latest/package_documentation.html>`_:

* Waveforms
* CommandTable
* Sequence
* PollFlags
* AveragingMode
* SHFQAChannelMode

They all can be imported directly from zhinst-qcodes. For example importing the
HDAWG device class the following statement can be used:

.. code-block:: python

    >>> from zhinst.qcodes import HDAWG

Full Package Documentation
---------------------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   zhinst.qcodes
