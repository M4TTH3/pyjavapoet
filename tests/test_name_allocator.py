# """
# Tests for NameAllocator functionality.
# Equivalent to NameAllocatorTest.java
# """
# import unittest

# from pyjavapoet.name_allocator import NameAllocator


# class NameAllocatorTest(unittest.TestCase):
#     """Test the NameAllocator class."""

#     def test_usage(self):
#         """Test basic usage."""
#         name_allocator = NameAllocator()

#         # Allocate names
#         self.assertEqual(name_allocator.new_name("foo", "tag1"), "foo")
#         self.assertEqual(name_allocator.new_name("bar", "tag2"), "bar")

#         # Get allocated names
#         self.assertEqual(name_allocator.get("tag1"), "foo")
#         self.assertEqual(name_allocator.get("tag2"), "bar")

#     def test_name_collision(self):
#         """Test name collision handling."""
#         name_allocator = NameAllocator()

#         # First allocation gets the name as-is
#         self.assertEqual(name_allocator.new_name("foo", "tag1"), "foo")

#         # Second allocation gets a modified name
#         self.assertEqual(name_allocator.new_name("foo", "tag2"), "foo_")

#         # Third allocation gets another modified name
#         self.assertEqual(name_allocator.new_name("foo", "tag3"), "foo__")

#     def test_name_collision_with_tag(self):
#         """Test name collision with different tags."""
#         name_allocator = NameAllocator()

#         name_allocator.new_name("foo", "tag1")
#         name_allocator.new_name("foo", "tag2")

#         # Same tag should return same name
#         self.assertEqual(name_allocator.get("tag1"), "foo")
#         self.assertEqual(name_allocator.get("tag2"), "foo_")

#     def test_character_mapping_substitute(self):
#         """Test character substitution mapping."""
#         name_allocator = NameAllocator()

#         # Test substitution of invalid Java identifier characters
#         result = name_allocator.new_name("a-b.c+d", "tag")

#         # Should substitute invalid characters
#         self.assertNotIn("-", result)
#         self.assertNotIn(".", result)
#         self.assertNotIn("+", result)
#         # Should use valid Java identifier characters
#         self.assertTrue(result.replace("_", "").isalnum())

#     def test_character_mapping_surrogate(self):
#         """Test surrogate character handling."""
#         name_allocator = NameAllocator()

#         # Test with Unicode surrogate pairs and other special characters
#         result = name_allocator.new_name("a\ud83d\ude00b", "tag")  # Unicode emoji

#         # Should handle Unicode characters appropriately
#         self.assertTrue(len(result) > 0)

#     def test_character_mapping_invalid_start_character(self):
#         """Test mapping of invalid start characters."""
#         name_allocator = NameAllocator()

#         # Java identifiers cannot start with digits
#         result = name_allocator.new_name("123abc", "tag")

#         # Should not start with digit
#         self.assertFalse(result[0].isdigit())

#     def test_character_mapping_dollar_sign(self):
#         """Test dollar sign handling."""
#         name_allocator = NameAllocator()

#         # Dollar sign is valid in Java identifiers
#         result = name_allocator.new_name("a$b", "tag")

#         # Should preserve dollar sign or map appropriately
#         self.assertTrue(len(result) > 0)

#     def test_java_keyword(self):
#         """Test Java keyword handling."""
#         name_allocator = NameAllocator()

#         # Java keywords should be modified
#         keywords = [
#             "abstract", "boolean", "break", "byte", "case", "catch", "char",
#             "class", "const", "continue", "default", "do", "double", "else",
#             "extends", "final", "finally", "float", "for", "goto", "if",
#             "implements", "import", "instanceof", "int", "interface", "long",
#             "native", "new", "package", "private", "protected", "public",
#             "return", "short", "static", "strictfp", "super", "switch",
#             "synchronized", "this", "throw", "throws", "transient", "try",
#             "void", "volatile", "while"
#         ]

#         for keyword in keywords:
#             result = name_allocator.new_name(keyword, f"tag_{keyword}")
#             # Should not be the exact keyword
#             self.assertNotEqual(result, keyword)
#             # Should be a valid modification
#             self.assertTrue(len(result) > 0)

#     def test_tag_reuse_forbidden(self):
#         """Test that tag reuse is forbidden."""
#         name_allocator = NameAllocator()

#         name_allocator.new_name("foo", "tag")

#         # Reusing the same tag should raise an error
#         with self.assertRaises(ValueError):
#             name_allocator.new_name("bar", "tag")

#     def test_use_before_allocate_forbidden(self):
#         """Test that using a tag before allocation is forbidden."""
#         name_allocator = NameAllocator()

#         # Getting a tag that hasn't been allocated should raise an error
#         with self.assertRaises(KeyError):
#             name_allocator.get("non_existent_tag")

#     def test_clone_usage(self):
#         """Test cloning usage."""
#         original = NameAllocator()
#         original.new_name("foo", "tag1")
#         original.new_name("bar", "tag2")

#         # Clone the allocator
#         cloned = original.clone()

#         # Cloned allocator should have same allocations
#         self.assertEqual(cloned.get("tag1"), "foo")
#         self.assertEqual(cloned.get("tag2"), "bar")

#         # Modifications to clone shouldn't affect original
#         cloned.new_name("baz", "tag3")

#         with self.assertRaises(KeyError):
#             original.get("tag3")

#     def test_empty_string_name(self):
#         """Test empty string name handling."""
#         name_allocator = NameAllocator()

#         # Empty string should be handled (likely converted to valid identifier)
#         result = name_allocator.new_name("", "tag")

#         # Should get some valid identifier
#         self.assertTrue(len(result) > 0)
#         self.assertTrue(result.replace("_", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").isalpha() or result.startswith("_"))

#     def test_very_long_name(self):
#         """Test very long name handling."""
#         name_allocator = NameAllocator()

#         long_name = "a" * 1000
#         result = name_allocator.new_name(long_name, "tag")

#         # Should handle long names (might truncate or keep as-is)
#         self.assertTrue(len(result) > 0)

#     def test_unicode_name(self):
#         """Test Unicode name handling."""
#         name_allocator = NameAllocator()

#         unicode_name = "café_naïve_résumé"
#         result = name_allocator.new_name(unicode_name, "tag")

#         # Should handle Unicode appropriately
#         self.assertTrue(len(result) > 0)

#     def test_multiple_collisions(self):
#         """Test handling multiple name collisions."""
#         name_allocator = NameAllocator()

#         # Create many collisions
#         names = []
#         for i in range(10):
#             name = name_allocator.new_name("collision", f"tag{i}")
#             names.append(name)

#         # All names should be unique
#         self.assertEqual(len(names), len(set(names)))

#         # First should be original
#         self.assertEqual(names[0], "collision")

#     def test_name_with_numbers(self):
#         """Test names that already contain numbers."""
#         name_allocator = NameAllocator()

#         # Allocate name with numbers
#         result1 = name_allocator.new_name("foo123", "tag1")
#         result2 = name_allocator.new_name("foo123", "tag2")

#         self.assertNotEqual(result1, result2)
#         self.assertEqual(result1, "foo123")

#     def test_preserve_case(self):
#         """Test that case is preserved where possible."""
#         name_allocator = NameAllocator()

#         result = name_allocator.new_name("CamelCase", "tag")

#         # Should preserve original casing
#         self.assertIn("CamelCase", result)


# if __name__ == "__main__":
#     unittest.main()
