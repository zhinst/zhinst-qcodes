"""Autogenerate the QCoDeS drivers from toolkit and zhinst-core."""
from collections import namedtuple
import typing as t
import inspect
import re
import importlib
import jinja2
import isort
import black
import autoflake
import click
from pathlib import Path

from zhinst.toolkit.driver.devices.base import BaseInstrument
from zhinst.toolkit.driver.modules.base_module import BaseModule
from zhinst.toolkit.nodetree import Node, NodeTree
import conf

parameter_tuple = namedtuple("parameter", ["name", "is_node"])
submodule_tuple = namedtuple("submodule", ["subclass", "name", "is_list"])
function_tuple = namedtuple("function", ["name", "is_deprecated"])
class_tuple = namedtuple("toolkit_class", ["functions", "parameters", "sub_modules"])


def getPropertyInfo(
    name: str, property: object, class_type: object
) -> t.Union[parameter_tuple, submodule_tuple]:
    """Get all necessary information for a toolkit property.

    Args:
        name (str): Name of the property
        property (object): Class of the property
        class_type (object): Owner class of the property

    Returns:
        Union[parameter_tuple,submodule_tuple]
    """
    typehint = t.get_type_hints(property.fget)
    if "deprecated" in inspect.getsource(property.fget):
        # TODO decide if we should keep them or remove them?
        print(f"WARNING {name}: deprecated property -> ignored")
    elif "typing.Union" in str(typehint["return"]) or "typing.Sequence" in str(
        typehint["return"]
    ):
        try:
            item_class = typehint["return"].__args__[0]
            if "typing.Sequence" in str(item_class):
                return submodule_tuple(item_class.__args__[0], name, True)
            if issubclass(item_class, Node):
                # list of submodules
                return submodule_tuple(item_class, name, True)
        except Exception:
            raise Exception(
                f"{name} in {class_type} has a type hint list, "
                "but misses the item typehint"
            )
        if item_class.__name__ in ["str"]:
            return parameter_tuple(name, False)
        raise Exception(
            f"{name} in {class_type} has a type hint list, "
            f"but the item typehint is of {str(item_class)}."
            "only submodules are currently allowed."
        )
    elif hasattr(typehint["return"], "_name") and typehint["return"]._name == "List":
        return parameter_tuple(name, False)
    elif typehint["return"] == Node:
        return parameter_tuple(name, True)
    elif typehint["return"] == NodeTree:
        raise RuntimeError("Why would there be such thing?")
    elif (
        inspect.isclass(typehint["return"])
        and issubclass(typehint["return"], Node)
        or (
            "typing.Optional" in str(typehint["return"])
            and issubclass(typehint["return"].__args__[0], Node)
        )
    ):
        return submodule_tuple(typehint["return"], name, False)
    return parameter_tuple(name, False)


def getInfo(class_type: object, existing_names: list) -> t.Tuple[class_tuple, list]:
    """Get all necessary information for a toolkit class.

    Args:
        class_type (object) toolkit class
        existing_names (list) list of existing names for the QCoDeS class.

    Returns:
        class_tuple: functions,parameters,sub_modules
        list:        updated existing names
    """
    blacklist_names = []
    functions = []
    parameters = []
    sub_modules = []

    for name, attribute in vars(class_type).items():
        # ignore private/blacklisted and existing items
        if name.startswith("_") or name in blacklist_names or name in existing_names:
            continue
        if isinstance(attribute, property):
            property_info = getPropertyInfo(name, attribute, class_type)
            if isinstance(property_info, parameter_tuple):
                parameters.append(property_info)
            else:
                sub_modules.append(property_info)
        else:
            # function
            if not callable(attribute):
                raise RuntimeError("Unsupported class item")
            functions.append(
                function_tuple(name, "deprecated" in inspect.getsource(attribute))
            )
        existing_names.append(name)

    result_tuple = class_tuple(functions, parameters, sub_modules)

    # add base class info if it is inside toolkit
    blacklist_base = [
        Node,
        BaseInstrument,
        BaseModule,
    ]
    for base_class in class_type.__bases__:
        if (
            base_class not in blacklist_base
            and "zhinst.toolkit" in base_class.__module__
        ):
            base_info, existing_names = getInfo(base_class, existing_names)
            result_tuple = class_tuple(
                *list(
                    base_tuple + res_tuple
                    for base_tuple, res_tuple in zip(base_info, result_tuple)
                )
            )

    return result_tuple, existing_names


def generate_submodules_info(sub_modules: list, base_class: object) -> t.List[list]:
    """Gather information for the submodules.

    Args:
        sub_modules(list) list of classes that should be add as submodules.

    Returns:
        (list) infos for the parent class
        (list) newly generate class information
    """
    parent_info = []  # information for the parent class
    submodule_info = []  # information about the submodule classes
    for module, name, is_list in sub_modules:
        if name == "commandtable" and base_class.__name__ == "Generator":
            continue
        if "typing.Optional" in str(module):
            module = module.__args__[0]
        parent_info.append(
            {"name": name, "class_name": module.__name__, "is_list": is_list}
        )
        submodule_info += generate_qcodes_class_info(
            module,
            is_submodule=True,
            is_list_element=is_list,
        )
    return parent_info, submodule_info


def generate_parameter_info(parameters: list, class_type: object) -> list:
    """Gather information for the Qcodes parameter.

    Args:
        parameters (list): list of parameters that should be added.
        toolkit_class (object): toolkit class that the parameters belong to.

    Returns:
        (list) list dict with information for each parameter.
    """
    parameter_info = []
    has_node_param = False
    for parameter, is_node in parameters:
        has_node_param = True if has_node_param or is_node else False
        signature = inspect.signature(getattr(class_type, parameter).fget)
        try:
            return_annotation = signature.return_annotation.__name__
        except AttributeError:
            return_annotation = str(signature.return_annotation)
            return_annotation = return_annotation.replace("typing.", "t.")

        parameter_info.append(
            {
                "name": parameter,
                "is_node": is_node,
                "docstring": getattr(class_type, parameter).__doc__,
                "return_annotation": return_annotation,
            }
        )
    return parameter_info, has_node_param


def generate_functions_info(functions: list, toolkit_class: object) -> list:
    """Gather information for the functions.

    Args:
        functions (list): list of functions that should be added.
        toolkit_class (object): toolkit class that the functions belong to.

    Returns:
        (list) list dict with information for each function.
    """
    # Enums from toolkit should be exposed also in the QCoDeS driver
    enums = {
        "NodeDict": "zhinst.toolkit.nodetree.helper.NodeDict",
        "np.": "numpy.",
        "QuditSettings": "zhinst.utils.shfqa.multistate.QuditSettings",
        "SHFQAChannelMode": "zhinst.toolkit.interface.SHFQAChannelMode",
        "MappingMode": "zhinst.toolkit.interface.MappingMode",
        "TriggerImpedance": "zhinst.toolkit.interface.TriggerImpedance",
        "AveragingMode": "zhinst.toolkit.interface.AveragingMode",
        "Waveforms": "zhinst.toolkit.waveform.Waveforms",
        "CommandTable": "zhinst.toolkit.command_table.CommandTable",
        "Sequence": "zhinst.toolkit.sequence.Sequence",
        "Path": "pathlib.Path",
        '"DeviceType"': "ForwardRef('DeviceType')",
    }
    # regex to find deprecation decorator
    deprecated_regex = re.compile(r"(@depreca(.|\n)*?)\s*?(?:def|@)")

    functions_info = []
    for name, deprecated in functions:
        decorator = ""
        if deprecated:
            # copy deprecation decorator
            deprecation_deco = inspect.getsource(getattr(toolkit_class, name))
            decorator = deprecated_regex.search(deprecation_deco).group(1)
        docstring = getattr(toolkit_class, name).__doc__
        signature = inspect.signature(getattr(toolkit_class, name))
        signature_str = str(signature)
        is_node_doc = False
        # replace toolkit enum typehint with direct typehint
        for new, old in enums.items():
            signature_str = signature_str.replace(old, new)
            if new in signature_str:
                # search for enum typehint in function arguments
                regex_result = re.search(
                    f"<({new}.*?):.*?>",
                    signature_str,
                )
                if regex_result:
                    signature_str = signature_str.replace(
                        regex_result.group(0), regex_result.group(1)
                    )
                if new == "NodeDict":
                    is_node_doc = True

        # replace weird stuff
        for weird_stuff, replacement in conf.TYPE_HINT_REPLACEMENTS.items():
            signature_str = signature_str.replace(weird_stuff, replacement)

        call_parameter_str = []
        for param in signature.parameters:
            if param == "self":
                continue
            if param == "kwargs":
                call_parameter_str.append("**kwargs")
            elif param == "args":
                call_parameter_str.append("*args")
            else:
                call_parameter_str.append(f"{param}={param}")
        call_signature = ", ".join(call_parameter_str)

        functions_info.append(
            {
                "name": name,
                "decorator": decorator,
                "signature": signature_str,
                "docstring": docstring if docstring else "",
                "call_signature": call_signature,
                "return_annotation": str(signature.return_annotation)
                if signature.return_annotation
                else "",
                "is_node_dict": is_node_doc,
            }
        )
    return functions_info


def generate_qcodes_class_info(
    class_type: object,
    is_submodule: bool = False,
    is_list_element: bool = False,
):
    """Gather information for a qcodes class from a toolkit class.

    Args:
        class_type (object): toolkit class that should mimiced.
        is_submodule (bool): Flag if the class is a sub module of another
            toolkit class.
        is_list_element (bool): Flag if the class is instaciated in a list.

    Returns:
        (list) list of dicts with information for the class and its subclasses.
    """
    tk_class_info, _ = getInfo(class_type, [])
    submodule_info, gathered_info = generate_submodules_info(
        tk_class_info.sub_modules, class_type
    )
    parameter_info, has_node_param = generate_parameter_info(
        tk_class_info.parameters, class_type
    )
    function_info = generate_functions_info(tk_class_info.functions, class_type)

    display_name_replacements = {"CommandTableNode": "commandtable", "AWGCore": "awg"}

    gathered_info.append(
        {
            "name": class_type.__name__,
            "display_name": display_name_replacements.get(
                class_type.__name__, class_type.__name__.lower()
            ),
            "is_instrument_class": not is_submodule,
            "docstring": class_type.__doc__,
            "modules": submodule_info,
            "functions": function_info,
            "parameters": parameter_info,
            "has_node_param": has_node_param,
            "is_list": is_list_element,
        }
    )
    return gathered_info


def camel_to_snake(name: str) -> str:
    """Convert camelcase into snake case.

    Args:
        name  (str): name in camel case

    Returns:
        str: name in snake case
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def generate_qcodes_driver(
    toolkit_class: object,
    template_path: t.Union[str, Path] = conf.TEMPLATE_PATH,
    output_dir: t.Union[str, Path] = conf.OUTPUT_DIR_DEVICES_DRIVER,
) -> None:
    """Generates the Qcodes drivers for the toolkit instrument classes.

    Args:
        toolkit_class (object): toolkit instrument driver class
        template_path (str):  jinja template location (default = "templates/")
        output_dir (str): output directory (default = "src/zhinst/qcodes/modules/")
    """
    data = {
        "classes": generate_qcodes_class_info(toolkit_class),
        "name": toolkit_class.__name__,
    }

    templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("instrument_class.py.j2")
    result = template.render(data)
    # result = black.format_str(result, mode=black.FileMode())
    result = black.format_str(
        result,
        mode=black.mode.Mode(
            target_versions={black.TargetVersion.PY310},
            line_length=88,
        ),
    )
    result = autoflake.fix_code(result, remove_all_unused_imports=True)
    module_name = camel_to_snake(toolkit_class.__name__)
    py_filename = str(output_dir) + "/" + module_name.lower() + ".py"
    with open(py_filename, "w+") as outfile:
        outfile.write(result)
    print(f"{py_filename} created.")


def generate_qcodes_driver_modules(
    zi_module_class: object,
    template_path: t.Union[str, Path] = conf.TEMPLATE_PATH,
    output_dir: t.Union[str, Path] = conf.OUTPUT_DIR_MODULE_DRIVER,
) -> None:
    """Generates the Qcodes drivers for the ziPython modules.

    The drivers forward all function (except the one in black_list) and
    initialises the nodes a nested qcodes prameter.

    Args:
        zi_module_class (object): ziPython module class
        template_path (str):  jinja template location (default = "templates/")
        output_dir (str): output directory (default = "src/zhinst/qcodes/modules/")
    """
    ignored_functions = []
    if zi_module_class == BaseModule:
        ignored_functions.append("subscribe")
        ignored_functions.append("unsubscribe")
    tk_class_info, _ = getInfo(zi_module_class, [])
    qcodes_functions = []
    for function in tk_class_info.functions:
        if function.name not in ignored_functions:
            qcodes_functions.append(function)

    function_info = generate_functions_info(qcodes_functions, zi_module_class)
    name = zi_module_class.__name__
    module_name = camel_to_snake(zi_module_class.__name__)
    module_docstring = zi_module_class.__doc__.split("Args:")[0]
    node_param = []
    if module_name == "sweeper_module":
        node_param.append("gridnode")
    if module_name == "daq_module":
        node_param.append("triggernode")
    data = {
        "name": name,
        "module_name": module_name,
        "module_docstring": module_docstring,
        "base_module": "ZIInstrument"
        if zi_module_class == BaseModule
        else "ZIBaseModule",
        "functions": function_info,
        "node_param": node_param,
    }
    templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("module_class.py.j2")
    result = template.render(data)
    result = black.format_str(
        result,
        mode=black.mode.Mode(
            target_versions={black.TargetVersion.PY310},
            line_length=88,
        ),
    )
    result = autoflake.fix_code(result, remove_all_unused_imports=True)
    py_filename = str(output_dir) + "/" + module_name.lower() + ".py"
    with open(py_filename, "w+") as outfile:
        outfile.write(result)
    print(f"{py_filename} created.")


def generate_device_api():
    """Generate device API.

    The device API enables that every ZI device is exposed as a class that
    can be istanciated directly without a session.
    """
    DEVICE_API_FILEPATH = "src/zhinst/qcodes/device_creator.py"
    data = {
        "classes": [
            {"name": "ZIDevice", "parent": "ZIBaseInstrument", "is_hf2": False},
            {"name": "SHFQA", "parent": "SHFQADriver", "is_hf2": False},
            {"name": "SHFSG", "parent": "SHFSGDriver", "is_hf2": False},
            {"name": "HDAWG", "parent": "HDAWGDriver", "is_hf2": False},
            {"name": "PQSC", "parent": "PQSCDriver", "is_hf2": False},
            {"name": "SHFQC", "parent": "SHFQCDriver", "is_hf2": False},
            {"name": "UHFLI", "parent": "UHFLIDriver", "is_hf2": False},
            {"name": "UHFQA", "parent": "UHFQADriver", "is_hf2": False},
            {"name": "MFLI", "parent": "ZIBaseInstrument", "is_hf2": False},
            {"name": "MFIA", "parent": "ZIBaseInstrument", "is_hf2": False},
            {"name": "HF2", "parent": "ZIBaseInstrument", "is_hf2": True},
        ],
        "imports": [
            "from zhinst.qcodes.driver.devices.base import ZIBaseInstrument",
            "from zhinst.qcodes.driver.devices.hdawg import HDAWG as HDAWGDriver",
            "from zhinst.qcodes.driver.devices.pqsc import PQSC as PQSCDriver",
            "from zhinst.qcodes.driver.devices.shfqa import SHFQA as SHFQADriver",
            "from zhinst.qcodes.driver.devices.shfqc import SHFQC as SHFQCDriver",
            "from zhinst.qcodes.driver.devices.shfsg import SHFSG as SHFSGDriver",
            "from zhinst.qcodes.driver.devices.uhfli import UHFLI as UHFLIDriver",
            "from zhinst.qcodes.driver.devices.uhfqa import UHFQA as UHFQADriver",
        ],
    }
    templateLoader = jinja2.FileSystemLoader(searchpath=conf.TEMPLATE_PATH)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("device_api.py.j2")
    result = template.render(data)
    result = black.format_str(
        result,
        mode=black.mode.Mode(
            target_versions={black.TargetVersion.PY37},
            line_length=88,
            string_normalization=False,
        ),
    )
    result = autoflake.fix_code(result, remove_all_unused_imports=True)
    result = isort.code(result)
    with open(DEVICE_API_FILEPATH, "w+") as outfile:
        outfile.write(result)
    print(f"{DEVICE_API_FILEPATH} created.")


@click.group()
def main():
    """Autogeneration of QCoDeS driver from zhinst.toolkit."""


@main.command(help="toolkit instrument class")
@click.argument(
    "name",
    required=False,
    type=str,
)
def instrument_class(name):
    """Generate a insturment class."""
    module = importlib.import_module(f"{conf.TOOLKIT_DEVICE_MODULE}.{name.lower()}")
    generate_qcodes_driver(getattr(module, name.upper()))


@main.command(help="toolkit module class")
@click.argument(
    "name",
    required=False,
    type=str,
)
def module_class(name):
    """Generate a module class."""
    module = importlib.import_module(f"{conf.TOOLKIT_MODULE_MODULE}.{name}")
    generate_qcodes_driver_modules(getattr(module, name.upper()))


@main.command(help="Generate all.")
def generate_all():
    """Generate all drivers."""
    for name in conf.DEVICE_DRIVERS:
        module = importlib.import_module(f"{conf.TOOLKIT_DEVICE_MODULE}.{name.lower()}")
        generate_qcodes_driver(getattr(module, name.upper()))
    generate_device_api()

    for name in conf.MODULE_DRIVERS:
        module = importlib.import_module(
            f"{conf.TOOLKIT_MODULE_MODULE}.{camel_to_snake(name)}"
        )
        generate_qcodes_driver_modules(getattr(module, name))


if __name__ == "__main__":
    main()
