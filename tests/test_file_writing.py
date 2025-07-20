"""
Tests for file writing functionality.
Equivalent to FileWritingTest.java
"""

import os
import tempfile
import unittest
from pathlib import Path

from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_spec import TypeSpec


class FileWritingTest(unittest.TestCase):
    """Test file writing functionality."""

    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_path_not_directory(self):
        """Test that writing to a non-directory path fails."""
        # Create a file instead of directory
        not_dir = os.path.join(self.temp_dir, "not_a_directory.txt")
        with open(not_dir, "w") as f:
            f.write("content")

        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        with self.assertRaises((OSError, ValueError)):
            java_file.write_to_path(not_dir)

    def test_path_default_package(self):
        """Test writing to default package."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("", type_spec).build()  # Default package

        output_path = java_file.write_to_path(self.temp_dir)

        # Should create Test.java in the root directory
        expected_file = os.path.join(self.temp_dir, "Test.java")
        self.assertEqual(str(output_path), expected_file)
        self.assertTrue(os.path.exists(expected_file))

        # Check content
        with open(expected_file, "r") as f:
            content = f.read()
        self.assertNotIn("package", content)
        self.assertIn("class Test", content)

    def test_path_nested_classes(self):
        """Test writing files with nested package structure."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example.nested", type_spec).build()

        output_path = java_file.write_to_path(self.temp_dir)

        # Should create com/example/nested/Test.java
        expected_file = os.path.join(self.temp_dir, "com", "example", "nested", "Test.java")
        self.assertEqual(str(output_path), expected_file)
        self.assertTrue(os.path.exists(expected_file))

        # Check that directories were created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "com")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "com", "example")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "com", "example", "nested")))

        # Check content
        with open(expected_file, "r") as f:
            content = f.read()
        self.assertIn("package com.example.nested;", content)

    def test_file_is_utf8(self):
        """Test that files are written in UTF-8 encoding."""
        # Create a class with Unicode content
        method = (
            MethodSpec.method_builder("test")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("String msg = $S", "Hello 世界! 🌍")
            .build()
        )

        type_spec = TypeSpec.class_builder("UnicodeTest").add_modifiers(Modifier.PUBLIC).add_method(method).build()

        java_file = JavaFile.builder("com.example", type_spec).build()
        output_path = java_file.write_to_path(self.temp_dir)

        # Read file as UTF-8 and check content
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Hello 世界! 🌍", content)

    def test_write_to_path_returns_path(self):
        """Test that write_to_path returns the created file path."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        returned_path = java_file.write_to_path(self.temp_dir)
        expected_path = os.path.join(self.temp_dir, "com", "example", "Test.java")

        self.assertEqual(str(returned_path), expected_path)
        self.assertTrue(os.path.exists(returned_path))

    def test_overwrite_existing_file(self):
        """Test overwriting an existing file."""
        # Create initial file
        type_spec1 = (
            TypeSpec.class_builder("Test")
            .add_method(MethodSpec.method_builder("method1").add_modifiers(Modifier.PUBLIC).returns("void").build())
            .build()
        )

        java_file1 = JavaFile.builder("com.example", type_spec1).build()
        output_path = java_file1.write_to_path(self.temp_dir)

        # Verify initial content
        with open(output_path, "r") as f:
            initial_content = f.read()
        self.assertIn("method1", initial_content)
        self.assertNotIn("method2", initial_content)

        # Overwrite with new content
        type_spec2 = (
            TypeSpec.class_builder("Test")
            .add_method(MethodSpec.method_builder("method2").add_modifiers(Modifier.PUBLIC).returns("void").build())
            .build()
        )

        java_file2 = JavaFile.builder("com.example", type_spec2).build()
        java_file2.write_to_path(self.temp_dir)

        # Verify overwritten content
        with open(output_path, "r") as f:
            new_content = f.read()
        self.assertNotIn("method1", new_content)
        self.assertIn("method2", new_content)

    def test_custom_indent_in_file(self):
        """Test custom indentation in written files."""
        method = (
            MethodSpec.method_builder("test")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("System.out.println($S)", "test")
            .build()
        )

        type_spec = TypeSpec.class_builder("Test").add_method(method).build()

        java_file = (
            JavaFile.builder("com.example", type_spec)
            .indent("\t")  # Use tabs instead of spaces
            .build()
        )

        output_path = java_file.write_to_path(self.temp_dir)

        with open(output_path, "r") as f:
            content = f.read()

        # Should contain tab indentation
        lines = content.split("\n")
        method_line = next((line for line in lines if "public void test()" in line), None)
        self.assertIsNotNone(method_line)
        # Method should be indented with tab
        self.assertTrue(method_line.startswith("\t"))

    def test_write_multiple_files(self):
        """Test writing multiple files to same directory."""
        # Create multiple files
        files_to_create = [
            ("Test1", "com.example.a"),
            ("Test2", "com.example.b"),
            ("Test3", "com.example.a"),  # Same package as Test1
        ]

        created_paths = []
        for class_name, package_name in files_to_create:
            type_spec = TypeSpec.class_builder(class_name).build()
            java_file = JavaFile.builder(package_name, type_spec).build()
            path = java_file.write_to_path(self.temp_dir)
            created_paths.append(path)

        # Verify all files were created
        for i, (class_name, package_name) in enumerate(files_to_create):
            expected_path = os.path.join(self.temp_dir, *package_name.split("."), f"{class_name}.java")
            self.assertEqual(str(created_paths[i]), expected_path)
            self.assertTrue(os.path.exists(created_paths[i]))

    def test_deep_package_structure(self):
        """Test writing to deep package structure."""
        deep_package = "com.very.deep.nested.package.structure"
        type_spec = TypeSpec.class_builder("DeepClass").build()
        java_file = JavaFile.builder(deep_package, type_spec).build()

        output_path = java_file.write_to_path(self.temp_dir)

        # Should create deep directory structure
        expected_dirs = ["com", "very", "deep", "nested", "package", "structure"]
        current_path = self.temp_dir

        for dir_name in expected_dirs:
            current_path = os.path.join(current_path, dir_name)
            self.assertTrue(os.path.exists(current_path))
            self.assertTrue(os.path.isdir(current_path))

        # Final file should exist
        final_file = os.path.join(current_path, "DeepClass.java")
        self.assertEqual(str(output_path), final_file)
        self.assertTrue(os.path.exists(final_file))

    def test_write_with_pathlib(self):
        """Test writing using pathlib.Path."""
        type_spec = TypeSpec.class_builder("PathLibTest").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        # Use pathlib.Path instead of string
        temp_path = Path(self.temp_dir)
        output_path = java_file.write_to_path(temp_path)

        expected_path = temp_path / "com" / "example" / "PathLibTest.java"
        self.assertEqual(output_path, expected_path)
        self.assertTrue(output_path.exists())

    def test_special_characters_in_filename(self):
        """Test handling of special characters that might appear in class names."""
        # Java allows $ in class names (used for inner classes)
        type_spec = TypeSpec.class_builder("Outer$Inner").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        output_path = java_file.write_to_path(self.temp_dir)

        # Should create file with $ in name
        expected_file = os.path.join(self.temp_dir, "com", "example", "Outer$Inner.java")
        self.assertEqual(str(output_path), expected_file)
        self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
