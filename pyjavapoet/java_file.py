"""
Copyright (C) 2015 Square, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Modified by Matthew Au-Yeung on 2025-07-29; see changelog.md for more details.
- Similar APIs ported from Java to Python.
"""

import sys
from io import StringIO
from pathlib import Path
from typing import Optional, TextIO, Union

from pyjavapoet.code_base import Code
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import EMPTY_STRING, CodeWriter
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


class JavaFile(Code["JavaFile"]):
    """
    Represents a Java source file. Includes package declaration, imports, and type declarations.

    JavaFile instances are immutable. Use the builder to create new instances.
    """

    def __init__(
        self,
        package_name: str,
        type_spec: TypeSpec,
        file_comment: Optional[CodeBlock],
        indent: str,
        static_imports: dict[ClassName, set[str]],
        additional_imports: set[str],
    ):
        self.package_name = package_name
        self.type_spec = type_spec
        self.file_comment = file_comment
        self.indent = indent
        self.static_imports = static_imports
        self.additional_imports = additional_imports

    def write_to_dir(self, java_dir: Path) -> Path:
        """
        Pass in the directory to write the file to using the relative path.
        i.e. java_dir = Path("src/main/java")
        """
        relative_path = self.get_relative_path()
        file_path = java_dir / relative_path
        self.write_to(file_path)
        return file_path

    def write_to(self, out: Union[str, Path, TextIO, None] = None) -> None:
        """
        out: str | Path | TextIO | None
        If None, write to stdout.
        If str or Path, write to file.
        If TextIO, write to file-like object.
        """
        if out is None:
            # Write to stdout
            self.emit_to(sys.stdout)
        elif isinstance(out, (str, Path)):
            # Write to file path
            out = Path(out)
            if parent := out.parent:
                parent.mkdir(parents=True, exist_ok=True)

            with open(out, "w") as f:
                self.emit_to(f)
        else:
            # Write to file-like object
            self.emit_to(out)

    def emit_to(self, out: TextIO) -> None:
        # Create a CodeWriter for generating the file
        writer = CodeWriter(
            indent=self.indent,
            type_spec_class_name=ClassName.get(self.package_name, self.type_spec.name),
        )
        # Emit the file
        self.emit(writer)
        # Write to the output
        out.write(str(writer))

    def _extract_wildcard_imports(self) -> set[str]:
        """Extract wildcard package imports from additional imports.

        Returns:
            Set of package names that have wildcard imports (e.g., 'java.util' for 'java.util.*')
        """
        wildcard_packages = set()

        for import_name in self.additional_imports:
            if import_name.endswith(".*"):
                # Wildcard import - extract package name
                package = import_name[:-2]  # Remove ".*"
                wildcard_packages.add(package)

        return wildcard_packages

    def _merge_all_specific_imports(
        self, collected_imports: dict[str, set[str]], wildcard_packages: set[str]
    ) -> dict[str, set[str]]:
        """Merge all specific imports (collected + additional) while excluding wildcard-covered packages.

        Args:
            collected_imports: Imports collected from type usage in the code
            wildcard_packages: Packages with wildcard imports to exclude

        Returns:
            Final resolved specific imports (excluding those covered by wildcards)
        """
        final_imports = {}

        # Add collected imports, but skip those covered by wildcards
        for package, simple_names in collected_imports.items():
            if package not in wildcard_packages:
                if package not in final_imports:
                    final_imports[package] = set()
                final_imports[package].update(simple_names)

        # Process additional specific imports and add them
        for import_name in self.additional_imports:
            if not import_name.endswith(".*") and "." in import_name:
                # This is a specific import, not a wildcard
                package, simple_name = import_name.rsplit(".", 1)

                # Only add if not covered by wildcard
                if package not in wildcard_packages:
                    if package not in final_imports:
                        final_imports[package] = set()
                    final_imports[package].add(simple_name)

        return final_imports

    def _emit_all_imports(
        self, code_writer: CodeWriter, final_imports: dict[str, set[str]], wildcard_packages: set[str]
    ) -> None:
        """Emit all import statements in the correct order.

        Args:
            code_writer: The CodeWriter to emit to
            final_imports: The resolved specific imports to emit
            wildcard_packages: The wildcard packages to emit
        """
        # Emit static imports first
        static_imports = sorted(
            [
                f"import static {type_name.canonical_name}.{member};"
                for type_name, members in self.static_imports.items()
                for member in sorted(members)
            ]
        )

        if static_imports:
            for static_import in static_imports:
                code_writer.emit(static_import)
                code_writer.emit("\n")
            code_writer.emit("\n")

        # Combine wildcard and specific imports, then sort them together
        all_imports = []

        # Add wildcard imports
        for package in wildcard_packages:
            all_imports.append(f"import {package}.*;")

        # Add specific imports
        for package in final_imports:
            for simple_name in final_imports[package]:
                all_imports.append(f"import {package}.{simple_name};")

        # Sort all imports alphabetically and emit them
        for import_statement in sorted(all_imports):
            code_writer.emit(import_statement)
            code_writer.emit("\n")

        # Add blank line after imports if there were any
        if all_imports:
            code_writer.emit("\n")

    def emit(self, code_writer: CodeWriter) -> None:
        # Emit file comment
        if self.file_comment is not None:
            self.file_comment.emit_javadoc(code_writer)
            code_writer.emit("\n")

        # Emit package declaration
        if self.package_name:
            code_writer.emit(f"package {self.package_name};\n\n")

        # Do a first pass to collect imports
        import_collector = CodeWriter(
            indent=self.indent,
            type_spec_class_name=ClassName.get(self.package_name, self.type_spec.name),
        )
        self.type_spec.emit(import_collector)

        # Get the imports from type usage and process all imports
        collected_imports = import_collector.get_imports()
        wildcard_packages = self._extract_wildcard_imports()
        final_imports = self._merge_all_specific_imports(collected_imports, wildcard_packages)
        self._emit_all_imports(code_writer, final_imports, wildcard_packages)

        # Emit the type
        self.type_spec.emit(code_writer)
        code_writer.emit("\n")

    def get_relative_path(self) -> Path:
        package_path = Path(*self.package_name.split("."))
        return package_path.joinpath(self.type_spec.name + ".java")

    def to_builder(self) -> "Builder":
        return JavaFile.Builder(
            self.package_name,
            self.type_spec,
            self.file_comment,
            self.indent,
            self.static_imports,
            self.additional_imports,
        )

    def __str__(self) -> str:
        with StringIO() as sio:
            self.emit_to(sio)
            return sio.getvalue()

    @staticmethod
    def builder(package_name: str, type_spec: TypeSpec) -> "Builder":
        return JavaFile.Builder(package_name, type_spec)

    class Builder(Code.Builder["JavaFile"]):
        """
        Builder for JavaFile instances.
        """

        def __init__(
            self,
            package_name: str,
            type_spec: TypeSpec,
            file_comment: Optional[CodeBlock] = None,
            indent: str = "  ",
            static_imports: dict[ClassName, set[str]] | None = None,
            additional_imports: set[str] | None = None,
        ):
            self.__package_name = package_name
            self.__type_spec = type_spec
            self.__file_comment = file_comment
            self.__indent = indent
            self.__static_imports = static_imports or {}
            self.__additional_imports = additional_imports or set()

        def add_file_comment(self, format_string: str = EMPTY_STRING, *args) -> "JavaFile.Builder":
            self.__file_comment = CodeBlock.add_javadoc(self.__file_comment, format_string, *args)
            return self

        def add_file_comment_line(self, format_string: str = EMPTY_STRING, *args) -> "JavaFile.Builder":
            self.__file_comment = CodeBlock.add_javadoc_line(self.__file_comment, format_string, *args)
            return self

        def indent(self, indent: str) -> "JavaFile.Builder":
            self.__indent = indent
            return self

        def add_static_import(self, constant_class: Union[ClassName, str], constant_name: str) -> "JavaFile.Builder":
            if isinstance(constant_class, str):
                constant_class = ClassName.get_from_fqcn(constant_class)

            if constant_class not in self.__static_imports:
                self.__static_imports[constant_class] = set()

            if constant_name == "*":
                self.__static_imports[constant_class].add(constant_name)
            else:
                self.__static_imports[constant_class].add(constant_name)

            return self

        def add_additional_import(self, import_name: str) -> "JavaFile.Builder":
            """Add an additional import that will be included in the generated file.

            Args:
                import_name: The import to add (e.g., "java.util.List" or "java.util.*")

            Returns:
                This builder for method chaining
            """
            self.__additional_imports.add(import_name)
            return self

        def build(self) -> "JavaFile":
            return JavaFile(
                self.__package_name,
                self.__type_spec,
                self.__file_comment,
                self.__indent,
                self.__static_imports,
                self.__additional_imports,
            )
