import importlib
from typing import Any, Iterable, Mapping


class ImportError(Exception):
    ...


def import_object(name: str) -> Any:
    try:
        module = importlib.import_module(name)
        return module
    except ImportError:
        if "." not in name:
            raise

    mod_name, attr_name = name.rsplit(".", 1)
    module = importlib.import_module(mod_name)
    return getattr(module, attr_name)


def import_from_string(import_str: str) -> Any:
    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        message = 'Import string "{import_str}" must be in format "<module>:<attribute>".'
        raise ImportError(message.format(import_str=import_str))

    try:
        module = importlib.import_module(module_str)
    except ImportError as exc:
        message = 'Could not import module "{module_str}".'
        raise ImportError(message.format(module_str=module_str)) from exc

    instance = module
    try:
        for attr_str in attrs_str.split("."):
            instance = getattr(instance, attr_str)
    except AttributeError as exc:
        message = 'Attribute "{attrs_str}" not found in module "{module_str}".'
        raise ImportError(message.format(attrs_str=attrs_str, module_str=module_str)) from exc

    return instance


def lazy_import(module_name: str, submodules: Iterable[str], submod_attrs: Mapping[str, Iterable[str]]):
    import importlib
    import os

    name_to_submod = {func: mod for mod, funcs in submod_attrs.items() for func in funcs}

    def __getattr__(name):
        if name in submodules:
            attr = importlib.import_module("{module_name}.{name}".format(module_name=module_name, name=name))
        elif name in name_to_submod:
            submodname = name_to_submod[name]
            module = importlib.import_module(
                "{module_name}.{submodname}".format(module_name=module_name, submodname=submodname)
            )
            attr = getattr(module, name)
        else:
            raise AttributeError("No {module_name} attribute {name}".format(module_name=module_name, name=name))
        globals()[name] = attr
        return attr

    if os.environ.get("EAGER_IMPORT", ""):
        for name in name_to_submod.values():
            __getattr__(name)

        for attrs in submod_attrs.values():
            for attr in attrs:
                __getattr__(attr)
    return __getattr__
