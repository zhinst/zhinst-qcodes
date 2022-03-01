Renaming for UHFLI
===================

.. note::

    The automatic sequencer code generation was removed since it was unstable
    and did not bring the expected user experience. Instead one can upload
    sequencer programs directly with uhfli.awgs[n].load_sequencer_program
    and waveforms through uhfli.awgs[n].write_to_waveform_memory.
    Please refer to the zhinst-toolkit documentation for an in-depth explanation.

.. note::

    The integration of modules has been refactored. The modules are now
    independent of the devices. For the UHFLI this means sweeper usage now
    requires to access the modules through the session. (session.modules.sweeper)
