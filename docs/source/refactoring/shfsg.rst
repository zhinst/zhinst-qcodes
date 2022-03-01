Renaming for SHFSG
===================

.. note::

    The automatic sequencer code generation was removed since it was unstable
    and did not bring the expected user experience. Instead one can upload
    sequencer programs directly with shfsg.sgchannels[n].awg.load_sequencer_program
    and waveforms through shfsg.sgchannels[n].awg.write_to_waveform_memory.
    Please refer to the zhinst-toolkit documentation for an in-depth explanation.

Node Renaming
--------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - shfsg.ref_clock
     - shfsg.system.clocks.referenceclock.in\_.source
   * - shfsg.ref_clock_status
     - shfsg.system.clocks.referenceclock.in\_.status
   * - shfsg.sgchannels[n].output
     - shfsg.sgchannels[n].output.on
   * - shfsg.sgchannels[n].output_range
     - shfsg.sgchannels[n].output.range
   * - shfsg.sgchannels[n].rf_center_freq
     - shfsg.synthesizers[n/2].centerfreq
   * - shfsg.sgchannels[n].rf_or_lf_path
     - shfsg.sgchannels[n].output.rflfpath
   * - shfsg.sgchannels[n].awg.output1
     - shfsg.sgchannels[n].awg.outputs[0].enable
   * - shfsg.sgchannels[n].awg.output2
     - shfsg.sgchannels[n].awgoutputs[1].enable
   * - shfsg.sgchannels[n].awg.modulation_freq
     - shfsg.sgchannels[n].oscs[0].freq
   * - shfsg.sgchannels[n].awg.modulation_phase_shift
     - shfsg.sgchannels[n].sines[0].phaseshift
   * - shfsg.sgchannels[n].awg.gain00
     - shfsg.sgchannels[n].awg.outputs[0].gains[0].value
   * - shfsg.sgchannels[n].awg.gain01
     - shfsg.sgchannels[n].awg.outputs[0].gains[1].value
   * - shfsg.sgchannels[n].awg.gain10
     - shfsg.sgchannels[n].awg.outputs[1].gains[0].value
   * - shfsg.sgchannels[n].awg.gain11
     - shfsg.sgchannels[n].awg.outputs[1].gains[1].value
   * - shfsg.sgchannels[n].awg.single
     - shfsg.sgchannels[n].awg.single
   * - shfsg.sgchannels[n].awg.digital_trigger1_source
     - shfsg.sgchannels[n].awg.auxtriggers[0].channel
   * - shfsg.sgchannels[n].awg.digital_trigger2_source
     - shfsg.sgchannels[n].awg.auxtriggers[1].channel
   * - shfsg.sgchannels[n].awg.digital_trigger1_slope
     - shfsg.sgchannels[n].awg.auxtriggers[0].slope
   * - shfsg.sgchannels[n].awg.digital_trigger2_slope
     - shfsg.sgchannels[n].awg.auxtriggers[0].slope
   * - shfsg.sgchannels[n].awg.osc_select
     - shfsg.sgchannels[n].sines[0].oscselect
   * - shfsg.sgchannels[n].sine.osc_select
     - shfsg.sgchannels[n].sines[0].oscselect
   * - shfsg.sgchannels[n].sine.harmonic
     - shfsg.sgchannels[n].sines[0].harmonic
   * - shfsg.sgchannels[n].sine.phaseshift
     - shfsg.sgchannels[n].sines[0].phaseshift
   * - shfsg.sgchannels[n].sine.i_enable
     - shfsg.sgchannels[n].sines[0].i.enable
   * - shfsg.sgchannels[n].sine.i_sin
     - shfsg.sgchannels[n].sines[0].i.sin.amplitude
   * - shfsg.sgchannels[n].sine.i_cos
     - shfsg.sgchannels[n].sines[0].i.cos.amplitude
   * - shfsg.sgchannels[n].sine.q_enable
     - shfsg.sgchannels[n].sines[0].q.enable
   * - shfsg.sgchannels[n].sine.q_sin
     - shfsg.sgchannels[n].sines[0].q.sin.amplitude
   * - shfsg.sgchannels[n].sine.q_cos
     - shfsg.sgchannels[n].sines[0].q.cos.amplitude

Function Renaming
-----------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - shfsg.check_ref_clock
     - **deleted**
   * - shfsg.enable_qccs_mode
     - **deleted**
   * - shfsg.enable_manual_mode
     - **deleted**
