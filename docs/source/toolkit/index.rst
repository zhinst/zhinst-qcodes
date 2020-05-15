QCoDeS Drivers and :mod:`zhinst-toolkit`
========================================

The *Zurich Instruments* drivers for *QCoDeS* are based on the *Zurich 
Instruments Toolkit*. The Python package :mod:`zhinst-toolkit` is an extension 
of the *LabOne* Python API :mod:`ziPython`. The :mod:`zhinst-toolkit` allows for 
easier and more intuitive control of Zurich Instruments devices. 

Functionally, the instrument drivers for *QCoDeS* work in the same way as the 
drivers available in the :mod:`zhinst-toolkit`. However, they implement the 
instrument drivers, their submodules and parameters into the *QCoDeS* 
measurement framework by subclassing or wrapping elements from *QCoDeS*. Those 
include the *QCoDeS* classes 

* :class:`qcodes.instrument.base.Instrument`:
    for instrument drivers, e.g. the *zhinst.qcodes.HDAWG*
* :class:`qcodes.instrument.channel.InstrumentChannel`: 
    for submodules, i.e. nodes in the device's nodetree structure or 
    device-specific modules such as *AWG Cores*, *Readout Channels*, 
    *Data Aqcuisition Modules*, *Sweeper Module*  
* :class:`qcodes.instrument.parameter.Parameter`: 
    for device parameters that mostly correspond directly to device settings, 
    using the *LabOne* Python API they would be accessed with a unique node 
    path, e.g. *'dev1234/sigouts/0/enable'*

