import sys
from pathlib import Path
import importlib.util

current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

# Force load 'core' package
core_init = current_dir / "core" / "__init__.py"
spec_core = importlib.util.spec_from_file_location("core", str(core_init))
core_pkg = importlib.util.module_from_spec(spec_core)
sys.modules["core"] = core_pkg
spec_core.loader.exec_module(core_pkg)

# Force load 'ui' package
ui_init = current_dir / "ui" / "__init__.py"
spec_ui = importlib.util.spec_from_file_location("ui", str(ui_init))
ui_pkg = importlib.util.module_from_spec(spec_ui)
sys.modules["ui"] = ui_pkg
spec_ui.loader.exec_module(ui_pkg)

from ui.app import OurWorldApp

if __name__ == "__main__":
    app = OurWorldApp()
    app.mainloop()