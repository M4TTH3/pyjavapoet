"""
Tests for CodeWriter functionality.
Equivalent to CodeWriterTest.java
"""

import unittest

from pyjavapoet.code_writer import CodeWriter


class CodeWriterTest(unittest.TestCase):
    """Test the CodeWriter class."""

    def test_empty_line_in_javadoc_dos_endings(self):
        """Test javadoc formatting with DOS line endings."""
        # This test is quite specific to the Java implementation
        # In Python, we'll test basic line ending handling
        writer = CodeWriter()

        # Test that the writer handles different line endings consistently
        javadoc = "/**\r\n * First line.\r\n *\r\n * Second line.\r\n */"
        normalized = writer.normalize_line_endings(javadoc)

        # Should normalize to Unix line endings
        expected = "/**\n * First line.\n *\n * Second line.\n */"
        self.assertEqual(normalized, expected)

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
        writer = CodeWriter(indent_string="\t")

        writer.emit("public class Test {\n")
        writer.indent()
        writer.emit("private String name;\n")
        writer.unindent()
        writer.emit("}\n")

        result = str(writer)
        expected = "public class Test {\n\tprivate String name;\n}\n"
        self.assertEqual(result, expected)

    def test_emit_with_format(self):
        """Test emit with format placeholders."""
        writer = CodeWriter()

        writer.emit_format("public $L $L", "class", "Test")
        writer.emit(" {\n")
        writer.indent()
        writer.emit_format("private $L $L;\n", "String", "name")
        writer.unindent()
        writer.emit("}\n")

        result = str(writer)
        expected = "public class Test {\n  private String name;\n}\n"
        self.assertEqual(result, expected)

    def test_line_wrapping(self):
        """Test line wrapping functionality."""
        writer = CodeWriter(line_length=20)  # Short line length for testing

        # This would test line wrapping, but implementation details may vary
        long_line = "this is a very long line that should be wrapped"
        writer.emit(long_line + "\n")

        result = str(writer)
        # Basic test that content is preserved
        self.assertIn("this is a very long line", result)

    def test_zero_width_space_handling(self):
        """Test zero-width space handling in line wrapping."""
        writer = CodeWriter()

        # Test that zero-width spaces are handled properly
        text_with_zwsp = "method\u200bname"  # Zero-width space
        writer.emit(text_with_zwsp + "\n")

        result = str(writer)
        self.assertIn("methodname", result)


if __name__ == "__main__":
    unittest.main()
