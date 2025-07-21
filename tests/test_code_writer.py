"""
Tests for CodeWriter functionality.
Equivalent to CodeWriterTest.java
"""

import unittest

from pyjavapoet.code_writer import CodeWriter


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


if __name__ == "__main__":
    unittest.main()
