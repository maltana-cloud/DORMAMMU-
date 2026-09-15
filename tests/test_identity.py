from pathlib import Path

import dormammu
import devintel


def test_canonical_package_identity_and_legacy_namespace():
    assert dormammu.__version__ == devintel.__version__
    assert Path("pyproject.toml").read_text(encoding="utf-8").splitlines()[1] == 'name = "dormammu"'
