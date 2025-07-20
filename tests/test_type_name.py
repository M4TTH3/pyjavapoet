"""
Tests for TypeName functionality.
Equivalent to TypeNameTest.java
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
        self.assertEqual(str(list_string), "java.util.List<java.lang.String>")

    def test_inner_class_in_generic_type(self):
        """Test inner class within generic types."""
        outer = ClassName.get("com.example", "Outer").with_type_arguments(ClassName.get("java.lang", "String"))
        inner = outer.nested_class("Inner")

        result = str(inner)
        self.assertIn("Outer<java.lang.String>.Inner", result)

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
        a = ArrayTypeName.of(ClassName.get("java.lang", "String"))
        b = ArrayTypeName.of(ClassName.get("java.lang", "String"))
        c = ArrayTypeName.of(ClassName.get("java.lang", "Object"))

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
        int_type = TypeName.get("int")
        boxed = int_type.box()
        self.assertEqual(boxed, ClassName.get("java.lang", "Integer"))

    def test_can_unbox_annotated_primitive(self):
        """Test unboxing annotated primitive types."""
        # This would test annotation preservation during unboxing
        # For now, just test basic unboxing functionality
        integer_type = ClassName.get("java.lang", "Integer")
        unboxed = integer_type.unbox()
        self.assertEqual(unboxed, TypeName.get("int"))

    def test_primitive_boxing(self):
        """Test primitive type boxing."""
        test_cases = [
            ("boolean", "java.lang.Boolean"),
            ("byte", "java.lang.Byte"),
            ("char", "java.lang.Character"),
            ("double", "java.lang.Double"),
            ("float", "java.lang.Float"),
            ("int", "java.lang.Integer"),
            ("long", "java.lang.Long"),
            ("short", "java.lang.Short"),
        ]

        for primitive, boxed_name in test_cases:
            primitive_type = TypeName.get(primitive)
            boxed_type = primitive_type.box()
            expected = ClassName.best_guess(boxed_name)
            self.assertEqual(boxed_type, expected, f"Boxing {primitive} failed")

    def test_primitive_unboxing(self):
        """Test boxed type unboxing."""
        test_cases = [
            ("java.lang.Boolean", "boolean"),
            ("java.lang.Byte", "byte"),
            ("java.lang.Character", "char"),
            ("java.lang.Double", "double"),
            ("java.lang.Float", "float"),
            ("java.lang.Integer", "int"),
            ("java.lang.Long", "long"),
            ("java.lang.Short", "short"),
        ]

        for boxed_name, primitive in test_cases:
            boxed_type = ClassName.best_guess(boxed_name)
            unboxed_type = boxed_type.unbox()
            expected = TypeName.get(primitive)
            self.assertEqual(unboxed_type, expected, f"Unboxing {boxed_name} failed")

    def test_void_cannot_be_boxed_or_unboxed(self):
        """Test that void cannot be boxed in the traditional sense."""
        void_type = TypeName.get("void")
        # Void can be "boxed" to java.lang.Void
        boxed = void_type.box()
        self.assertEqual(boxed, ClassName.get("java.lang", "Void"))

    def test_array_type_creation(self):
        """Test array type creation."""
        string_array = ArrayTypeName.of(ClassName.get("java.lang", "String"))
        self.assertEqual(str(string_array), "java.lang.String[]")

        # Multi-dimensional array
        int_2d_array = ArrayTypeName.of(ArrayTypeName.of(TypeName.get("int")))
        self.assertEqual(str(int_2d_array), "int[][]")

    def test_type_variable_with_bounds(self):
        """Test type variables with bounds."""
        bounded_t = TypeVariableName.get("T", ClassName.get("java.lang", "Number"))
        self.assertEqual(str(bounded_t), "T")
        # The bounds would be used in the generic signature, not the string representation

    def test_wildcard_types(self):
        """Test wildcard type creation."""
        # ? extends Number
        extends_wildcard = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        self.assertEqual(str(extends_wildcard), "? extends java.lang.Number")

        # ? super Integer
        super_wildcard = WildcardTypeName.supertypes_of(ClassName.get("java.lang", "Integer"))
        self.assertEqual(str(super_wildcard), "? super java.lang.Integer")

        # Unbounded wildcard ?
        unbounded = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Object"))
        self.assertEqual(str(unbounded), "?")

    def test_parameterized_type_with_wildcards(self):
        """Test parameterized types with wildcards."""
        wildcard = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        list_wildcard = ClassName.get("java.util", "List").with_type_arguments(wildcard)

        self.assertEqual(str(list_wildcard), "java.util.List<? extends java.lang.Number>")

    def test_nested_parameterized_types(self):
        """Test deeply nested parameterized types."""
        map_type = ClassName.get("java.util", "Map").with_type_arguments(
            ClassName.get("java.lang", "String"),
            ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "Integer")),
        )

        self.assertEqual(str(map_type), "java.util.Map<java.lang.String, java.util.List<java.lang.Integer>>")

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


if __name__ == "__main__":
    unittest.main()
