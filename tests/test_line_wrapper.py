# """
# Tests for LineWrapper functionality.
# Equivalent to LineWrapperTest.java
# """
# import unittest

# from pyjavapoet.line_wrapper import LineWrapper


# class LineWrapperTest(unittest.TestCase):
#     """Test the LineWrapper class."""

#     def test_wrap(self):
#         """Test basic wrapping functionality."""
#         wrapper = LineWrapper(width=10, indent="  ")
#         wrapper.append("abcdefghijklmnop")
#         result = str(wrapper)

#         # Should wrap the long text
#         lines = result.split('\n')
#         self.assertTrue(len(lines) > 1)
#         self.assertTrue(all(len(line.strip()) <= 10 for line in lines if line.strip()))

#     def test_no_wrap(self):
#         """Test no wrapping for short text."""
#         wrapper = LineWrapper(width=20, indent="  ")
#         wrapper.append("short")
#         result = str(wrapper)

#         self.assertEqual(result, "short")

#     def test_zero_width_no_wrap(self):
#         """Test zero-width space with no wrapping needed."""
#         wrapper = LineWrapper(width=20, indent="  ")
#         wrapper.append("method")
#         wrapper.zero_width_space()
#         wrapper.append("Name")
#         result = str(wrapper)

#         self.assertEqual(result, "methodName")

#     def test_no_space_wrap_max(self):
#         """Test wrapping at zero-width space when at max width."""
#         wrapper = LineWrapper(width=6, indent="  ")
#         wrapper.append("method")  # 6 characters, at max width
#         wrapper.zero_width_space()
#         wrapper.append("Name")
#         result = str(wrapper)

#         # Should wrap at the zero-width space
#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "method")
#         self.assertEqual(lines[1], "  Name")

#     def test_multiple_write(self):
#         """Test multiple append operations."""
#         wrapper = LineWrapper(width=15, indent="  ")
#         wrapper.append("first")
#         wrapper.append(" ")
#         wrapper.append("second")
#         wrapper.append(" ")
#         wrapper.append("third")
#         result = str(wrapper)

#         self.assertIn("first second third", result)

#     def test_fencepost(self):
#         """Test fencepost edge case at exact width boundary."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("exact")  # Exactly 5 characters
#         wrapper.append("ly")
#         result = str(wrapper)

#         # Should wrap since adding "ly" would exceed width
#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "exact")

#     def test_fencepost_zero_width(self):
#         """Test fencepost with zero-width space."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("exact")  # Exactly 5 characters
#         wrapper.zero_width_space()
#         wrapper.append("ly")
#         result = str(wrapper)

#         # Should wrap at zero-width space
#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "exact")
#         self.assertEqual(lines[1], "  ly")

#     def test_overly_long_lines_without_leading_space(self):
#         """Test handling of overly long lines without leading space."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("verylongword")  # Longer than width
#         result = str(wrapper)

#         # Should still output the word even though it's too long
#         self.assertEqual(result, "verylongword")

#     def test_overly_long_lines_with_leading_space(self):
#         """Test handling of overly long lines with leading space."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("x")
#         wrapper.append(" ")
#         wrapper.append("verylongword")  # This will force a wrap due to space
#         result = str(wrapper)

#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "x")
#         self.assertEqual(lines[1], "  verylongword")

#     def test_overly_long_lines_with_leading_zero_width(self):
#         """Test overly long lines with leading zero-width space."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("x")
#         wrapper.zero_width_space()
#         wrapper.append("verylongword")
#         result = str(wrapper)

#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "x")
#         self.assertEqual(lines[1], "  verylongword")

#     def test_no_wrap_embedded_newlines(self):
#         """Test handling of embedded newlines without wrapping."""
#         wrapper = LineWrapper(width=20, indent="  ")
#         wrapper.append("first\nsecond")
#         result = str(wrapper)

#         lines = result.split('\n')
#         self.assertEqual(len(lines), 2)
#         self.assertEqual(lines[0], "first")
#         self.assertEqual(lines[1], "second")

#     def test_wrap_embedded_newlines(self):
#         """Test wrapping with embedded newlines."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("verylongfirst\nverylongsecond")
#         result = str(wrapper)

#         lines = result.split('\n')
#         self.assertGreaterEqual(len(lines), 2)
#         # First line should contain "verylongfirst"
#         self.assertIn("verylongfirst", lines[0])

#     def test_no_wrap_multiple_newlines(self):
#         """Test multiple consecutive newlines without wrapping."""
#         wrapper = LineWrapper(width=20, indent="  ")
#         wrapper.append("first\n\nsecond")
#         result = str(wrapper)

#         lines = result.split('\n')
#         self.assertEqual(len(lines), 3)
#         self.assertEqual(lines[0], "first")
#         self.assertEqual(lines[1], "")
#         self.assertEqual(lines[2], "second")

#     def test_wrap_multiple_newlines(self):
#         """Test multiple newlines with wrapping."""
#         wrapper = LineWrapper(width=5, indent="  ")
#         wrapper.append("verylongfirst\n\nverylongsecond")
#         result = str(wrapper)

#         lines = result.split('\n')
#         # Should have at least 3 lines (first, empty, second)
#         self.assertGreaterEqual(len(lines), 3)
#         empty_line_index = next(i for i, line in enumerate(lines) if line == "")
#         self.assertIsNotNone(empty_line_index)

#     def test_custom_indent_string(self):
#         """Test custom indent string."""
#         wrapper = LineWrapper(width=5, indent="\t\t")
#         wrapper.append("first")
#         wrapper.append(" ")
#         wrapper.append("second")
#         result = str(wrapper)

#         lines = result.split('\n')
#         if len(lines) > 1:
#             # Second line should use custom indent
#             self.assertTrue(lines[1].startswith("\t\t"))

#     def test_empty_wrapper(self):
#         """Test empty wrapper."""
#         wrapper = LineWrapper(width=10, indent="  ")
#         result = str(wrapper)

#         self.assertEqual(result, "")

#     def test_only_spaces(self):
#         """Test wrapper with only spaces."""
#         wrapper = LineWrapper(width=10, indent="  ")
#         wrapper.append("   ")
#         result = str(wrapper)

#         # Trailing spaces might be trimmed
#         self.assertTrue(len(result) <= 3)

#     def test_wrapping_preserves_content(self):
#         """Test that wrapping preserves all content."""
#         wrapper = LineWrapper(width=3, indent="  ")
#         original_text = "abcdefghijklmnopqrstuvwxyz"
#         wrapper.append(original_text)
#         result = str(wrapper)

#         # All characters should be preserved (ignoring whitespace changes)
#         result_chars = ''.join(result.split())
#         self.assertEqual(result_chars, original_text)


# if __name__ == "__main__":
#     unittest.main()
