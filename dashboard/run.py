import os
import sys

_dashboard_dir = os.path.dirname(os.path.abspath(__file__))
if _dashboard_dir not in sys.path:
    sys.path.insert(0, _dashboard_dir)

_code_dir = os.path.normpath(os.path.join(_dashboard_dir, "..", "code"))
if _code_dir not in sys.path:
    sys.path.insert(0, _code_dir)

import streamlit.web.bootstrap

if __name__ == "__main__":
    app_path = os.path.join(_dashboard_dir, "app.py")
    streamlit.web.bootstrap.run(
        app_path,
        "",
        [],
        flag_options={},
    )
