"""
Tests for file reading functionality.
Equivalent to FileReadingTest.java
"""

import os
import tempfile
import unittest

from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


class FileReadingTest(unittest.TestCase):
    """Test file reading functionality."""

    def setUp(self):
        """Set up test with a sample Java file."""
        self.temp_dir = tempfile.mkdtemp()

        # Create a sample Java file
        method = (
            MethodSpec.method_builder("main")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
            .returns("void")
            .add_parameter("String[]", "args")
            .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Hello, World!")
            .build()
        )

        type_spec = (
            TypeSpec.class_builder("HelloWorld")
            .add_modifiers(Modifier.PUBLIC, Modifier.FINAL)
            .add_method(method)
            .build()
        )

        self.java_file = JavaFile.builder("com.example", type_spec).build()
        self.file_path = self.java_file.write_to_path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_java_file_object_uri(self):
        """Test JavaFileObject URI generation."""
        # In Java, this tests javax.tools.JavaFileObject
        # In Python, we'll test file path/URI generation

        # Different package structures should generate different URIs/paths
        test_cases = [
            ("", "Test", "Test.java"),
            ("com.example", "Test", os.path.join("com", "example", "Test.java")),
            ("deeply.nested.package", "Test", os.path.join("deeply", "nested", "package", "Test.java")),
        ]

        for package, class_name, expected_relative_path in test_cases:
            type_spec = TypeSpec.class_builder(class_name).build()
            java_file = JavaFile.builder(package, type_spec).build()

            relative_path = java_file.get_relative_path()
            self.assertEqual(relative_path, expected_relative_path)

    def test_java_file_object_kind(self):
        """Test JavaFileObject kind detection."""
        # Test that we can identify Java source files
        self.assertTrue(self.file_path.name.endswith(".java"))

        # Test file extension handling
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        relative_path = java_file.get_relative_path()
        self.assertTrue(relative_path.endswith(".java"))

    def test_java_file_object_character_content(self):
        """Test reading character content."""
        # Read the file we created
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain expected elements
        self.assertIn("package com.example;", content)
        self.assertIn("public final class HelloWorld", content)
        self.assertIn("public static void main(String[] args)", content)
        self.assertIn('System.out.println("Hello, World!");', content)

    def test_java_file_object_input_stream_is_utf8(self):
        """Test that file input stream uses UTF-8 encoding."""
        # Create a file with Unicode content
        method = (
            MethodSpec.method_builder("test")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("String msg = $S", "Unicode: 世界 🌍")
            .build()
        )

        type_spec = TypeSpec.class_builder("UnicodeTest").add_method(method).build()

        java_file = JavaFile.builder("com.example.unicode", type_spec).build()
        unicode_file_path = java_file.write_to_path(self.temp_dir)

        # Read as bytes and decode as UTF-8
        with open(unicode_file_path, "rb") as f:
            byte_content = f.read()

        decoded_content = byte_content.decode("utf-8")
        self.assertIn("Unicode: 世界 🌍", decoded_content)

    def test_file_content_consistency(self):
        """Test that file content matches the JavaFile string representation."""
        # Read the written file
        with open(self.file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Compare with JavaFile's string representation
        java_file_str = str(self.java_file)

        self.assertEqual(file_content.strip(), java_file_str.strip())

    def test_read_written_file_roundtrip(self):
        """Test reading a file that was written by JavaFile."""
        # Create a complex Java file
        field = (
            FieldSpec.builder(
                ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String")), "items"
            )
            .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
            .initializer("new $T<>()", ClassName.get("java.util", "ArrayList"))
            .build()
        )

        method1 = (
            MethodSpec.method_builder("addItem")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_parameter(ClassName.get("java.lang", "String"), "item")
            .add_statement("items.add(item)")
            .build()
        )

        method2 = (
            MethodSpec.method_builder("getItems")
            .add_modifiers(Modifier.PUBLIC)
            .returns(ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String")))
            .add_statement("return new $T<>(items)", ClassName.get("java.util", "ArrayList"))
            .build()
        )

        type_spec = (
            TypeSpec.class_builder("ItemContainer")
            .add_modifiers(Modifier.PUBLIC)
            .add_field(field)
            .add_method(method1)
            .add_method(method2)
            .build()
        )

        java_file = JavaFile.builder("com.example.container", type_spec).build()
        file_path = java_file.write_to_path(self.temp_dir)

        # Read back and verify structure
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify package
        self.assertIn("package com.example.container;", content)

        # Verify imports
        self.assertIn("import java.util.ArrayList;", content)
        self.assertIn("import java.util.List;", content)

        # Verify class structure
        self.assertIn("public class ItemContainer", content)
        self.assertIn("private final List<String> items", content)
        self.assertIn("public void addItem(String item)", content)
        self.assertIn("public List<String> getItems()", content)

    def test_empty_file_handling(self):
        """Test handling of empty or minimal files."""
        # Create minimal class
        type_spec = TypeSpec.class_builder("Empty").build()
        java_file = JavaFile.builder("com.example", type_spec).build()
        file_path = java_file.write_to_path(self.temp_dir)

        # Read and verify
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("package com.example;", content)
        self.assertIn("class Empty {", content)
        self.assertIn("}", content)

    def test_file_with_comments(self):
        """Test file with various types of comments."""
        method = (
            MethodSpec.method_builder("documented")
            .add_javadoc("This is a documented method.\n")
            .add_javadoc("@param none no parameters\n")
            .add_javadoc("@return nothing\n")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("// Single line comment")
            .add_statement("/* Block comment */")
            .build()
        )

        type_spec = (
            TypeSpec.class_builder("Commented").add_javadoc("This is a documented class.\n").add_method(method).build()
        )

        java_file = JavaFile.builder("com.example", type_spec).add_file_comment("This file was generated.\n").build()

        file_path = java_file.write_to_path(self.temp_dir)

        # Read and verify comments are preserved
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("// This file was generated.", content)
        self.assertIn("/**", content)
        self.assertIn("This is a documented class.", content)
        self.assertIn("This is a documented method.", content)
        self.assertIn("// Single line comment", content)
        self.assertIn("/* Block comment */", content)

    def test_large_file_handling(self):
        """Test handling of larger files."""
        # Create a class with many methods
        type_spec_builder = TypeSpec.class_builder("LargeClass").add_modifiers(Modifier.PUBLIC)

        # Add many methods
        for i in range(50):
            method = (
                MethodSpec.method_builder(f"method{i}")
                .add_modifiers(Modifier.PUBLIC)
                .returns("void")
                .add_parameter("int", f"param{i}")
                .add_statement("System.out.println($S + param$L)", f"Method {i}: ", i)
                .build()
            )
            type_spec_builder.add_method(method)

        type_spec = type_spec_builder.build()
        java_file = JavaFile.builder("com.example.large", type_spec).build()
        file_path = java_file.write_to_path(self.temp_dir)

        # Read and verify
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain all methods
        for i in range(50):
            self.assertIn(f"public void method{i}(int param{i})", content)
            self.assertIn(f'"Method {i}: "', content)

    def test_relative_path_calculation(self):
        """Test relative path calculation for different package structures."""
        test_cases = [
            ("", "Test", "Test.java"),
            ("com", "Test", os.path.join("com", "Test.java")),
            ("com.example", "Test", os.path.join("com", "example", "Test.java")),
            (
                "org.springframework.boot",
                "Application",
                os.path.join("org", "springframework", "boot", "Application.java"),
            ),
        ]

        for package, class_name, expected_path in test_cases:
            type_spec = TypeSpec.class_builder(class_name).build()
            java_file = JavaFile.builder(package, type_spec).build()

            relative_path = java_file.get_relative_path()
            expected_normalized = expected_path.replace("/", os.sep)
            self.assertEqual(relative_path, expected_normalized)


if __name__ == "__main__":
    unittest.main()
