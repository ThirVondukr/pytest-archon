from textwrap import dedent

import pytest

pytest_plugins = "myapp.testsupport.myplugin"

@pytest.fixture
def create_testset(tmp_path):
    def _create_testset(*module_contents):
        for module, contents in module_contents:
            mod_path = tmp_path / module
            mod_path.parent.mkdir(parents=True, exist_ok=True)
            mod_path.write_text(dedent(contents))
        return tmp_path

    return _create_testset
