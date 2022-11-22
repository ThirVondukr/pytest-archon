# Py3arch

_(pronounce: py-triarch)_

[![build_and_test](https://github.com/jwbargsten/py3arch/actions/workflows/tests.yml/badge.svg)](https://github.com/jwbargsten/py3arch/actions/workflows/tests.yml)

Py3arch is a little tool that helps you structure (large) Python projects.
This tool allows you to define architectural boundries in your code, also
known as _forbidden dependencies_.

Explicitly defined architectural boundaries help you keep your code in shape.
It avoids the creation of circular dependencies. New people on the project
are made aware of the structure through a simple set of rules, instead of lore.

## Installation


The simple way:

```sh
pip install git+https://github.com/jwbargsten/py3arch.git
```


### As pre-commit hook

Add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/jwbargsten/py3arch
    rev: main
    hooks:
      - id: py3arch
```

## Usage

Py3arch can be used in two different ways: with configuration defined in `pyproject.toml` and
through (test) code.

Both approaches have the own advantages and disadvantages. `pyproject.toml` based configuration
is relatively simple, but the configurability is limited. They can be executed as part of
a pre-commit hook.

Code based rules can be more flexible, especially for bigger, existing code bases. They are
written as tests.

### `pyproject.toml`

Add rules and configuration options to your `pyproject.toml`:

```toml
[tool.py3arch.options]
source = "py3arch"

[tool.py3arch.rules]
"py3arch.collect" = [ "not py3arch.rule" ]
```

(don't forget the quotes (`"`), otherwise it will not work)

In the above example, py3arch will examine the source files in the `py3arch` package.
The module `py3arch.collect` is not supposed to access the module `py3arch.rule`.

The left side of the expression (`py3arch.collect`) should adhere to the rules defined on the right.

The syntax is pretty simple:

* `module.submodule` to define a module is allowed
* `not module.submodule` to define a dependency is not allowed
* `only module` A module or package is only allowed to import from the module package, and its submodules.

Modules can be combined, by separating them with a comma: `module,othermodule`.

### Tests

You can use py3arch in tests by simply importing the `rule` function. Using this
function you can construct import tests:

```
from py3arch.pytest.plugin import rule


def test_rule_basic():
    (
        rule("name", comment="some comment")
        .match("py3arch.col*")
        .except("py3arch.colgate")
        .should_not_import("py3arch.import_finder")
        .should_import("py3arch.core*")
        .check("module", path=["/path/to/base/dir"])
    )
```

- To match the modules and constraints,
  [fnmatch](https://docs.python.org/3/library/fnmatch.html) syntax is used.
- `.except()` is optional
- `.should_import()` and `.should_not_import()` can be combined and occur multiple
  times.
- `.check()` needs either a module object or a string; `path` can be skipped and will be
  derived from the module path.
- `comment=` is currently not used, but might be in the future



## Similar projects

* [Archunit](https://www.archunit.org/) (Java)
* [Dependency Cruiser](https://github.com/sverweij/dependency-cruiser) (Javascript)
* [import-linter](https://github.com/seddonym/import-linter) (Python)
