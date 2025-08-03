"""
Copyright (C) 2025 Matthew Au-Yeung.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import ClassName


class CodeWriterTest(unittest.TestCase):
    """Test the CodeWriter class."""

    def test_basic_code_writing(self):
        """Test basic code writing functionality."""
        writer = CodeWriter()

        writer.emit("public class Test {\n")
        writer.indent()
        writer.emit("private String name;\n")
        writer.unindent()
        writer.emit("}\n")

        result = str(writer)
        expected = "public class Test {\n  private String name;\n}\n"
        self.assertEqual(result, expected)

    def test_indentation_handling(self):
        """Test indentation handling."""
        writer = CodeWriter()

        writer.emit("start\n")
        writer.indent()
        writer.emit("indented\n")
        writer.indent()
        writer.emit("double indented\n")
        writer.unindent()
        writer.emit("single indented\n")
        writer.unindent()
        writer.emit("end\n")

        result = str(writer)
        expected = "start\n  indented\n    double indented\n  single indented\nend\n"
        self.assertEqual(result, expected)

    def test_emit_with_nested_newlines_handling(self):
        """Test that if double newline and there's a new_line_prefix, we add it."""
        writer = CodeWriter()
        # Emit a line, then a double newline with a prefix, then another line
        writer.emit("line1\n", new_line_prefix="// ")
        writer.emit("\n\nline2\n", new_line_prefix="// ")
        writer.emit("line3", new_line_prefix="// ")

        result = str(writer)
        # The expected result:
        # // line1
        # //
        # //
        # // line2
        # // line3
        expected = "// line1\n// \n// \n// line2\n// line3"
        self.assertEqual(result, expected)

    def test_custom_indent_string(self):
        """Test custom indentation string."""
        writer = CodeWriter(indent="\t")

        writer.emit("public class Test {\n")
        writer.indent()
        writer.emit("private String name;\n")
        writer.unindent()
        writer.emit("}\n")

        result = str(writer)
        expected = "public class Test {\n\tprivate String name;\n}\n"
        self.assertEqual(result, expected)

    def test_emit_type_with_imports_and_package_name(self):
        """Test that emit_type uses imports and package_name correctly."""
        writer = CodeWriter(type_spec_class_name=ClassName.get("foo", "Test"))

        bar_Baz = ClassName.get("bar", "Baz")
        foo_Qux = ClassName.get("foo", "Qux")

        # First use: should record import for bar.Baz and emit 'Baz'
        writer.emit_type(bar_Baz)
        writer.emit(" a;\n")

        # Second use: should emit 'Baz' again (imported)
        writer.emit_type(bar_Baz)
        writer.emit(" b;\n")

        # Use a class from the same package: should emit just 'Qux'
        writer.emit_type(foo_Qux)
        writer.emit(" c;\n")

        result = str(writer)
        # Both uses of bar.Baz should emit 'Baz', not 'bar.Baz'
        self.assertIn("Baz a;", result)
        self.assertIn("Baz b;", result)
        self.assertIn("Qux c;", result)
        self.assertNotIn("bar.Baz", result)

        # The import should be recorded for bar.Baz, but not for foo.Qux
        imports = writer.get_imports()
        self.assertIn("bar", imports)
        self.assertIn("Baz", imports["bar"])
        self.assertNotIn("foo", imports)

    def test_emit_type_with_same_classname_different_packages(self):
        """Test that emit_type distinguishes between same class name in different packages."""
        writer = CodeWriter(type_spec_class_name=ClassName.get("foo", "Test"))

        bar_Baz = ClassName.get("bar", "Baz")
        qux_Baz = ClassName.get("qux", "Baz")

        # First use: should record import for bar.Baz and emit 'Baz'
        writer.emit_type(bar_Baz)
        writer.emit(" a;\n")

        # Second use: should record import for qux.Baz and emit 'qux.Baz'
        writer.emit_type(qux_Baz)
        writer.emit(" b;\n")

        result = str(writer)
        # The first should emit 'Baz a;', the second should emit 'qux.Baz b;'
        self.assertIn("Baz a;", result)
        self.assertIn("qux.Baz b;", result)

        # The imports should include both bar.Baz and qux.Baz
        imports = writer.get_imports()
        self.assertIn("bar", imports)
        self.assertIn("Baz", imports["bar"])
        self.assertNotIn("qux", imports)


if __name__ == "__main__":
    unittest.main()
