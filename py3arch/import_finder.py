import ast
import sys
import importlib
import os

import modulefinder

# https://stackoverflow.com/questions/54325116/can-i-handle-imports-in-an-abstract-syntax-tree
# https://bugs.python.org/issue38721
# https://github.com/0cjs/sedoc/blob/master/lang/python/importers.md


def resolve_module_or_object(fqname, path=None):
    spec = find_spec(fqname, path)
    return fqname if spec else fqname.rpartition(".")[0]


def find_spec(fqname, path=None):

    # taken from importlib.util.find_spec
    if fqname in sys.modules:
        module = sys.modules[fqname]
        if module is None:
            return None
        try:
            spec = module.__spec__
        except AttributeError:
            raise ValueError('{}.__spec__ is not set'.format(fqname)) from None
        else:
            if spec is None:
                raise ValueError('{}.__spec__ is None'.format(fqname))
            return spec


    importlib.machinery.PathFinder.invalidate_caches()

    if "." not in fqname:
        return importlib.machinery.PathFinder.find_spec(fqname, path)

    head, tail = fqname.split(".", 1)
    spec = None
    while tail:
        spec = importlib.machinery.PathFinder.find_spec(head, path)
        if spec is None:
            # if we cannot find the last part the "c" of "a.b.c"
            # then we might try to import an object
            # but if we already cannot find the spec for "a.b", then
            # something is off
            if "." in tail:
                raise ImportError("No module named {name!r}".format(name=head), name=head)
            else:
                return None
        file_path = spec.origin
        path = os.path.dirname(file_path)
        head, tail = fqname.split(".", 1)
    return spec


def resolve_import_from(name, module=None, package=None, level=None):
    if not level:
        # absolute import
        return name if module is None else "{}.{}".format(module, name)

    # taken from importlib._bootstrap._resolve_name
    bits = package.rsplit(".", level - 1)
    if len(bits) < level:
        raise ImportError("attempted relative import beyond top-level package")
    base = bits[0]

    # relative import
    if module is None:
        # from . import moduleX
        return "{}.{}".format(base, name)
    else:
        # from .moduleZ import moduleX
        return "{}.{}.{}".format(base, module, name)


def walk_ast(tree, package=None, package_path=None):
    modules = []
    if package_path is None:
        package_path = sys.path
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend([a.name for a in node.names])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                fqname = resolve_import_from(alias.name, node.module, package=package, level=node.level)
                fqname = resolve_module_or_object(fqname, path=package_path)
                modules.append(fqname)
    return modules
