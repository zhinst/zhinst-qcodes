"""Autogenerated module for the HDAWG QCodes driver."""
from typing import Any, Dict, List, Tuple, Union
from zhinst.toolkit import CommandTable, Waveforms, Sequence
from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.qcodes_adaptions import ZINode, ZIChannelList


class CommandTableNode(ZINode):
    """CommandTable node.

    This class implements the basic functionality of the command table allowing
    the user to load and upload their own command table.

    A dedicated class called ``CommandTable`` exists that is the preferred way
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
            "commandtable",
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

    def load_validation_schema(self) -> Dict[str, Any]:
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
        session: Underlying session.
        serial: Serial of the device.
        index: Index of the corresponding awg channel
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

    def compile_sequencer_program(
        self, sequencer_program: Union[str, Sequence], **kwargs: Union[str, int]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Compiles a sequencer program for the sepcific device.

        Args:
            sequencer_program: The sequencer program to compile.

        Keyword Args:
            samplerate: Target sample rate of the sequencer. Only allowed/
                necessary for HDAWG devices. Must correspond to the samplerate
                used by the device (device.system.clocks.sampleclock.freq()).
                If not specified the function will get the value itself from
                the device. It is recommended passing the samplerate if more
                than one sequencer code is uploaded in a row to speed up the
                execution time.
            wavepath: path to directory with waveforms. Defaults to path used
                by LabOne UI or AWG Module.
            waveforms: waveform CSV files separated by ';'
            output: name of embedded ELF filename.

        Returns:
            elf: Binary ELF data for sequencer.
            extra: Extra dictionary with compiler output.

        Examples:
            >>> elf, compile_info = device.awgs[0].compile_sequencer_program(seqc)
            >>> device.awgs[0].elf.data(elf)
            >>> device.awgs[0].ready.wait_for_state_change(1)
            >>> device.awgs[0].enable(True)

        Raises:
            RuntimeError: `sequencer_program` is empty.
            RuntimeError: If the compilation failed.

        .. versionadded:: 0.4.1
        """
        return self._tk_object.compile_sequencer_program(
            sequencer_program=sequencer_program, kwargs=kwargs
        )

    def load_sequencer_program(
        self, sequencer_program: Union[str, Sequence], **kwargs: Union[str, int]
    ) -> Dict[str, Any]:
        """Compiles the given sequencer program on the AWG Core.

        Warning:
            After uploading the sequencer program one needs to wait before for
            the awg core to become ready before it can be enabled.
            The awg core indicates the ready state through its `ready` node.
            (device.awgs[0].ready() == True)

        Args:
            sequencer_program: Sequencer program to be uploaded.

        Keyword Args:
            samplerate: Target sample rate of the sequencer. Only allowed/
                necessary for HDAWG devices. Must correspond to the samplerate
                used by the device (device.system.clocks.sampleclock.freq()).
                If not specified the function will get the value itself from
                the device. It is recommended passing the samplerate if more
                than one sequencer code is uploaded in a row to speed up the
                execution time.
            wavepath: path to directory with waveforms. Defaults to path used
                by LabOne UI or AWG Module.
            waveforms: waveform CSV files separated by ';'
            output: name of embedded ELF filename.

        Examples:
            >>> compile_info = device.awgs[0].load_sequencer_program(seqc)
            >>> device.awgs[0].ready.wait_for_state_change(1)
            >>> device.awgs[0].enable(True)

        Raises:
            RuntimeError: `sequencer_program` is empty.
            RuntimeError: If the upload or compilation failed.

        .. versionadded:: 0.3.4

            `sequencer_program` does not accept empty strings

        .. versionadded:: 0.4.1

            Use offline compiler instead of AWG module to compile the sequencer
            program. This speeds of the compilation and also enables parallel
            compilation/upload.
        """
        return self._tk_object.load_sequencer_program(
            sequencer_program=sequencer_program, kwargs=kwargs
        )

    def write_to_waveform_memory(
        self, waveforms: Waveforms, indexes: list = None, validate: bool = True
    ) -> None:
        """Writes waveforms to the waveform memory.

        The waveforms must already be assigned in the sequencer program.

        Args:
            waveforms: Waveforms that should be uploaded.
            indexes: Specify a list of indexes that should be uploaded. If
                nothing is specified all available indexes in waveforms will
                be uploaded. (default = None)
            validate: Enable sanity check preformed by toolkit, based on the
                waveform descriptors on the device. Can be disabled for e.g.
                speed optimizations. Does not affect the checks happen in LabOne
                and or the firmware. (default = True)

        Raises:
            IndexError: The index of a waveform exceeds the one on the device
                and `validate` is True.
            RuntimeError: One of the waveforms index points to a
                filler(placeholder) and `validate` is True.
        """
        return self._tk_object.write_to_waveform_memory(
            waveforms=waveforms, indexes=indexes, validate=validate
        )

    def read_from_waveform_memory(self, indexes: List[int] = None) -> Waveforms:
        """Read waveforms to the waveform memory.

        Args:
            indexes: List of waveform indexes to read from the device. If not
                specified all assigned waveforms will be downloaded.

        Returns:
            Waveform object with the downloaded waveforms.
        """
        return self._tk_object.read_from_waveform_memory(indexes=indexes)


class HDAWG(ZIBaseInstrument):
    """QCodes driver for the Zurich Instruments HDAWG."""

    def _init_additional_nodes(self):
        """Init class specific modules and parameters."""
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

    def enable_qccs_mode(self) -> None:
        """Configure the instrument to work with PQSC.

        This method sets the reference clock source to
        connect the instrument to the PQSC.

        Info:
            Use ``factory_reset`` to reset the changes if necessary
        """
        return self._tk_object.enable_qccs_mode()
