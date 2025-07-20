# """
# Tests for utility functions.
# Equivalent to UtilTest.java
# """
# import unittest

# from pyjavapoet.util import character_literal, string_literal


# class UtilTest(unittest.TestCase):
#     """Test utility functions."""

#     def test_character_literal(self):
#         """Test character literal generation with proper escaping."""
#         # Basic characters
#         self.assertEqual(character_literal('a'), "'a'")
#         self.assertEqual(character_literal('Z'), "'Z'")
#         self.assertEqual(character_literal('0'), "'0'")
#         self.assertEqual(character_literal(' '), "' '")

#         # Special characters that need escaping
#         self.assertEqual(character_literal('\t'), "'\\t'")
#         self.assertEqual(character_literal('\n'), "'\\n'")
#         self.assertEqual(character_literal('\r'), "'\\r'")
#         self.assertEqual(character_literal('\b'), "'\\b'")
#         self.assertEqual(character_literal('\f'), "'\\f'")
#         self.assertEqual(character_literal('\''), "'\\'")
#         self.assertEqual(character_literal('\"'), "'\"'")  # Double quote doesn't need escaping in char
#         self.assertEqual(character_literal('\\'), "'\\\\'")

#         # Unicode escape sequences
#         self.assertEqual(character_literal('\0'), "'\\u0000'")
#         self.assertEqual(character_literal('\u0001'), "'\\u0001'")
#         self.assertEqual(character_literal('\u001f'), "'\\u001f'")
#         self.assertEqual(character_literal('\u007f'), "'\\u007f'")

#         # High Unicode values
#         self.assertEqual(character_literal('\u00a0'), "'\\u00a0'")  # Non-breaking space
#         self.assertEqual(character_literal('\u2603'), "'\\u2603'")  # Snowman

#         # Unicode outside Basic Multilingual Plane (if supported)
#         # Note: This depends on Python's Unicode handling
#         try:
#             result = character_literal('\U0001f4a9')  # Pile of poo emoji
#             self.assertTrue(result.startswith("'"))
#             self.assertTrue(result.endswith("'"))
#         except:
#             # May not be supported on all systems
#             pass

#     def test_string_literal(self):
#         """Test string literal generation with proper escaping."""
#         # Basic strings
#         self.assertEqual(string_literal("hello"), '"hello"')
#         self.assertEqual(string_literal(""), '""')
#         self.assertEqual(string_literal("world"), '"world"')

#         # Strings with special characters
#         self.assertEqual(string_literal("hello\tworld"), '"hello\\tworld"')
#         self.assertEqual(string_literal("hello\nworld"), '"hello\\nworld"')
#         self.assertEqual(string_literal("hello\rworld"), '"hello\\rworld"')
#         self.assertEqual(string_literal("hello\bworld"), '"hello\\bworld"')
#         self.assertEqual(string_literal("hello\fworld"), '"hello\\fworld"')
#         self.assertEqual(string_literal('hello"world'), '"hello\\"world"')
#         self.assertEqual(string_literal("hello\\world"), '"hello\\\\world"')

#         # Unicode characters
#         self.assertEqual(string_literal("café"), '"café"')
#         self.assertEqual(string_literal("世界"), '"世界"')
#         self.assertEqual(string_literal("\u2603"), '"☃"')  # Snowman (should not be escaped if printable)

#         # Control characters (should be escaped)
#         self.assertEqual(string_literal("hello\u0000world"), '"hello\\u0000world"')
#         self.assertEqual(string_literal("hello\u0001world"), '"hello\\u0001world"')
#         self.assertEqual(string_literal("hello\u001fworld"), '"hello\\u001fworld"')

#         # Mixed content
#         self.assertEqual(string_literal('He said "Hello\tworld!"'), '"He said \\"Hello\\tworld!\\""')

#         # Long strings (should handle without issue)
#         long_string = "a" * 1000
#         result = string_literal(long_string)
#         self.assertTrue(result.startswith('"'))
#         self.assertTrue(result.endswith('"'))
#         self.assertEqual(len(result), len(long_string) + 2)  # Original + 2 quotes

#     def test_character_literal_edge_cases(self):
#         """Test edge cases for character literal generation."""
#         # Null character
#         self.assertEqual(character_literal('\x00'), "'\\u0000'")

#         # Delete character
#         self.assertEqual(character_literal('\x7f'), "'\\u007f'")

#         # Non-printable characters in extended ASCII
#         self.assertEqual(character_literal('\x80'), "'\\u0080'")
#         self.assertEqual(character_literal('\xff'), "'\\u00ff'")

#     def test_string_literal_edge_cases(self):
#         """Test edge cases for string literal generation."""
#         # String with only escape characters
#         self.assertEqual(string_literal("\t\n\r"), '"\\t\\n\\r"')

#         # String with mixed quotes
#         self.assertEqual(string_literal("'\""), '"\'\\"')

#         # String with backslashes at end
#         self.assertEqual(string_literal("test\\"), '"test\\\\"')

#         # String with Unicode and ASCII mixed
#         self.assertEqual(string_literal("Hello\u2603World\tTest"), '"Hello☃World\\tTest"')

#     def test_character_literal_printable_ascii(self):
#         """Test all printable ASCII characters."""
#         # Test basic printable ASCII range
#         for i in range(32, 127):  # Space to tilde
#             char = chr(i)
#             result = character_literal(char)

#             # Should always be wrapped in single quotes
#             self.assertTrue(result.startswith("'"))
#             self.assertTrue(result.endswith("'"))

#             # Special cases that need escaping
#             if char in "'\\":
#                 self.assertIn("\\", result)
#             elif char in '"':
#                 # Double quote doesn't need escaping in character literal
#                 self.assertEqual(result, "'\"'")

#     def test_string_literal_all_escapes(self):
#         """Test all standard escape sequences in strings."""
#         escape_mappings = {
#             '\t': '\\t',
#             '\n': '\\n',
#             '\r': '\\r',
#             '\b': '\\b',
#             '\f': '\\f',
#             '"': '\\"',
#             '\\': '\\\\'
#         }

#         for char, escape_seq in escape_mappings.items():
#             result = string_literal(char)
#             expected = f'"{escape_seq}"'
#             self.assertEqual(result, expected, f"Failed for character: {repr(char)}")

#     def test_unicode_normalization(self):
#         """Test Unicode normalization in literals."""
#         # Test that Unicode characters are handled consistently
#         unicode_chars = ['é', 'ñ', '中', '🎉', '∑', '∞']

#         for char in unicode_chars:
#             # Character literal
#             char_result = character_literal(char)
#             self.assertTrue(char_result.startswith("'"))
#             self.assertTrue(char_result.endswith("'"))

#             # String literal
#             str_result = string_literal(char)
#             self.assertTrue(str_result.startswith('"'))
#             self.assertTrue(str_result.endswith('"'))

#     def test_literal_consistency(self):
#         """Test consistency between character and string literals."""
#         test_chars = ['a', 'Z', '0', ' ', '\t', '\n', '\'', '"', '\\', '\u2603']

#         for char in test_chars:
#             char_literal = character_literal(char)
#             str_literal = string_literal(char)

#             # Extract the content (remove outer quotes)
#             char_content = char_literal[1:-1]  # Remove single quotes
#             str_content = str_literal[1:-1]    # Remove double quotes

#             # For most characters, the escaping should be similar
#             # Exception: double quote needs escaping in strings but not in chars
#             if char != '"':
#                 self.assertEqual(char_content, str_content,
#                                f"Inconsistent escaping for {repr(char)}: char={char_literal}, str={str_literal}")


# if __name__ == "__main__":
#     unittest.main()
