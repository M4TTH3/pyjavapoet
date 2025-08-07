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

from pyjavapoet.type_name import (
    ArrayTypeName,
    ClassName,
    ParameterizedTypeName,
    TypeName,
    TypeVariableName,
    WildcardTypeName,
)


class TypeNameTest(unittest.TestCase):
    """Test the TypeName class and its subclasses."""

    def test_generic_type(self):
        """Test generic type creation."""
        list_string = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        self.assertIsInstance(list_string, ParameterizedTypeName)
        self.assertEqual(str(list_string), "List<String>")

    def test_inner_class_in_generic_type(self):
        """Test inner class within generic types."""
        outer = ClassName.get("com.example", "Outer").with_type_arguments(ClassName.get("java.lang", "String"))
        inner = outer.nested_class("Inner")

        result = str(inner)
        self.assertIn("Outer<String>.Inner", result)

    def test_equals_and_hash_code_primitive(self):
        """Test equals and hash code for primitive types."""
        a = TypeName.get("int")
        b = TypeName.get("int")
        c = TypeName.get("long")

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_equals_and_hash_code_class_name(self):
        """Test equals and hash code for class names."""
        a = ClassName.get("java.lang", "String")
        b = ClassName.get("java.lang", "String")
        c = ClassName.get("java.lang", "Object")

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_equals_and_hash_code_array_type_name(self):
        """Test equals and hash code for array types."""
        a = ArrayTypeName.get(ClassName.get("java.lang", "String"))
        b = ArrayTypeName.get(ClassName.get("java.lang", "String"))
        c = ArrayTypeName.get(ClassName.get("java.lang", "Object"))

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_equals_and_hash_code_parameterized_type_name(self):
        """Test equals and hash code for parameterized types."""
        a = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        b = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        c = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "Integer"))

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_equals_and_hash_code_type_variable_name(self):
        """Test equals and hash code for type variables."""
        a = TypeVariableName.get("T")
        b = TypeVariableName.get("T")
        c = TypeVariableName.get("U")

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_equals_and_hash_code_wildcard_type_name(self):
        """Test equals and hash code for wildcard types."""
        a = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        b = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        c = WildcardTypeName.supertypes_of(ClassName.get("java.lang", "Number"))

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, c)

    def test_get_with_type_or_none(self):
        """Test get with type or none."""
        self.assertEqual(TypeName.get(bool), ClassName.BOOLEAN)
        self.assertEqual(TypeName.get(int), ClassName.INTEGER)
        self.assertEqual(TypeName.get(float), ClassName.FLOAT)
        self.assertEqual(TypeName.get(str), ClassName.STRING)
        self.assertEqual(TypeName.get(list), ClassName.LIST)
        self.assertEqual(TypeName.get(dict), ClassName.MAP)
        self.assertEqual(TypeName.get(set), ClassName.SET)
        self.assertEqual(TypeName.get(tuple), ClassName.LIST)
        self.assertEqual(TypeName.get(None), ClassName.VOID)

    def test_is_primitive(self):
        """Test primitive type detection."""
        self.assertTrue(TypeName.get("boolean").is_primitive())
        self.assertTrue(TypeName.get("byte").is_primitive())
        self.assertTrue(TypeName.get("char").is_primitive())
        self.assertTrue(TypeName.get("double").is_primitive())
        self.assertTrue(TypeName.get("float").is_primitive())
        self.assertTrue(TypeName.get("int").is_primitive())
        self.assertTrue(TypeName.get("long").is_primitive())
        self.assertTrue(TypeName.get("short").is_primitive())
        self.assertTrue(TypeName.get("void").is_primitive())

        self.assertFalse(ClassName.get("java.lang", "String").is_primitive())
        self.assertFalse(ClassName.get("java.lang", "Object").is_primitive())

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
        self.assertTrue(ClassName.get("java.lang", "Void").is_boxed_primitive())

        self.assertFalse(ClassName.get("java.lang", "String").is_boxed_primitive())
        self.assertFalse(ClassName.get("java.lang", "Object").is_boxed_primitive())

    def test_can_box_annotated_primitive(self):
        """Test boxing annotated primitive types."""
        # This would test annotation preservation during boxing
        # For now, just test basic boxing functionality
        types = [
            (ClassName.INTEGER, ClassName.get("java.lang", "Integer")),
            (ClassName.BOOLEAN, ClassName.get("java.lang", "Boolean")),
            (ClassName.FLOAT, ClassName.get("java.lang", "Float")),
            (ClassName.LONG, ClassName.get("java.lang", "Long")),
            (ClassName.SHORT, ClassName.get("java.lang", "Short")),
            (ClassName.DOUBLE, ClassName.get("java.lang", "Double")),
            (ClassName.VOID, ClassName.get("java.lang", "Void")),
            (ClassName.CHAR, ClassName.get("java.lang", "Character")),
            (ClassName.BYTE, ClassName.get("java.lang", "Byte")),
        ]
        for t, c in types:
            boxed = t.to_type_param()
            print(boxed)
            self.assertEqual(boxed, c)

    def test_array_type_creation(self):
        """Test array type creation."""
        string_array = ArrayTypeName.get(ClassName.get("java.lang", "String"))
        self.assertEqual(str(string_array), "String[]")

        # Multi-dimensional array
        int_2d_array = ArrayTypeName.get(ArrayTypeName.get(TypeName.get("int")))
        self.assertEqual(str(int_2d_array), "int[][]")

    def test_type_variable_with_bounds(self):
        """Test type variables with bounds."""
        bounded_t = TypeVariableName.get("T", ClassName.get("java.lang", "Number"))
        self.assertEqual(str(bounded_t), "T extends Number")
        # The bounds would be used in the generic signature, not the string representation

    def test_wildcard_types(self):
        """Test wildcard type creation."""
        # ? extends Number
        extends_wildcard = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        self.assertEqual(str(extends_wildcard), "? extends Number")

        # ? super Integer
        super_wildcard = WildcardTypeName.supertypes_of(ClassName.get("java.lang", "Integer"))
        self.assertEqual(str(super_wildcard), "? super Integer")

        # Unbounded wildcard ?
        unbounded = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Object"))
        self.assertEqual(str(unbounded), "?")

    def test_parameterized_type_with_wildcards(self):
        """Test parameterized types with wildcards."""
        wildcard = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        list_wildcard = ClassName.get("java.util", "List").with_type_arguments(wildcard)

        self.assertEqual(str(list_wildcard), "List<? extends Number>")

    def test_parameterized_type_with_primitives(self):
        types = [
            (ClassName.INTEGER, ClassName.get("java.lang", "Integer")),
            (ClassName.BOOLEAN, ClassName.get("java.lang", "Boolean")),
            (ClassName.FLOAT, ClassName.get("java.lang", "Float")),
            (ClassName.LONG, ClassName.get("java.lang", "Long")),
            (ClassName.SHORT, ClassName.get("java.lang", "Short")),
            (ClassName.DOUBLE, ClassName.get("java.lang", "Double")),
            (ClassName.VOID, ClassName.get("java.lang", "Void")),
            (ClassName.CHAR, ClassName.get("java.lang", "Character")),
            (ClassName.BYTE, ClassName.get("java.lang", "Byte")),
        ]
        list_type = ClassName.get("java.util", "List")
        for t, c in types:
            new_type = list_type.with_type_arguments(t)
            self.assertIn(c.simple_name, str(new_type))
            self.assertNotIn(t.simple_name, str(new_type))

    def test_nested_parameterized_types(self):
        """Test deeply nested parameterized types."""
        map_type = ClassName.get("java.util", "Map").with_type_arguments(
            ClassName.get("java.lang", "String"),
            ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "Integer")),
        )

        self.assertEqual(str(map_type), "Map<String, List<Integer>>")

    def test_get_method_with_class_type(self):
        """Test TypeName.get() with different input types."""
        # String class name
        type1 = TypeName.get("java.lang.String")
        self.assertEqual(str(type1), "java.lang.String")

        # Primitive
        type2 = TypeName.get("int")
        self.assertEqual(str(type2), "int")

        # Array notation
        type3 = TypeName.get("int[]")
        self.assertEqual(str(type3), "int[]")

    def test_string_representation_consistency(self):
        """Test that string representation is consistent."""
        type_name = ClassName.get("com.example", "TestClass", "InnerClass")
        str1 = str(type_name)
        str2 = str(type_name)
        self.assertEqual(str1, str2)


class ClassNameTest(unittest.TestCase):
    """Test the ClassName class."""

    def test_best_guess_for_string_simple_class(self):
        """Test best guess for simple class names."""
        self.assertEqual(ClassName.get_from_fqcn("String"), ClassName.get("java.lang", "String"))

    def test_best_guess_non_ascii(self):
        """Test best guess with non-ASCII characters."""
        class_name = ClassName.get_from_fqcn("com.𝕯android.𝕸ctivⅈty")
        self.assertEqual(class_name.package_name, "com.𝕯android")
        self.assertEqual(class_name.simple_name, "𝕸ctivⅈty")

    def test_best_guess_for_string_nested_class(self):
        """Test best guess for nested classes."""
        self.assertEqual(ClassName.get_from_fqcn("java.util.Map.Entry"), ClassName.get("java.util", "Map", "Entry"))
        self.assertEqual(
            ClassName.get_from_fqcn("com.example.OuterClass.InnerClass"),
            ClassName.get("com.example", "OuterClass", "InnerClass"),
        )

    def test_best_guess_for_string_default_package(self):
        """Test best guess for default package classes."""
        self.assertEqual(ClassName.get_from_fqcn("SomeClass"), ClassName.get("", "SomeClass"))
        self.assertEqual(ClassName.get_from_fqcn("SomeClass.Nested"), ClassName.get("", "SomeClass", "Nested"))
        self.assertEqual(
            ClassName.get_from_fqcn("SomeClass.Nested.EvenMore"), ClassName.get("", "SomeClass", "Nested", "EvenMore")
        )

    def test_create_nested_class(self):
        """Test creating nested classes."""
        foo = ClassName.get("com.example", "Foo")
        bar = foo.nested_class("Bar")
        self.assertEqual(bar, ClassName.get("com.example", "Foo", "Bar"))

        baz = bar.nested_class("Baz")
        self.assertEqual(baz, ClassName.get("com.example", "Foo", "Bar", "Baz"))
        self.assertEqual(str(baz), "com.example.Foo.Bar.Baz")

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
        self.assertEqual(ClassName.get("", "Object").package_name, "java.lang")
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
        self.assertEqual(str(ClassName.get("", "String")), "java.lang.String")
        self.assertEqual(str(ClassName.get("java.util", "Map", "Entry")), "java.util.Map.Entry")

    def test_to_type_param(self):
        """Test type parameter conversion."""
        self.assertEqual(ClassName.get("java.lang", "Boolean").to_type_param(), ClassName.get("java.lang", "Boolean"))
        self.assertEqual(ClassName.get("java.lang", "Byte").to_type_param(), ClassName.get("java.lang", "Byte"))
        self.assertEqual(
            ClassName.get("java.lang", "Character").to_type_param(), ClassName.get("java.lang", "Character")
        )
        self.assertEqual(ClassName.get("java.lang", "Double").to_type_param(), ClassName.get("java.lang", "Double"))
        self.assertEqual(ClassName.get("java.lang", "Float").to_type_param(), ClassName.get("java.lang", "Float"))

    def test_simple_names(self):
        """Test simple names list."""
        self.assertEqual(ClassName.get("java.lang", "Object").simple_names, ["Object"])
        self.assertEqual(ClassName.get("java.util", "Map", "Entry").simple_names, ["Map", "Entry"])
        self.assertEqual(ClassName.get("", "Foo", "Bar", "Baz").simple_names, ["Foo", "Bar", "Baz"])

    def test_nested_name(self):
        """Test nested name generation."""
        self.assertEqual(ClassName.get("java.lang", "Object").nested_name, "Object")
        self.assertEqual(ClassName.get("java.util", "Map", "Entry").nested_name, "Map.Entry")
        self.assertEqual(ClassName.get("", "Foo", "Bar", "Baz").nested_name, "Foo.Bar.Baz")
        self.assertEqual(ClassName.get("a.b.c", "Foo", "Bar", "Baz").nested_name, "Foo.Bar.Baz")


if __name__ == "__main__":
    unittest.main()
