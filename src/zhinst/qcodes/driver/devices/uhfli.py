""" Autogenerated module for the UHFLI QCodes driver. """
from typing import List, Union
from zhinst.toolkit import CommandTable, Waveforms
from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.qcodes_adaptions import ZINode, ZIChannelList


class CommandTableNode(ZINode):
    """CommandTable node.

    This class implements the basic functionality of the command table allowing
    the user to load and upload their own command table.

    A dedicated class called ``CommandTable`` exists that is the prefered way
    to create a valid command table. For more information about the
    ``CommandTable`` refer to the corresponding example or the documentation
    of that class directly.

    Args:
        root: Node used for the upload of the command table
        tree: Tree (node path as tuple) of the current node
        device_type: Device type.
    """

    def __init__(self, parent, tk_object, snapshot_cache=None, zi_node=None):
        ZINode.__init__(
            self,
            parent,
            f"commandtablenode",
            snapshot_cache=snapshot_cache,
            zi_node=zi_node,
        )
        self._tk_object = tk_object

    def check_status(self) -> bool:
        """Check status of the command table.

        Returns:
            Flag if a valid command table is loaded into the device.

        Raises:
            RuntimeError: If the command table upload into the device failed.
        """
        return self._tk_object.check_status()

    def load_validation_schema(self) -> dict:
        """Load device command table validation schema.

        Returns:
            JSON validation schema for the device command tables.
        """
        return self._tk_object.load_validation_schema()

    def upload_to_device(
        self, ct: Union[CommandTable, str, dict], *, validate: bool = True
    ) -> None:
        """Upload command table into the device.

        The command table can either be specified through the dedicated
        ``CommandTable`` class or in a raw format, meaning a json string or json
        dict. In the case of a json string or dict the command table is
        validated by default against the schema provided by the device.

        Args:
            ct: Command table.
            validate: Flag if the command table should be validated. (Only
                applies if the command table is passed as a raw json string or
                json dict)

        Raises:
            RuntimeError: If the command table upload into the device failed.
            zhinst.toolkit.exceptions.ValidationError: Incorrect schema.
        """
        return self._tk_object.upload_to_device(ct=ct, validate=validate)

    def load_from_device(self) -> CommandTable:
        """Load command table from the device.

        Returns:
            command table.
        """
        return self._tk_object.load_from_device()


class AWG(ZINode):
    """AWG node.

    This class implements the basic functionality for the device specific
    arbitrary waveform generator.
    Besides the upload/compilation of sequences it offers the upload of
    waveforms and command tables.

    Args:
        root: Root of the nodetree
        tree: Tree (node path as tuple) of the current node
        awg_module: Instance of the AWG Module
        daq_server: Instance of the ziDAQServer
        serial: Serial of the device.
        index: Index of the coresponding awg channel
        device_type: Device type
    """

    def __init__(self, parent, tk_object, index, snapshot_cache=None, zi_node=None):
        ZINode.__init__(
            self, parent, f"awg_{index}", snapshot_cache=snapshot_cache, zi_node=zi_node
        )
        self._tk_object = tk_object

        if self._tk_object.commandtable:

            self.add_submodule(
                "commandtable",
                CommandTableNode(
                    self,
                    self._tk_object.commandtable,
                    zi_node=self._tk_object.commandtable.node_info.path,
                    snapshot_cache=self._snapshot_cache,
                ),
            )

    def enable_sequencer(self, *, single: bool) -> None:
        """Starts the sequencer of a specific channel.

        Waits until the sequencer is enabled.

        Args:
            single: Flag if the sequencer should be disabled after finishing
            execution.
        """
        return self._tk_object.enable_sequencer(single=single)

    def wait_done(self, *, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the AWG is finished.

        Args:
            timeout: The maximum waiting time in seconds for the generator
                (default: 10).
            sleep_time: Time in seconds to wait between requesting generator
                state

        Raises:
            RuntimeError: If continuous mode is enabled
            TimeoutError: If the sequencer program did not finish within
                the specified timeout time
        """
        return self._tk_object.wait_done(timeout=timeout, sleep_time=sleep_time)

    def load_sequencer_program(
        self, sequencer_program: str, *, timeout: float = 100.0
    ) -> None:
        """Compiles the current SequenceProgram on the AWG Core.

        Args:
            sequencer_program: Sequencer program to be uploaded
            timeout: Maximum time to wait for the compilation on the device in
                seconds.

        Raises:
            TimeoutError: If the upload or compilation times out.
            RuntimeError: If the upload or compilation failed.
        """
        return self._tk_object.load_sequencer_program(
            sequencer_program=sequencer_program, timeout=timeout
        )

    def write_to_waveform_memory(
        self, waveforms: Waveforms, indexes: list = None
    ) -> None:
        """Writes waveforms to the waveform memory.

        The waveforms must already be assigned in the sequencer programm.

        Args:
            waveforms: Waveforms that should be uploaded.

        Raises:
            IndexError: The index of a waveform exeeds the one on the device
            RuntimeError: One of the waveforms index points to a filler(placeholder)
        """
        return self._tk_object.write_to_waveform_memory(
            waveforms=waveforms, indexes=indexes
        )

    def read_from_waveform_memory(self, indexes: List[int] = None) -> Waveforms:
        """Read waveforms to the waveform memory.

        Args:
            indexes: List of waveform indexes to read from the device. If not
                specfied all assigned waveforms will be downloaded.

        Returns:
            Mutuable mapping of the downloaded waveforms.
        """
        return self._tk_object.read_from_waveform_memory(indexes=indexes)


class UHFLI(ZIBaseInstrument):
    """QCodes driver for the Zurich Instruments UHFLI."""

    def _init_additional_nodes(self):
        """init class specific modules and paramaters."""

        if self._tk_object.awgs:

            channel_list = ZIChannelList(
                self,
                "awgs",
                AWG,
                zi_node=self._tk_object.awgs.node_info.path,
                snapshot_cache=self._snapshot_cache,
            )
            for i, x in enumerate(self._tk_object.awgs):
                channel_list.append(
                    AWG(
                        self,
                        x,
                        i,
                        zi_node=self._tk_object.awgs[i].node_info.path,
                        snapshot_cache=self._snapshot_cache,
                    )
                )
            # channel_list.lock()
            self.add_submodule("awgs", channel_list)
