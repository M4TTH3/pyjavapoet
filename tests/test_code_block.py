"""
Tests for CodeBlock functionality.
Equivalent to CodeBlockTest.java
"""

import unittest

from pyjavapoet.code_block import CodeBlock
from pyjavapoet.type_name import ClassName


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

    def test_of(self):
        """Test CodeBlock.of() factory method."""
        a = CodeBlock.of("$L taco", "delicious")
        self.assertEqual(str(a), "delicious taco")

    def test_is_empty(self):
        """Test isEmpty functionality."""
        self.assertTrue(CodeBlock.builder().is_empty())
        self.assertTrue(CodeBlock.builder().add("").is_empty())
        self.assertFalse(CodeBlock.builder().add(" ").is_empty())

    def test_indent_cannot_be_indexed(self):
        """Test that indent placeholders cannot have indices."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1>", "taco").build()
        self.assertIn("may not have an index", str(context.exception))

    def test_deindent_cannot_be_indexed(self):
        """Test that deindent placeholders cannot have indices."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1<", "taco").build()
        self.assertIn("may not have an index", str(context.exception))

    def test_dollar_sign_escape_cannot_be_indexed(self):
        """Test that dollar sign escape cannot have indices."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1$", "taco").build()
        self.assertIn("may not have an index", str(context.exception))

    def test_statement_beginning_cannot_be_indexed(self):
        """Test that statement beginning cannot have indices."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1[", "taco").build()
        self.assertIn("may not have an index", str(context.exception))

    def test_statement_ending_cannot_be_indexed(self):
        """Test that statement ending cannot have indices."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1]", "taco").build()
        self.assertIn("may not have an index", str(context.exception))

    def test_name_format_can_be_indexed(self):
        """Test that name format can be indexed."""
        block = CodeBlock.builder().add("$1N", "taco").build()
        self.assertEqual(str(block), "taco")

    def test_literal_format_can_be_indexed(self):
        """Test that literal format can be indexed."""
        block = CodeBlock.builder().add("$1L", "taco").build()
        self.assertEqual(str(block), "taco")

    def test_string_format_can_be_indexed(self):
        """Test that string format can be indexed."""
        block = CodeBlock.builder().add("$1S", "taco").build()
        self.assertEqual(str(block), '"taco"')

    def test_type_format_can_be_indexed(self):
        """Test that type format can be indexed."""
        block = CodeBlock.builder().add("$1T", ClassName.get("java.lang", "String")).build()
        self.assertEqual(str(block), "java.lang.String")

    def test_simple_named_argument(self):
        """Test simple named arguments."""
        args = {"text": "taco"}
        block = CodeBlock.builder().add_named("$text:S", args).build()
        self.assertEqual(str(block), '"taco"')

    def test_repeated_named_argument(self):
        """Test repeated named arguments."""
        args = {"text": "tacos"}
        block = CodeBlock.builder().add_named('"I like " + $text:S + ". Do you like " + $text:S + "?"', args).build()
        self.assertEqual(str(block), '"I like " + "tacos" + ". Do you like " + "tacos" + "?"')

    def test_named_and_no_arg_format(self):
        """Test named arguments with no-arg formats."""
        args = {"text": "tacos"}
        block = CodeBlock.builder().add_named("$>\n$text:L for $$3.50", args).build()
        self.assertEqual(str(block), "\n  tacos for $3.50")

    def test_missing_named_argument(self):
        """Test missing named arguments."""
        args = {}
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add_named("$text:S", args).build()
        self.assertIn("Missing named argument for $text", str(context.exception))

    def test_lower_case_named(self):
        """Test that named arguments must start with lowercase."""
        args = {"Text": "tacos"}
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add_named("$Text:S", args).build()
        self.assertIn("must start with a lowercase character", str(context.exception))

    def test_multiple_named_arguments(self):
        """Test multiple named arguments."""
        args = {"pipe": ClassName.get("java.lang", "System"), "text": "tacos"}
        block = CodeBlock.builder().add_named('$pipe:T.out.println("Let\'s eat some $text:L");', args).build()
        self.assertEqual(str(block), 'java.lang.System.out.println("Let\'s eat some tacos");')

    def test_named_newline(self):
        """Test named arguments with newlines."""
        args = {"clazz": ClassName.get("java.lang", "Integer")}
        block = CodeBlock.builder().add_named("$clazz:T\n", args).build()
        self.assertEqual(str(block), "java.lang.Integer\n")

    def test_dangling_named(self):
        """Test dangling named arguments."""
        args = {"clazz": ClassName.get("java.lang", "Integer")}
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add_named("$clazz:T$", args).build()
        self.assertIn("dangling $ at end", str(context.exception))

    def test_index_too_high(self):
        """Test index too high error."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$2T", ClassName.get("java.lang", "String")).build()
        self.assertIn("index 2", str(context.exception))
        self.assertIn("not in range", str(context.exception))

    def test_index_is_zero(self):
        """Test zero index error."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$0T", ClassName.get("java.lang", "String")).build()
        self.assertIn("index 0", str(context.exception))
        self.assertIn("not in range", str(context.exception))

    def test_index_is_negative(self):
        """Test negative index error."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$-1T", ClassName.get("java.lang", "String")).build()
        self.assertIn("invalid format string", str(context.exception))

    def test_index_without_format_type(self):
        """Test index without format type."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1", ClassName.get("java.lang", "String")).build()
        self.assertIn("dangling format characters", str(context.exception))

    def test_index_without_format_type_not_at_string_end(self):
        """Test index without format type not at string end."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1 taco", ClassName.get("java.lang", "String")).build()
        self.assertIn("invalid format string", str(context.exception))

    def test_index_but_no_arguments(self):
        """Test index with no arguments."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$1T").build()
        self.assertIn("index 1", str(context.exception))
        self.assertIn("not in range", str(context.exception))

    def test_format_indicator_alone(self):
        """Test format indicator alone."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$", ClassName.get("java.lang", "String")).build()
        self.assertIn("dangling format characters", str(context.exception))

    def test_format_indicator_without_index_or_format_type(self):
        """Test format indicator without index or format type."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.builder().add("$ tacoString", ClassName.get("java.lang", "String")).build()
        self.assertIn("invalid format string", str(context.exception))

    def test_same_index_can_be_used_with_different_formats(self):
        """Test same index with different formats."""
        block = CodeBlock.builder().add("$1T.out.println($1S)", ClassName.get("java.lang", "System")).build()
        self.assertEqual(str(block), 'java.lang.System.out.println("java.lang.System")')

    def test_join(self):
        """Test joining code blocks."""
        code_blocks = [
            CodeBlock.of("$S", "hello"),
            CodeBlock.of("$T", ClassName.get("world", "World")),
            CodeBlock.of("need tacos"),
        ]
        joined = CodeBlock.join(code_blocks, " || ")
        self.assertEqual(str(joined), '"hello" || world.World || need tacos')

    def test_joining_collector(self):
        """Test joining with stream collector pattern."""
        code_blocks = [
            CodeBlock.of("$S", "hello"),
            CodeBlock.of("$T", ClassName.get("world", "World")),
            CodeBlock.of("need tacos"),
        ]
        # Python equivalent of stream().collect(CodeBlock.joining())
        joined = CodeBlock.join(code_blocks, " || ")
        self.assertEqual(str(joined), '"hello" || world.World || need tacos')

    def test_joining_single(self):
        """Test joining single code block."""
        code_blocks = [CodeBlock.of("$S", "hello")]
        joined = CodeBlock.join(code_blocks, " || ")
        self.assertEqual(str(joined), '"hello"')

    def test_joining_with_prefix_and_suffix(self):
        """Test joining with prefix and suffix."""
        code_blocks = [
            CodeBlock.of("$S", "hello"),
            CodeBlock.of("$T", ClassName.get("world", "World")),
            CodeBlock.of("need tacos"),
        ]
        joined = CodeBlock.join(code_blocks, " || ", "start {", "} end")
        self.assertEqual(str(joined), 'start {"hello" || world.World || need tacos} end')

    def test_too_many_arguments(self):
        """Test too many arguments error."""
        with self.assertRaises(ValueError) as context:
            CodeBlock.of("test", 1)
        self.assertIn("unused arguments", str(context.exception))

        with self.assertRaises(ValueError) as context:
            CodeBlock.of("test", 1, 2)
        self.assertIn("unused arguments", str(context.exception))

        with self.assertRaises(ValueError) as context:
            CodeBlock.of("test $L", 2, 3)
        self.assertIn("unused arguments", str(context.exception))

    def test_clear(self):
        """Test clearing code block."""
        block = CodeBlock.builder().add_statement("$S", "Test string").clear().build()
        self.assertEqual(str(block), "")

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

    def test_indentation(self):
        """Test manual indentation."""
        block = CodeBlock.builder().add("start\n").indent().add("middle\n").unindent().add("end\n").build()

        expected = "start\n  middle\nend\n"
        self.assertEqual(str(block), expected)


if __name__ == "__main__":
    unittest.main()
