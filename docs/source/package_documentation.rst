Package Documentation
=====================

zhinst-qcodes exposes the following classes:

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ~zhinst.qcodes.session.ZISession
   ~zhinst.qcodes.device_creator.ZIDevice

``ZIDevice`` is also exposed as (for convenience):

* HDAWG
* HF2
* MFLI
* MFIA
* PQSC
* SHFQA
* SHFSG
* UHFLI
* UHFQA

In addition the following classes are imported from
`zhinst-toolkit <https://docs.zhinst.com/zhinst-toolkit/en/latest/package_documentation.html>`_:

* Waveforms
* CommandTable
* PollFlags
* AveragingMode
* SHFQAChannelMode

They all can be imported directly from zhinst-qcodes. For example importing the
Session class the following statement can be used:

.. code-block:: python

    >>> from zhinst.qcodes import ZISession, HDAWG

Full Package Documentation
---------------------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   zhinst.qcodes
