# zhinst-qcodes Changelog

## Version 0.3.5
* Fix Display name for the commandtable node. (`commandtablenode` -> `commandtable`)
* Fix Display name for the awg node. (`awgcore` -> `awg`)

## Version 0.3.4
* Add SHFQC device-utils and toolkit functionalities.
## Version 0.3.3
* Adapt to toolkit 0.3.2
* Make device class stubs derivable. This enables the user to directly derive
  from the exposed classes.
* Fixed [#31](https://github.com/zhinst/zhinst-qcodes/issues/31).

## Version 0.3.2
* Adapt to toolkit 0.3.1

## Version 0.3.1
* Outsource device class mapping into zhinst.qcodes.driver.devices
  (This enables the user to derive from the device classes easily the same
  way as in toolkit.)
## Version 0.3
* **redesign and complete refactoring of zhinst-qcodes**
  * lazy node tree to improve setup times
  * switch to session based approach (no longer device based)
  * command table handling improved
  * waveform handling improved
  * removed automated sequencer code generation
  * added LabOne modules

## Version 0.2.2
* Add SHFSG driver
* Support both HDAWG8 and HDAWG4

## Version 0.2.0
* Append a trailing underscore to nodes that equal to reserved keywords in Python to make them available in the nodetree.
* Adapt instrument drivers to [zhinst-toolkit](https://docs.zhinst.com/zhinst-toolkit/en/latest/changelog/index.html#version-0-1-2) release 0.2.0
* Add SHFQA driver
* Add PQSC driver

## Version 0.1.3
* Add complex validator for device streaming node `DEMODS/n/SAMPLE`

## Version 0.1.2
* Snapshot only parameters marked as 'Setting'
* Fix readout channel assignment in UHFQA driver

## Version 0.1.1
* initial release

