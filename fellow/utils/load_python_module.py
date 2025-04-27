import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_python_module(file_path: Path) -> ModuleType:
    """
    todo: doc
    todo: test?
    """
    module_name = f"fellow_custom_{file_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module
