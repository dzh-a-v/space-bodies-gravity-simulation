from __future__ import annotations

import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class OptionalBuildExt(build_ext):
    """Build the C++ backend when possible, but keep Python fallback installable."""

    def run(self):
        try:
            super().run()
        except Exception as exc:
            print(f"warning: optional C++ backend was not built: {exc}", file=sys.stderr)

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as exc:
            print(f"warning: optional extension {ext.name} was not built: {exc}", file=sys.stderr)


def extension_modules() -> list[Extension]:
    try:
        import pybind11
    except ImportError:
        return []

    compile_args = ["/std:c++17", "/O2"] if sys.platform == "win32" else ["-std=c++17", "-O3"]
    return [
        Extension(
            "gravity_sim._cpp_backend",
            [str(Path("src") / "gravity_sim" / "native" / "cpp_backend.cpp")],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=compile_args,
        )
    ]


setup(
    ext_modules=extension_modules(),
    cmdclass={"build_ext": OptionalBuildExt},
)
