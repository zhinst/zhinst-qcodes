Renaming for SHFQA
===================

.. note::

    The automatic sequencer code generation was removed since it was unstable
    and did not bring the expected user experience. Instead one can upload
    sequencer programs directly with shfqa.qachannels[n].generator.load_sequencer_program
    and waveforms through shfqa.qachannels[n].generator.write_to_waveform_memory.
    Please refer to the zhinst-toolkit documentation for an in-depth explanation.

.. note::

    The integration of modules has been refactored. The modules are now
    independent of the devices. For the SHFQA this means sweeper usage now
    requires to access the modules through the session. (session.modules.shfqa_sweeper)

Node Renaming
--------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - shfqa.sw_trigger
     - shfqa.system.swtriggers.0.single
   * - shfqa.ref_clock
     - shfqa.system.clocks.referenceclock.in\_.source
   * - shfqa.ref_clock_actual
     - shfqa.system.clocks.referenceclock.in\_.sourceactual
   * - shfqa.ref_clock_status
     - shfqa.system.clocks.referenceclock.in\_.status
   * - shfqa.qachannels[n].input
     - shfqa.qachannels[n].input.on
   * - shfqa.qachannels[n].input_range
     - shfqa.qachannels[n].input.range
   * - shfqa.qachannels[n].output
     - shfqa.qachannels[n].output.on
   * - shfqa.qachannels[n].output_range
     - shfqa.qachannels[n].output.range
   * - shfqa.qachannels[n].center_freq
     - shfqa.qachannels[n].centerfreq
   * - shfqa.qachannels[n].mode
     - shfqa.qachannels[n].mode
   * - shfqa.qachannels[n].generator.dig_trigger1_source
     - shfqa.qachannels[n].generator.auxtriggers[0].channel
   * - shfqa.qachannels[n].generator.dig_trigger2_source
     - shfqa.qachannels[n].generator.auxtriggers[1].channel
   * - shfqa.qachannels[n].generator.playback_delay
     - shfqa.qachannels[n].generator.delay
   * - shfqa.qachannels[n].generator.single
     - shfqa.qachannels[n].generator.single
   * - shfqa.qachannels[n].readout.integration_length
     - shfqa.qachannels[n].readout.integration.length
   * - shfqa.qachannels[n].readout.integration_delay
     - shfqa.qachannels[n].readout.integration.delay
   * - shfqa.qachannels[n].readout.result_source
     - shfqa.qachannels[n].readout.result.source
   * - shfqa.qachannels[n].readout.integration[m].threshold
     - shfqa.qachannels[n].readout.discriminators[m].threshold
   * - shfqa.qachannels[n].readout.integration[m].result
     - shfqa.qachannels[n].readout.result.data[m].wave
   * - shfqa.qachannels[n].readout.integration[m].weights
     - shfqa.qachannels[n].readout.integration.weights[m].wave
   * - shfqa.qachannels[n].sweeper.oscillator_gain
     - shfqa.qachannels[n].oscs[0].gain
   * - shfqa.qachannels[n].sweeper.oscillator_freq
     - shfqa.qachannels[n].oscs[0].freq
   * - shfqa.qachannels[n].sweeper.integration_time
     - shfqa.qachannels[n].spectroscopy.length (time needs to be converted manualy to length)
   * - shfqa.qachannels[n].sweeper.integration_length
     - shfqa.qachannels[n].spectroscopy.length
   * - shfqa.qachannels[n].sweeper.integration_delay
     - shfqa.qachannels[n].spectroscopy.delay
   * - shfqa.qachannels[n].sweeper.trigger_source
     - shfqa.qachannels[n].spectroscopy.trigger.channel
   * - shfqa.scope.channel1-4
     - shfqa.scopes[0].channels[0-4].enable
   * - shfqa.scope.input_select1-4
     - shfqa.scopes[0].channels[0-4].inputselect
   * - shfqa.scope.trigger_source
     - shfqa.scopes[0].trigger.channel
   * - shfqa.scope.trigger_delay
     - shfqa.scopes[0].trigger.delay
   * - shfqa.scope.length
     - shfqa.scopes[0].length
   * - shfqa.scope.time
     - shfqa.scopes[0].time


Function Renaming
------------------

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - old
     - new
   * - shfqa.set_trigger_loopback
     - **deleted** (experimental)
   * - shfqa.clear_trigger_loopback
     - **deleted** (experimental)
   * - shfqa.check_ref_clock
     - **deleted**
   * - shfqa.allowed_sequences
     - **deleted** automatic sequencer code generation was removed
   * - shfqa.allowed_trigger_modes
     - **deleted** automatic sequencer code generation was removed
   * - shfqa.qachannels[0].generator.run
     - shfqa.qachannels[0].generator.enable_sequencer
   * - shfqa.qachannels[0].generator.stop
     - shfqa.qachannels[0].generator.enable(False)
   * - shfqa.qachannels[0].generator.wait_done
     - shfqa.qachannels[0].generator.wait_done
   * - shfqa.qachannels[0].readout.arm
     - shfqa.qachannels[0].readout.configure_result_logger
   * - shfqa.qachannels[0].readout.run
     - shfqa.qachannels[0].readout.run
   * - shfqa.qachannels[0].readout.stop
     - shfqa.qachannels[0].readout.stop
   * - shfqa.qachannels[0].readout.wait_done
     - shfqa.qachannels[0].readout.wait_done
   * - shfqa.qachannels[0].readout.read
     - shfqa.qachannels[0].readout.read
   * - shfqa.qachannels[0].readout.integration.set_int_weights
     - shfqa.qachannels[0].readout.write_integration_weights
   * - shfqa.scope.run
     - shfqa.scopes[0].run
   * - shfqa.scope.stop
     - shfqa.scopes[0].stop
   * - shfqa.scope.wait_done
     - shfqa.scopes[0].wait_done
   * - shfqa.scope.read
     - shfqa.scopes[0].read
   * - shfqa.scope.channels
     - **deleted** Set all channels individualy
   * - shfqa.scope.input_select
     - **deleted** Set all input select individualy
   * - shfqa.scope.segments
     - **deleted** shfqa.scopes[0].segments.enable & count
   * - shfqa.scope.averaging
     - **deleted** shfqa.scopes[0].averaging.enable & count
