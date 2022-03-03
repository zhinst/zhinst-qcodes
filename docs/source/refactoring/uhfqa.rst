Renaming for UHFQA
===================

.. note::

    The automatic sequencer code generation was removed since it was unstable
    and did not bring the expected user experience. Instead one can upload
    sequencer programs directly with uhfqa.awgs[n].load_sequencer_program
    and waveforms through uhfqa.awgs[n].write_to_waveform_memory.
    Please refer to the zhinst-toolkit documentation for an in-depth explanation.

.. note::

    The integration of modules has been refactored. The modules are now
    independent of the devices. For the UHFLI this means scope usage now
    requires to access the modules through the session. (session.modules.scope)

Node Renaming
--------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - uhfqa.crosstalk_matrix
     - uhfqa.qas[0].crosstalk_matrix
   * - uhfqa.result_source
     - uhfaq.qas[0].result.source
   * - uhfqa.integration_time
     - uhfqa.integration_length (conert time to samples manually)
   * - uhfqa.integration_length
     - uhfaq.qas[0].integration.length
   * - uhfqa.averaging_mode
     - uhfaq.qas[0].result.mode
   * - uhfqa.qa_delay
     - uhfaq.qas[0].adjusted_delay
   * - uhfqa.ref_clock
     - uhfqa.system.extclk
   * - uhfqa.scope.single
     - uhfqa.scopes[0].single
   * - uhfqa.scope.length
     - uhfqa.scopes[0].length
   * - uhfqa.scope.trigger_source
     - uhfqa.scopes[0].trigchannel
   * - uhfqa.scope.trigger_level
     - uhfqa.scopes[0].triglevel
   * - uhfqa.scope.trigger_enable
     - uhfqa.scopes[0].trigenable
   * - uhfqa.scope.trigger_reference
     - uhfqa.scopes[0].trigreference
   * - uhfqa.scope.trigger_holdoff
     - uhfqa.scopes[0].trigholdoff
   * - uhfqa.awgs[n].output1
     - uhfqa.sigouts[0].on
   * - uhfqa.awgs[n].output2
     - uhfqa.sigouts[1].on
   * - uhfqa.awgs[n].gain1
     - uhfqa.awgs[n].outputs[0].amplitude
   * - uhfqa.awgs[n].gain2
     - uhfqa.awgs[n].outputs[0].amplitude
   * - uhfqa.awgs[n].single
     - uhfqa.awgs[n].single



Function Renaming
-----------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - uhfqa.arm
     - **Removed**
   * - uhfqa.enable_readout_channels
     - **Removed**
   * - uhfqa.disable_readout_channels
     - **Removed**
   * - uhfqa.enable_qccs_mode
     - uhfqa.enable_qccs_mode
   * - uhfqa.channels[n].enabled
     - **Removed**
   * - uhfqa.channels[n].enable
     - **Removed**
   * - uhfqa.channels[n].disable
     - **Removed**

