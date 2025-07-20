"""
JavaFile for generating Java source files.

This module defines the JavaFile class, which is used to generate
Java source files with proper package declarations, imports, and type declarations.
"""

import os
import sys
from typing import Dict, Optional, Set, TextIO, Union

from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


class JavaFile:
    """
    Represents a Java source file.

    JavaFile instances are immutable. Use the builder to create new instances.
    """

    def __init__(
        self,
        package_name: str,
        type_spec: TypeSpec,
        file_comment: Optional[CodeBlock],
        skip_java_lang_imports: bool,
        indent: str,
        static_imports: Dict[ClassName, Set[str]],
    ):
        """
        Initialize a new JavaFile.

        Args:
            package_name: The package name
            type_spec: The type to emit
            file_comment: The file comment
            skip_java_lang_imports: Whether to skip java.lang imports
            indent: The indentation string
            static_imports: The static imports (class -> set of static members)
        """
        self.package_name = package_name
        self.type_spec = type_spec
        self.file_comment = file_comment
        self.skip_java_lang_imports = skip_java_lang_imports
        self.indent = indent
        self.static_imports = static_imports

    def write_to(self, out: Union[str, TextIO, None] = None) -> None:
        """
        Write this Java file to the specified output.

        Args:
            out: The output (file path, file-like object, or None for stdout)
        """
        if out is None:
            # Write to stdout
            self.emit_to(sys.stdout)
        elif isinstance(out, str):
            # Write to file path
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "w") as f:
                self.emit_to(f)
        else:
            # Write to file-like object
            self.emit_to(out)

    def emit_to(self, out: TextIO) -> None:
        """
        Emit this Java file to the specified output.

        Args:
            out: The output file-like object
        """
        # Create a CodeWriter for generating the file
        writer = CodeWriter(indent=self.indent)

        # Emit the file
        self.emit_file(writer)

        # Write to the output
        out.write(str(writer))

    def emit_file(self, code_writer: CodeWriter) -> None:
        """
        Emit this Java file to a CodeWriter.

        Args:
            code_writer: The CodeWriter to emit to
        """
        # Emit file comment
        if self.file_comment is not None:
            code_writer.emit("/**\n")
            self.file_comment.emit(code_writer)
            code_writer.emit("\n*/")
            code_writer.emit("\n\n")

        # Emit package declaration
        if self.package_name:
            code_writer.emit(f"package {self.package_name};\n\n")

        # Do a first pass to collect imports
        import_collector = CodeWriter(indent=self.indent)
        self.type_spec.emit(import_collector)

        # Get the imports
        imports = import_collector.get_imports()

        # Emit static imports
        static_imports = sorted(
            [
                f"import static {type_name.qualified_name}.{member};"
                for type_name, members in self.static_imports.items()
                for member in sorted(members)
            ]
        )
        if static_imports:
            for static_import in static_imports:
                code_writer.emit(static_import)
                code_writer.emit("\n")
            code_writer.emit("\n")

        # Emit normal imports
        import_packages = sorted(imports.keys())
        for package in import_packages:
            # Skip java.lang imports if requested
            if self.skip_java_lang_imports and package == "java.lang":
                continue

            for simple_name in sorted(imports[package]):
                code_writer.emit(f"import {package}.{simple_name};\n")

        if import_packages:
            code_writer.emit("\n")

        # Emit the type
        self.type_spec.emit(code_writer)
        code_writer.emit("\n")

    def __str__(self) -> str:
        """
        Get a string representation of this Java file.

        Returns:
            A string representation
        """
        from io import StringIO

        out = StringIO()
        self.emit_to(out)
        return out.getvalue()

    @staticmethod
    def builder(package_name: str, type_spec: TypeSpec) -> "Builder":
        """
        Create a new JavaFile builder.

        Args:
            package_name: The package name
            type_spec: The type to emit

        Returns:
            A new Builder
        """
        return JavaFile.Builder(package_name, type_spec)

    class Builder:
        """
        Builder for JavaFile instances.
        """

        def __init__(self, package_name: str, type_spec: TypeSpec):
            """
            Initialize a new Builder.

            Args:
                package_name: The package name
                type_spec: The type to emit
            """
            self.package_name = package_name
            self.type_spec = type_spec
            self.file_comment = None
            self.skip_java_lang_imports = False
            self.indent = "  "
            self.static_imports = {}  # ClassName -> set of static members

        def add_file_comment(self, format_string: str, *args) -> "JavaFile.Builder":
            """
            Add a file comment.

            Args:
                format_string: The format string
                *args: The arguments to format with

            Returns:
                self for chaining
            """
            self.file_comment = CodeBlock.of(format_string, *args)
            return self

        def skip_java_lang_imports(self, skip: bool = True) -> "JavaFile.Builder":
            """
            Set whether to skip java.lang imports.

            Args:
                skip: Whether to skip java.lang imports

            Returns:
                self for chaining
            """
            self.skip_java_lang_imports = skip
            return self

        def indent(self, indent: str) -> "JavaFile.Builder":
            """
            Set the indentation string.

            Args:
                indent: The indentation string

            Returns:
                self for chaining
            """
            self.indent = indent
            return self

        def add_static_import(self, constant_class: Union[ClassName, str], constant_name: str) -> "JavaFile.Builder":
            """
            Add a static import.

            Args:
                constant_class: The class containing the constant
                constant_name: The constant name

            Returns:
                self for chaining
            """
            if isinstance(constant_class, str):
                constant_class = ClassName.get_from_fqcn(constant_class)

            if constant_class not in self.static_imports:
                self.static_imports[constant_class] = set()

            if constant_name == "*":
                self.static_imports[constant_class].add(constant_name)
            else:
                self.static_imports[constant_class].add(constant_name)

            return self

        def build(self) -> "JavaFile":
            """
            Build a new JavaFile.

            Returns:
                A new JavaFile
            """
            return JavaFile(
                self.package_name,
                self.type_spec,
                self.file_comment,
                self.skip_java_lang_imports,
                self.indent,
                self.static_imports,
            )
