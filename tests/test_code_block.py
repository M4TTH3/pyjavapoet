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

from pyjavapoet.code_block import CodeBlock
from pyjavapoet.code_writer import CodeWriter
from pyjavapoet.type_name import ClassName


class MockNamed:
    """Mock class with a name attribute for testing $N placeholders."""

    def __init__(self, name):
        self.name = name


class CodeBlockTest(unittest.TestCase):
    """Test the CodeBlock class."""

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = CodeBlock.builder().build()
        b = CodeBlock.builder().build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

        a = CodeBlock.builder().add("$L", "taco").build()
        b = CodeBlock.builder().add("$L", "taco").build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_copy_and_to_builder(self):
        """Test copy() and to_builder() methods of CodeBlock."""
        # Create a complex CodeBlock
        block = (
            CodeBlock.builder()
            .add("if ($L)", True)
            .begin_control_flow("")
            .add_statement("System.out.println($S)", "Hello")
            .end_control_flow()
            .build()
        )

        # Test copy() produces an equal but not identical object
        block_copy = block.copy()
        self.assertEqual(block, block_copy)
        self.assertIsNot(block, block_copy)
        self.assertEqual(str(block), str(block_copy))

        # Mutate the copy's builder and ensure original is unchanged
        builder = block.to_builder()
        builder.add_statement("System.out.println($S)", "World")
        new_block = builder.build()
        self.assertNotEqual(str(block), str(new_block))
        self.assertIn("World", str(new_block))
        self.assertNotIn("World", str(block))

        # to_builder should produce a builder that can round-trip
        rebuilt = builder.build()
        self.assertEqual(str(new_block), str(rebuilt))

    def test_of(self):
        """Test CodeBlock.of() factory method."""
        a = CodeBlock.of("$L taco", "delicious")
        self.assertEqual(str(a), "delicious taco")

    def test_basic_placeholders(self):
        """Test basic placeholder functionality."""
        # Test $L (literal)
        block = CodeBlock.of("$L", "hello")
        self.assertEqual(str(block), "hello")

        # Test $S (string)
        block = CodeBlock.of("$S", "hello")
        self.assertEqual(str(block), '"hello"')

        # Test $T (type) - basic case
        block = CodeBlock.of("$T", "String")
        self.assertEqual(str(block), "String")

        # Test $N (name)
        block = CodeBlock.of("$N", MockNamed("myVar"))
        self.assertEqual(str(block), "myVar")

    def test_string_escaping(self):
        """Test that string placeholders properly escape special characters."""
        block = CodeBlock.of("$S", 'hello "world"')
        self.assertEqual(str(block), '"hello \\"world\\""')

        block = CodeBlock.of("$S", "hello\\world")
        self.assertEqual(str(block), '"hello\\\\world"')

    def test_indent_and_unindent(self):
        """Test indent and unindent placeholders."""
        block = CodeBlock.builder().add("start\n$>indented\n$<end").build()
        expected = "start\n  indented\nend"
        self.assertEqual(str(block), expected)

    def test_nested_code_blocks(self):
        """Test that CodeBlocks can contain other CodeBlocks."""
        inner = CodeBlock.of("inner content")
        outer = CodeBlock.of("before $L after", inner)
        self.assertEqual(str(outer), "before inner content after")

    def test_multiple_placeholders(self):
        """Test multiple placeholders in one format string."""
        block = CodeBlock.of("$S says $S", "Alice", "Hello")
        self.assertEqual(str(block), '"Alice" says "Hello"')

    def test_mixed_placeholders(self):
        """Test mixing different types of placeholders."""
        block = CodeBlock.of("String $N = $S;", MockNamed("var"), "value")
        self.assertEqual(str(block), 'String var = "value";')

    def test_statement_has_indentation(self):
        """Test that statement has indentation."""
        block = CodeBlock.builder().add_statement("return StringBuilder\n.of($S)\n.toString()", "hello").build()
        self.assertEqual(str(block), 'return StringBuilder\n    .of("hello")\n    .toString();\n')

    def test_add_statement(self):
        """Test adding statements."""
        block = CodeBlock.builder().add_statement("return $S", "hello").build()
        self.assertEqual(str(block), 'return "hello";\n')

    def test_begin_control_flow(self):
        """Test begin control flow."""
        block = (
            CodeBlock.builder()
            .begin_control_flow("if ($L)", True)
            .add_statement("return $S", "yes")
            .end_control_flow()
            .build()
        )

        expected = 'if (true) {\n  return "yes";\n}\n'
        self.assertEqual(str(block), expected)

    def test_next_control_flow(self):
        """Test next control flow (else/else if)."""
        block = (
            CodeBlock.builder()
            .begin_control_flow("if ($L)", False)
            .add_statement("return $S", "no")
            .next_control_flow("else")
            .add_statement("return $S", "maybe")
            .end_control_flow()
            .build()
        )

        expected = 'if (false) {\n  return "no";\n} else {\n  return "maybe";\n}\n'
        self.assertEqual(str(block), expected)

    def test_manual_indentation(self):
        """Test manual indentation."""
        block = CodeBlock.builder().add("start\n").add("$>").add("middle\n").add("$<").add("end\n").build()

        expected = "start\n  middle\nend\n"
        self.assertEqual(str(block), expected)

    def test_join_to_code(self):
        """Test joining code blocks."""
        code_blocks = [
            CodeBlock.of("$S", "hello"),
            CodeBlock.of("$T", ClassName.get("com.example.world", "World")),
            CodeBlock.of("need tacos"),
        ]
        joined = CodeBlock.join_to_code(code_blocks, " || ")
        self.assertEqual(str(joined), '"hello" || World || need tacos')

    def test_join_to_code_single(self):
        """Test joining single code block."""
        code_blocks = [CodeBlock.of("$S", "hello")]
        joined = CodeBlock.join_to_code(code_blocks, " || ")
        self.assertEqual(str(joined), '"hello"')

    def test_join_to_code_empty(self):
        """Test joining empty list."""
        joined = CodeBlock.join_to_code([], " || ")
        self.assertEqual(str(joined), "")

    def test_copy(self):
        """Test copying code blocks."""
        original = CodeBlock.of("$S", "hello")
        copied = original.copy()
        self.assertEqual(str(original), str(copied))
        self.assertEqual(original, copied)
        self.assertIsNot(original, copied)

    def test_builder_chaining(self):
        """Test that builder methods can be chained."""
        block = CodeBlock.builder().add("first").add(" second").add(" third").build()
        self.assertEqual(str(block), "first second third")

    def test_empty_code_block(self):
        """Test empty code block."""
        block = CodeBlock.builder().build()
        self.assertEqual(str(block), "")

    def test_no_placeholders(self):
        """Test code block with no placeholders."""
        block = CodeBlock.of("just text")
        self.assertEqual(str(block), "just text")

    def test_regex_compilation(self):
        """Test that the regex pattern compiles without errors."""
        # This should not raise an exception
        pattern = CodeBlock.placeholder_match
        self.assertIsNotNone(pattern)

        # Test that it can match basic patterns
        test_string = "$L $S $T $N"
        matches = pattern.findall(test_string)
        # The regex should find 4 matches for the 4 placeholders
        self.assertEqual(len(matches), 4)

    def test_type_placeholder_with_classname(self):
        """Test $T placeholder with ClassName objects."""
        class_name = ClassName.get("java.lang", "String")
        block = CodeBlock.of("$T", class_name)
        self.assertEqual(str(block), "String")

    def test_literal_with_numbers(self):
        """Test $L placeholder with numbers."""
        block = CodeBlock.of("$L", 42)
        self.assertEqual(str(block), "42")

        block = CodeBlock.of("$L", 3.14)
        self.assertEqual(str(block), "3.14")

    def test_name_placeholder_with_string(self):
        """Test $N placeholder with plain string when object has no name attribute."""
        block = CodeBlock.of("$N", "plainString")
        self.assertEqual(str(block), "plainString")

    # Tests for features that may not be fully implemented yet
    def test_named_arguments_basic(self):
        """Test basic named arguments functionality."""
        block = CodeBlock.builder().add("Hello $name:S", name="World").build()
        # If this works, test the output
        self.assertEqual(str(block), 'Hello "World"')

        with self.assertRaises(KeyError):
            str(CodeBlock.builder().add("$name:S", noop="World").build())

    def test_indexed_arguments_basic(self):
        """Test basic indexed arguments functionality."""
        block = CodeBlock.builder().add("$1L $2S", "first", "second").build()
        # If this works, test the output
        self.assertEqual(str(block), 'first "second"')
        with self.assertRaises(IndexError):
            str(CodeBlock.builder().add("$1L $2S", "first").build())

    def test_control_flow_nesting(self):
        """Test nested control flow structures."""
        block = (
            CodeBlock.builder()
            .begin_control_flow("if (condition1)")
            .begin_control_flow("if (condition2)")
            .add_statement("doSomething()")
            .end_control_flow()
            .next_control_flow("else")
            .add_statement("doSomethingElse()")
            .end_control_flow()
            .build()
        )

        expected = (
            "if (condition1) {\n  if (condition2) {\n    doSomething();\n  }\n} else {\n  doSomethingElse();\n}\n"
        )
        self.assertEqual(str(block), expected)

    def test_multiline_statements(self):
        """Test multiline statement formatting."""
        block = CodeBlock.builder().add_statement("System.out.println(\n$S\n)", "Hello, World!").build()

        expected = 'System.out.println(\n    "Hello, World!"\n    );\n'
        self.assertEqual(str(block), expected)

    def test_multiline_statements_with_builders(self):
        block = CodeBlock.builder().add_statement("System\n.out\n.println($S)", "Hello, World!").build()
        block2 = (
            CodeBlock.builder()
            .begin_statement("System")
            .add_statement_item(".out")
            .add_statement_item(".println($S)", "Hello, World!")
            .end_statement()
            .build()
        )
        block3 = (
            CodeBlock.builder()
            .begin_statement("System")
            .add_statement_item(".out\n.println($S)", "Hello, World!")
            .end_statement()
            .build()
        )
        expected = 'System\n    .out\n    .println("Hello, World!");\n'
        self.assertEqual(str(block), expected)
        self.assertEqual(str(block2), expected)
        self.assertEqual(str(block3), expected)

    def test_begin_statement_no_end_statement_throws_error(self):
        with self.assertRaises(ValueError):
            CodeBlock.builder().begin_statement("Hello").build()

    def test_emit_as_java_doc(self):
        """Test emitting as JavaDoc."""
        block = CodeBlock.of("$L", "Hello, World!")

        self.assertEqual(block.javadoc(), "/**\n * Hello, World!\n */")

    def test_add_javadoc(self):
        """Test adding JavaDoc to a code block."""
        block = CodeBlock.of("$L", "Hello, World!")
        block = CodeBlock.add_javadoc(block, " Hello, World!\n\n")
        writer = CodeWriter()
        block.emit_javadoc(writer)
        print(str(writer))
        self.assertEqual(str(writer), "/**\n * Hello, World! Hello, World!\n * \n * \n */")

    def test_add_javadoc_with_line_breaks(self):
        """Test adding JavaDoc with line breaks."""
        block = CodeBlock.add_javadoc_line(None, "One!\n")
        block = CodeBlock.add_javadoc_line(block, "Two!\nThree!\nFour!")
        writer = CodeWriter()
        block.emit_javadoc(writer)
        self.assertEqual(str(writer), "/**\n * One!\n * \n * Two!\n * Three!\n * Four!\n */")

    def test_add_raw_line(self):
        """Test adding raw code to a code block."""
        block = CodeBlock.builder().add_line("System.out.println($S);", "Hello, World!").build()
        self.assertEqual(str(block), 'System.out.println("Hello, World!");\n')


if __name__ == "__main__":
    unittest.main()
