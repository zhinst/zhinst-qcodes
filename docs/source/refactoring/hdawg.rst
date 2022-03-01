Renaming for HDAWG
===================

.. note::

    The automatic sequencer code generation was removed since it was unstable
    and did not bring the expected user experience. Instead one can upload
    sequencer programs directly with hdawg.awgs[n].load_sequencer_program
    and waveforms through hdawg.awgs[n].write_to_waveform_memory.
    Please refer to the zhinst-toolkit documentation for an in-depth explanation.

Node Renaming
--------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - hdawg.ref_clock
     - hdawg.system.clocks.referenceclock.in\_.source
   * - hdawg.ref_clock_status
     - hdawg.system.clocks.referenceclock.in\_.status
   * - hdawg.awgs[n].output1
     - hdawg.sigouts[2*n].on
   * - hdawg.awgs[n].output2
     - hdawg.sigouts[2*n+1].on
   * - hdawg.awgs[n].gain1
     - hdawg.awgs[n].outputs[0].gains[0].value
   * - hdawg.awgs[n].gain2
     - hdawg.awgs[n].outputs[1].gains[1].value
   * - hdawg.awgs[n].modulation_phase_shift
     - hdawg.sines[2*n+1].phaseshift
   * - hdawg.awgs[n].modulation_freq
     - hdawg.oscs[n].freq (hdawg.oscs[4*n].freq with MF option)
   * - hdawg.awgs[n].single
     - hdawg.awgs[n].single
   * - hdawg.awgs[n].zsync_register_mask
     - hdawg.awgs[n].zsync.register.mask
   * - hdawg.awgs[n].zsync_register_shift
     - hdawg.awgs[n].zsync.register.shift
   * - hdawg.awgs[n].zsync_register_offset
     - hdawg.awgs[n].zsync.register.offset
   * - hdawg.awgs[n].zsync_decoder_mask
     - hdawg.awgs[n].zsync.decoder.mask
   * - hdawg.awgs[n].zsync_decoder_shift
     - hdawg.awgs[n].zsync.decoder.shift
   * - hdawg.awgs[n].zsync_decoder_offset
     - hdawg.awgs[n].zsync.decoder.offset

Function Renaming
------------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - hdawg.enable_manual_mode
     - **deleted**
