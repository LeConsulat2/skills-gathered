from __future__ import annotations

import importlib.util
import sys
import unittest

from codex_ones.config import PROJECT_ROOT

SDK_MODULES_AVAILABLE = all(
    importlib.util.find_spec(name) is not None for name in ("openai", "agents", "pydantic")
)


@unittest.skipUnless(SDK_MODULES_AVAILABLE, "Install the learn extra to import SDK examples")
class SdkExampleImportTests(unittest.TestCase):
    def test_paid_examples_import_without_making_requests(self) -> None:
        example_paths = sorted((PROJECT_ROOT / "examples").glob("*.py"))
        for path in example_paths:
            if path.name.startswith(("01_", "07_", "08_", "09_")):
                continue
            module_name = f"codex_ones_import_check_{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            self.assertIsNotNone(spec)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
            finally:
                sys.modules.pop(module_name, None)


if __name__ == "__main__":
    unittest.main()

