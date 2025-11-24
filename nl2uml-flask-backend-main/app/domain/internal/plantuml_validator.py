from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Tuple


class PlantUMLValidator:
    """
    Validates PlantUML diagrams using the official PlantUML jar when available.
    Provide PLANTUML_JAR_PATH (or PLANTUML_JAR) to enable validation.
    """

    def __init__(self, jar_path: str | None = None, java_cmd: str | None = None):
        self.jar_path = jar_path or os.getenv("PLANTUML_JAR_PATH") or os.getenv("PLANTUML_JAR")
        self.java_cmd = java_cmd or os.getenv("PLANTUML_JAVA_CMD", "java")

    def is_available(self) -> bool:
        if not self.jar_path:
            return False
        if not os.path.exists(self.jar_path):
            return False
        return shutil.which(self.java_cmd) is not None

    def validate(self, plantuml: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, output). When PlantUML jar is unavailable, returns (True, "").
        """
        if not self.is_available():
            return True, ""
        if not plantuml.strip():
            return False, "PlantUML diagram is empty."

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".puml") as tmp:
                tmp.write(plantuml)
                tmp_path = tmp.name

            cmd = [self.java_cmd, "-jar", self.jar_path, "-check", tmp_path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode == 0, output.strip()
        except FileNotFoundError:
            # java not installed; treat as unavailable
            return True, ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            if tmp_path:
                png_path = os.path.splitext(tmp_path)[0] + ".png"
                if os.path.exists(png_path):
                    os.remove(png_path)
