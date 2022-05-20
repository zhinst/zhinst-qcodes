"""Autogenerate the QCodes drivers from toolkit and ziPython"""
from collections import namedtuple
import typing
import inspect
import re
import importlib
import jinja2
import black
import autoflake
import click
from pathlib import Path

from zhinst.toolkit.driver.devices.base import BaseInstrument
from zhinst.toolkit.driver.modules.base_module import BaseModule
from zhinst.toolkit.nodetree import Node, NodeTree

parameter_tuple = namedtuple("parameter", ["name", "is_node"])
submodule_tuple = namedtuple("submodule", ["subclass", "name", "is_list"])
function_tuple = namedtuple("function", ["name", "is_deprecated"])
class_tuple = namedtuple("toolkit_class", ["functions", "parameters", "sub_modules"])

_PKG_ROOT = Path(__file__).parent
TEMPLATE_PATH = _PKG_ROOT / "templates"
OUTPUT_DIR_DEVICES_DRIVER_ = _PKG_ROOT.parent / "src/zhinst/qcodes/driver/devices/"

def getPropertyInfo(
    name: str, property: object, class_type: object
) -> typing.Union[parameter_tuple, submodule_tuple]:
    """Get all necessary information for a toolkit property.

    Args:
        name (str): Name of the property
        property (object): Class of the property
        class_type (object): Owner class of the property

    Returns:
        Union[parameter_tuple,submodule_tuple]
    """
    typehint = typing.get_type_hints(property.fget)
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
        except:
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


def getInfo(
    class_type: object, existing_names: list
) -> typing.Tuple[class_tuple, list]:
    """Get all necessary information for a toolkit class.

    Args:
        class_type (object) toolkit class
        existing_names (list) list of existing names for the QCodes class.

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


def generate_submodules_info(sub_modules: list) -> typing.List[list]:
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
        if "typing.Optional" in str(module):
            module = module.__args__[0]
        parent_info.append(
            {"name": name, "class_name": module.__name__, "is_list": is_list}
        )
        submodule_info += generate_qcodes_class_info(
            module, is_submodule=True, is_list_element=is_list
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
            return_annotation = return_annotation.replace("typing.", "")

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
    # Enums from toolkit should be exposed also in the QCodes driver
    enums = {
        "SHFQAChannelMode": "zhinst.toolkit.interface.SHFQAChannelMode",
        "MappingMode": "zhinst.toolkit.interface.MappingMode",
        "TriggerImpedance": "zhinst.toolkit.interface.TriggerImpedance",
        "AveragingMode": "zhinst.toolkit.interface.AveragingMode",
        "Waveforms": "zhinst.toolkit.waveform.Waveforms",
        "CommandTable": "zhinst.toolkit.command_table.CommandTable",
    }
    # weird typing infos that can be replaced with the right term
    replacements = {"<built-in function array>": "np.array"}
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
        # replace toolkit enum typehint with direct typehint
        for enum in enums.keys():
            if enum in signature_str:
                signature_str = signature_str.replace(enums[enum], enum)
                # search for enum typehint in function arguments
                regex_result = re.search(
                    f"<({enum}.*?):.*?>",
                    signature_str,
                )
                if regex_result:
                    signature_str = signature_str.replace(
                        regex_result.group(0), regex_result.group(1)
                    )
        # replace weird stuff
        for weird_stuff, replacement in replacements.items():
            signature_str = signature_str.replace(weird_stuff, replacement)

        functions_info.append(
            {
                "name": name,
                "decorator": decorator,
                "signature": signature_str,
                "docstring": docstring if docstring else "",
                "call_signature": ", ".join(
                    [f"{x}={x}" for x in signature.parameters][1:]
                ),
                "return_annotation": str(signature.return_annotation)
                if signature.return_annotation
                else "",
            }
        )
    return functions_info


def generate_qcodes_class_info(
    class_type: object, is_submodule: bool = False, is_list_element: bool = False
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
    submodule_info, gathered_info = generate_submodules_info(tk_class_info.sub_modules)
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
    """Convert camelcase into snake case

    Args:
        name  (str): name in camel case

    Returns:
        str: name in snake case
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def generate_qcodes_driver(
    toolkit_class: object,
    template_path: typing.Union[str, Path] = TEMPLATE_PATH,
    output_dir: typing.Union[str, Path] = OUTPUT_DIR_DEVICES_DRIVER_,
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
    result = black.format_str(result, mode=black.FileMode())
    result = autoflake.fix_code(result, remove_all_unused_imports=True)
    module_name = camel_to_snake(toolkit_class.__name__)

    py_filename = str(output_dir) + "/" + module_name.lower() + ".py"
    with open(py_filename, "w+") as outfile:
        outfile.write(result)
    print(f"{py_filename} created.")


# def generate_qcodes_driver_modules(
#     zi_module_class: object,
#     module_name: str,
#     template_path: str = "templates/",
#     output_dir: str = "src/zhinst/qcodes/modules/",
#     name: str = None,
# ) -> None:
#     """Generates the Qcodes drivers for the ziPython modules.

#     The drivers forward all function (except the one in black_list) and
#     initialises the nodes a nested qcodes prameter.

#     Args:
#         zi_module_class (object): ziPython module class
#         template_path (str):  jinja template location (default = "templates/")
#         output_dir (str): output directory (default = "src/zhinst/qcodes/modules/")
#         name (str): name for the module. default is the original class name
#     """
#     ignored_functions = []
#     if zi_module_class == BaseModule:
#         ignored_functions.append("subscribe")
#         ignored_functions.append("unsubscribe")
#     tk_class_info, _ = getInfo(zi_module_class, [])
#     qcodes_functions = []
#     for function in tk_class_info.functions:
#         if function.name not in ignored_functions:
#             qcodes_functions.append(function)

#     function_info = generate_functions_info(qcodes_functions, zi_module_class)
#     name = name if name else zi_module_class.__name__
#     data = {
#         "name": name,
#         "module_name": module_name,
#         "base_module": "Instrument"
#         if zi_module_class == BaseModule
#         else "BaseInstrument",
#         "functions": function_info,
#     }

#     templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
#     templateEnv = jinja2.Environment(loader=templateLoader)
#     template = templateEnv.get_template("module_class.py.j2")
#     result = template.render(data)
#     # result = black.format_str(result, mode=black.FileMode())
#     # result = autoflake.fix_code(result, remove_all_unused_imports=True)
#     module_name = camel_to_snake(name)
#     open(output_dir + module_name.lower() + ".py", "w").write(result)

#     # source, additional_imports=None, expand_star_imports=False,
#     #          remove_all_unused_imports=False, remove_duplicate_keys=False,
#     #          remove_unused_variables=False, ignore_init_module_imports=False):
#     print(f"Module {output_dir + name.lower()}.py created.")


@click.group()
def main():
    """Autogeneration of QCoDeS driver from zhinst.toolkit"""


@main.command(help="toolkit instrument class")
@click.argument(
    "name",
    required=True,
    type=str,
)
def instrument_class(name):
    module = importlib.import_module(f"zhinst.toolkit.driver.devices.{name.lower()}")
    generate_qcodes_driver(getattr(module, name.upper()))


# @main.command(help="toolkit modules")
# @click.argument(
#     "name",
#     required=True,
#     type=str,
# )
# @click.option(
#     "-t", "--target", type=str, help="QCoDeS class name of the Module", default=None
# )
# def zi_module(name, target):
#     module = importlib.import_module(f"zhinst.toolkit.driver.modules.{name.lower()}")
#     generate_qcodes_driver_modules(getattr(module, name))


if __name__ == "__main__":
    main()
