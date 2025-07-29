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

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.type_name import ClassName


class AnnotationSpecTest(unittest.TestCase):
    """Test the AnnotationSpec class."""

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation")).build()
        b = AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation")).build()

        self.assertEqual(hash(a), hash(b))

        a = (
            AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation"))
            .add_member("value", "$S", "123")
            .build()
        )
        b = (
            AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation"))
            .add_member("value", "$S", "123")
            .build()
        )

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_empty_array(self):
        """Test empty array handling."""
        builder = AnnotationSpec.builder(ClassName.get("com.example", "HasDefaultsAnnotation"))
        builder.add_member("n", "$L", "{}")
        builder.add_member("m", "$L", "{}")
        annotation_str = str(builder.build())
        self.assertIn("n = {}", annotation_str)
        self.assertIn("m = {}", annotation_str)
        self.assertIn("@HasDefaultsAnnotation", annotation_str)

    def test_dynamic_array_of_enum_constants(self):
        """Test dynamic array of enum constants."""
        breakfast_class = ClassName.get("com.example", "Breakfast")
        builder = AnnotationSpec.builder(ClassName.get("com.example", "HasDefaultsAnnotation"))
        builder.add_member("n", "$T.$L", breakfast_class, "PANCAKES")

        result = str(builder.build())
        expected_part = "Breakfast.PANCAKES"

        self.assertIn(expected_part, result)

    def test_to_builder(self):
        """Test annotation to builder conversion."""
        original = (
            AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation"))
            .add_member("value", "$S", "original")
            .build()
        )

        modified = original.to_builder().add_member("extra", "$L", "123").build()

        original_str = str(original)
        modified_str = str(modified)

        self.assertIn('"original"', original_str)
        self.assertIn('value = "original"', modified_str)
        self.assertIn("extra = 123", modified_str)
        self.assertNotIn("extra = 123", original_str)

    def test_requires_valid_member_name(self):
        """Test that invalid member names are rejected."""
        builder = AnnotationSpec.builder(ClassName.get("com.example", "TestAnnotation"))
        with self.assertRaises(ValueError):
            builder.add_member("@", "$L", "")

    def test_annotation_with_class_member(self):
        """Test annotation with class members."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "MyAnnotation"))
            .add_member("value", "$T.class", ClassName.get("java.lang", "String"))
            .build()
        )

        result = str(annotation)
        self.assertIn("String.class", result)

    def test_nested_annotation(self):
        """Test nested annotation."""
        inner = AnnotationSpec.builder(ClassName.get("com.example", "Inner")).add_member("value", "$S", "test").build()
        outer = AnnotationSpec.builder(ClassName.get("com.example", "Outer")).add_member("inner", "$L", inner).build()

        result = str(outer)
        self.assertIn('@Inner("test")', result)

    def test_array_values(self):
        """Test array values in annotations."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "ArrayAnnotation"))
            .add_member("values", "{$S, $S, $S}", "one", "two", "three")
            .build()
        )

        result = str(annotation)
        self.assertIn('values = {"one", "two", "three"}', result)

    def test_primitive_values(self):
        """Test primitive values in annotations."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "Primitives"))
            .add_member("intVal", "$L", 42)
            .add_member("floatVal", "$Lf", 3.14)
            .add_member("boolVal", "$L", True)
            .add_member("longVal", "$LL", 123456789)
            .build()
        )

        result = str(annotation)
        self.assertIn("intVal = 42", result)
        self.assertIn("floatVal = 3.14f", result)
        self.assertIn("boolVal = true", result)
        self.assertIn("longVal = 123456789L", result)

    def test_character_literals(self):
        """Test character literals in annotations."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "CharAnnotation"))
            .add_member("ch", "'$L'", "a")
            .add_member("escaped", "'$L'", "\t")
            .build()
        )

        result = str(annotation)
        self.assertIn("ch = 'a'", result)
        self.assertIn("escaped = '\t'", result)


if __name__ == "__main__":
    unittest.main()
