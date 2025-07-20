"""
Tests for ClassName functionality.
Equivalent to ClassNameTest.java
"""

import unittest

from pyjavapoet.type_name import ClassName


class ClassNameTest(unittest.TestCase):
    """Test the ClassName class."""

    def test_best_guess_for_string_simple_class(self):
        """Test best guess for simple class names."""
        self.assertEqual(ClassName.best_guess("String"), ClassName.get("java.lang", "String"))

    def test_best_guess_non_ascii(self):
        """Test best guess with non-ASCII characters."""
        class_name = ClassName.best_guess("com.𝕯android.𝕸ctivⅈty")
        self.assertEqual(class_name.package_name, "com.𝕯android")
        self.assertEqual(class_name.simple_name, "𝕸ctivⅈty")

    def test_best_guess_for_string_nested_class(self):
        """Test best guess for nested classes."""
        self.assertEqual(ClassName.best_guess("java.util.Map.Entry"), ClassName.get("java.util", "Map", "Entry"))
        self.assertEqual(
            ClassName.best_guess("com.example.OuterClass.InnerClass"),
            ClassName.get("com.example", "OuterClass", "InnerClass"),
        )

    def test_best_guess_for_string_default_package(self):
        """Test best guess for default package classes."""
        self.assertEqual(ClassName.best_guess("SomeClass"), ClassName.get("", "SomeClass"))
        self.assertEqual(ClassName.best_guess("SomeClass.Nested"), ClassName.get("", "SomeClass", "Nested"))
        self.assertEqual(
            ClassName.best_guess("SomeClass.Nested.EvenMore"), ClassName.get("", "SomeClass", "Nested", "EvenMore")
        )

    def test_create_nested_class(self):
        """Test creating nested classes."""
        foo = ClassName.get("com.example", "Foo")
        bar = foo.nested_class("Bar")
        self.assertEqual(bar, ClassName.get("com.example", "Foo", "Bar"))

        baz = bar.nested_class("Baz")
        self.assertEqual(baz, ClassName.get("com.example", "Foo", "Bar", "Baz"))

    def test_peer_class(self):
        """Test peer class creation."""
        self.assertEqual(ClassName.get("java.lang", "Double").peer_class("Short"), ClassName.get("java.lang", "Short"))
        self.assertEqual(ClassName.get("", "Double").peer_class("Short"), ClassName.get("", "Short"))
        self.assertEqual(
            ClassName.get("a.b", "Combo", "Taco").peer_class("Burrito"), ClassName.get("a.b", "Combo", "Burrito")
        )

    def test_reflection_name(self):
        """Test reflection name generation."""
        self.assertEqual(ClassName.get("java.lang", "Object").reflection_name, "java.lang.Object")
        self.assertEqual(ClassName.get("java.lang", "Thread", "State").reflection_name, "java.lang.Thread$State")
        self.assertEqual(ClassName.get("java.util", "Map", "Entry").reflection_name, "java.util.Map$Entry")
        self.assertEqual(ClassName.get("", "Foo").reflection_name, "Foo")
        self.assertEqual(ClassName.get("", "Foo", "Bar", "Baz").reflection_name, "Foo$Bar$Baz")
        self.assertEqual(ClassName.get("a.b.c", "Foo", "Bar", "Baz").reflection_name, "a.b.c.Foo$Bar$Baz")

    def test_canonical_name(self):
        """Test canonical name generation."""
        self.assertEqual(ClassName.get("java.lang", "Object").canonical_name, "java.lang.Object")
        self.assertEqual(ClassName.get("java.lang", "Thread", "State").canonical_name, "java.lang.Thread.State")
        self.assertEqual(ClassName.get("java.util", "Map", "Entry").canonical_name, "java.util.Map.Entry")
        self.assertEqual(ClassName.get("", "Foo").canonical_name, "Foo")
        self.assertEqual(ClassName.get("", "Foo", "Bar", "Baz").canonical_name, "Foo.Bar.Baz")
        self.assertEqual(ClassName.get("a.b.c", "Foo", "Bar", "Baz").canonical_name, "a.b.c.Foo.Bar.Baz")

    def test_simple_name_and_enclosing_class(self):
        """Test simple name and enclosing class extraction."""
        object_class = ClassName.get("java.lang", "Object")
        self.assertEqual(object_class.simple_name, "Object")
        self.assertIsNone(object_class.enclosing_class_name)

        entry_class = ClassName.get("java.util", "Map", "Entry")
        self.assertEqual(entry_class.simple_name, "Entry")
        self.assertEqual(entry_class.enclosing_class_name, ClassName.get("java.util", "Map"))

    def test_package_name(self):
        """Test package name extraction."""
        self.assertEqual(ClassName.get("java.lang", "Object").package_name, "java.lang")
        self.assertEqual(ClassName.get("", "Object").package_name, "")
        self.assertEqual(ClassName.get("com.example", "Foo", "Bar").package_name, "com.example")

    def test_top_level_class_name(self):
        """Test top level class name extraction."""
        self.assertEqual(
            ClassName.get("java.util", "Map", "Entry").top_level_class_name, ClassName.get("java.util", "Map")
        )
        self.assertEqual(
            ClassName.get("java.lang", "Object").top_level_class_name, ClassName.get("java.lang", "Object")
        )

    def test_equals_and_hash_code(self):
        """Test equals and hash code."""
        a = ClassName.get("java.lang", "String")
        b = ClassName.get("java.lang", "String")
        c = ClassName.get("java.lang", "Object")

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)
        self.assertNotEqual(hash(a), hash(c))

    def test_string_representation(self):
        """Test string representation."""
        self.assertEqual(str(ClassName.get("java.lang", "String")), "java.lang.String")
        self.assertEqual(str(ClassName.get("", "String")), "String")
        self.assertEqual(str(ClassName.get("java.util", "Map", "Entry")), "java.util.Map.Entry")

    def test_is_boxed_primitive(self):
        """Test boxed primitive detection."""
        self.assertTrue(ClassName.get("java.lang", "Boolean").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Byte").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Character").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Double").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Float").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Integer").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Long").is_boxed_primitive())
        self.assertTrue(ClassName.get("java.lang", "Short").is_boxed_primitive())

        self.assertFalse(ClassName.get("java.lang", "String").is_boxed_primitive())
        self.assertFalse(ClassName.get("java.lang", "Object").is_boxed_primitive())

    def test_simple_names(self):
        """Test simple names list."""
        self.assertEqual(ClassName.get("java.lang", "Object").simple_names, ["Object"])
        self.assertEqual(ClassName.get("java.util", "Map", "Entry").simple_names, ["Map", "Entry"])
        self.assertEqual(ClassName.get("", "Foo", "Bar", "Baz").simple_names, ["Foo", "Bar", "Baz"])


if __name__ == "__main__":
    unittest.main()
