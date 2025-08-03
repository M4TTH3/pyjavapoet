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

import tempfile
import unittest
from io import StringIO
from pathlib import Path

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import ClassName, TypeVariableName
from pyjavapoet.type_spec import TypeSpec


class JavaFileTest(unittest.TestCase):
    """Test the JavaFile class."""

    def test_import_static_readme_example(self):
        """Test static import example."""
        type_spec = (
            TypeSpec.class_builder("HelloWorld")
            .add_modifiers(Modifier.PUBLIC, Modifier.FINAL)
            .add_method(
                MethodSpec.method_builder("main")
                .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
                .returns("void")
                .add_parameter("String[]", "args")
                .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Hello, World!")
                .build()
            )
            .build()
        )

        java_file = (
            JavaFile.builder("com.example.helloworld", type_spec)
            .add_static_import(ClassName.get("java.lang", "System"), "out")
            .build()
        )

        result = str(java_file)
        self.assertIn("import static java.lang.System.out;", result)

    def test_import_static_for_crazy_formats_works(self):
        """Test static imports with complex format strings."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_method(MethodSpec.method_builder("test").add_statement("out.println($S)", "test").build())
            .build()
        )

        java_file = (
            JavaFile.builder("com.example", type_spec)
            .add_static_import(ClassName.get("java.lang", "System"), "out")
            .build()
        )

        result = str(java_file)
        self.assertIn("import static java.lang.System.out;", result)

    def test_no_imports(self):
        """Test file with no imports."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        self.assertIn("package com.example;", result)
        self.assertNotIn("import", result)
        self.assertIn("class Test", result)

    def test_single_import(self):
        """Test file with single import."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_field(FieldSpec.builder(ClassName.get("java.util", "List"), "list").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        self.assertIn("import java.util.List;", result)

    def test_conflicting_imports(self):
        """Test handling of conflicting imports."""
        awt_list = ClassName.get("java.awt", "List")
        util_list = ClassName.get("java.util", "List")

        type_spec = (
            TypeSpec.class_builder("Test")
            .add_field(FieldSpec.builder(awt_list, "awtList").build())
            .add_field(FieldSpec.builder(util_list, "utilList").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        # One should be imported, the other should be fully qualified
        import_count = result.count("import java.awt.List;") + result.count("import java.util.List;")
        self.assertEqual(import_count, 1)

    def test_skip_java_lang_imports_with_conflicting_class_names(self):
        """Test that java.lang imports are skipped when there's a naming conflict."""
        system_class = ClassName.get("java.lang", "System")
        type_spec = (
            TypeSpec.class_builder("System")
            .add_method(
                MethodSpec.method_builder("test").add_statement("$T.out.println($S)", system_class, "test").build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        print(result)
        # Should use fully qualified name for java.lang.System due to conflict
        self.assertIn("java.lang.System.out.println", result)

    def test_conflicting_parent_name(self):
        """Test conflicting names with parent class."""
        type_spec = TypeSpec.class_builder("MyClass").superclass(ClassName.get("com.example.parent", "MyClass")).build()

        java_file = JavaFile.builder("com.example.child", type_spec).build()

        result = str(java_file)
        # Parent class should be fully qualified due to name conflict
        self.assertIn("com.example.parent.MyClass", result)

    def test_conflicting_child_name(self):
        """Test conflicting names with nested class."""
        inner_class = TypeSpec.class_builder("Conflict").build()
        outer_class = (
            TypeSpec.class_builder("OuterClass")
            .add_type(inner_class)
            .add_field(FieldSpec.builder(ClassName.get("com.other", "Conflict"), "field").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", outer_class).build()

        result = str(java_file)
        # External class should be fully qualified due to nested class conflict
        self.assertIn("com.other.Conflict", result)

    def test_always_qualify_package_private_types(self):
        """Test that package-private types are always qualified when in different packages."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_field(FieldSpec.builder(ClassName.get("com.other", "PackagePrivate"), "field").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        # Package-private class in different package should be fully qualified
        self.assertIn("com.other.PackagePrivate", result)

    def test_default_package(self):
        """Test class in default package."""
        type_spec = TypeSpec.class_builder("DefaultPackageClass").build()
        java_file = JavaFile.builder("", type_spec).build()

        result = str(java_file)
        self.assertNotIn("package", result)
        self.assertIn("class DefaultPackageClass", result)

    def test_file_comment(self):
        """Test file header comment."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = (
            JavaFile.builder("com.example", type_spec)
            .add_file_comment_line("This is a generated file.")
            .add_file_comment_line("Do not modify directly.")
            .build()
        )

        result = str(java_file)
        self.assertIn(" * This is a generated file.", result)
        self.assertIn(" * Do not modify directly.", result)

    def test_skip_java_lang_imports(self):
        """Test that java.lang imports are automatically skipped."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_field(FieldSpec.builder(ClassName.get("java.lang", "String"), "name").build())
            .add_field(FieldSpec.builder(ClassName.get("java.lang", "Object"), "obj").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        self.assertNotIn("import java.lang.String;", result)
        self.assertNotIn("import java.lang.Object;", result)
        self.assertIn("String name", result)
        self.assertIn("Object obj", result)

    def test_nested_class_and_superclass_share_name(self):
        """Test nested class and superclass with same name."""
        nested = TypeSpec.class_builder("Parent").build()
        main_class = (
            TypeSpec.class_builder("Child").superclass(ClassName.get("com.other", "Parent")).add_type(nested).build()
        )

        java_file = JavaFile.builder("com.example", main_class).build()

        result = str(java_file)
        # External parent should be fully qualified
        self.assertIn("com.other.Parent", result)

    def test_avoid_clashes_with_nested_classes(self):
        """Test avoiding import clashes with nested classes."""
        nested = TypeSpec.class_builder("List").build()
        main_class = (
            TypeSpec.class_builder("Container")
            .add_type(nested)
            .add_field(FieldSpec.builder(ClassName.get("java.util", "List"), "items").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", main_class).build()

        result = str(java_file)
        # java.util.List should be fully qualified due to nested class conflict
        self.assertIn("java.util.List", result)

    def test_annotated_type_param(self):
        """Test annotated type parameters."""
        annotation = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
        t_var = TypeVariableName.get("T")
        type_spec = TypeSpec.class_builder("Container").add_type_variable(t_var).add_annotation(annotation).build()

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        self.assertIn("@Nullable\nclass Container<T>", result)

    def test_static_import_conflicts_with_field(self):
        """Test static import conflicts with field names."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_field(FieldSpec.builder("int", "max").add_modifiers(Modifier.PRIVATE).build())
            .add_method(
                MethodSpec.method_builder("test")
                .add_statement("int result = $T.max(1, 2)", ClassName.get("java.lang", "Math"))
                .build()
            )
            .build()
        )

        java_file = (
            JavaFile.builder("com.example", type_spec)
            .add_static_import(ClassName.get("java.lang", "Math"), "max")
            .build()
        )

        result = str(java_file)
        # Static import should be avoided due to field name conflict
        self.assertIn("Math.max(1, 2)", result)

    def test_indent_with_tabs(self):
        """Test indentation with tabs instead of spaces."""
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_method(
                MethodSpec.method_builder("test")
                .add_modifiers(Modifier.PUBLIC)
                .returns("void")
                .add_statement("System.out.println($S)", "test")
                .build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).indent("\t").build()

        result = str(java_file)
        # Should use tabs for indentation
        lines = result.split("\n")
        method_line = next((line for line in lines if "public void test()" in line), None)
        assert method_line
        self.assertTrue(method_line.startswith("\t"))

    def test_java_file_equals_and_hash_code(self):
        """Test JavaFile equals and hash code."""
        type_spec = TypeSpec.class_builder("Test").build()
        a = JavaFile.builder("com.example", type_spec).build()
        b = JavaFile.builder("com.example", type_spec).build()

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_java_file_to_builder(self):
        """Test JavaFile to builder conversion."""
        type_spec = TypeSpec.class_builder("Test").build()
        original = JavaFile.builder("com.example", type_spec).build()

        modified = original.to_builder().add_static_import(ClassName.get("java.lang", "System"), "out").build()

        original_str = str(original)
        modified_str = str(modified)

        self.assertNotIn("import static", original_str)
        self.assertIn("import static java.lang.System.out;", modified_str)

    def test_write_to_string_io(self):
        """Test writing to StringIO."""
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        output = StringIO()
        java_file.write_to(output)

        result = output.getvalue()
        self.assertIn("package com.example;", result)
        self.assertIn("class Test", result)

    def test_package_class_conflicts_with_nested_class(self):
        self.maxDiff = None
        system_lang = ClassName.get("java.util", "System")
        system_class_name = ClassName.get("", "Top", "System")
        nested_system_class_name = ClassName.get("", "Top", "Inner", "System")
        nested_inner_class = (
            TypeSpec.builder("Inner")
            .add_modifiers(Modifier.PUBLIC)
            .add_type(TypeSpec.builder("System").add_modifiers(Modifier.PUBLIC).build())
            .add_method(
                MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_statement("$T obj = null", system_lang)
                .add_statement("$T obj2 = null", system_class_name)
                .add_statement("$T obj3 = null", nested_system_class_name)
                .build()
            )
            .build()
        )
        system_class = TypeSpec.builder("System").add_modifiers(Modifier.PUBLIC).build()
        top_class = (
            TypeSpec.builder("Top")
            .add_modifiers(Modifier.PUBLIC)
            .add_type(system_class)
            .add_type(nested_inner_class)
            .add_method(
                MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_statement("$T obj = null", system_lang)
                .add_statement("$T obj2 = null", system_class_name)
                .add_statement("$T obj3 = null", nested_system_class_name)
                .build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", top_class).indent("    ").build()
        result = str(java_file)
        print(result)
        self.assertEqual(
            result,
            """\
package com.example;

public class Top {
    public Top() {
        java.util.System obj = null;
        Top.System obj2 = null;
        Top.Inner.System obj3 = null;
    }

    public class System {
    }

    public class Inner {
        public Inner() {
            java.util.System obj = null;
            Top.System obj2 = null;
            Top.Inner.System obj3 = null;
        }

        public class System {
        }
    }
}
""",
        )

    def test_inner_inner_scope_conflicts_should_use_canonical_in_inner_scope(self):
        self.maxDiff = None
        system_lang = ClassName.get("java.util", "System")
        nested_system_class_name = ClassName.get("", "Top", "Inner", "System")
        nested_inner_class = (
            TypeSpec.builder("Inner")
            .add_modifiers(Modifier.PUBLIC)
            .add_type(TypeSpec.builder("System").add_modifiers(Modifier.PUBLIC).build())
            .add_method(
                MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_statement("$T obj = null", system_lang)
                .add_statement("$T obj2 = null", nested_system_class_name)
                .build()
            )
            .build()
        )
        top_class = (
            TypeSpec.builder("Top")
            .add_modifiers(Modifier.PUBLIC)
            .add_type(nested_inner_class)
            .add_method(
                MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_statement("$T obj = null", system_lang)
                .add_statement("$T obj2 = null", nested_system_class_name)
                .build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", top_class).indent("    ").build()
        result = str(java_file)
        self.assertEqual(
            result,
            """\
package com.example;

import java.util.System;

public class Top {
    public Top() {
        System obj = null;
        Top.Inner.System obj2 = null;
    }

    public class Inner {
        public Inner() {
            java.util.System obj = null;
            Top.Inner.System obj2 = null;
        }

        public class System {
        }
    }
}
""",
        )

    def test_record_one_field_with_generic(self):
        """Test record with generic field."""
        list_string = ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String"))
        record = (
            TypeSpec.record_builder("Container")
            .add_record_component(ParameterSpec.builder(list_string, "items").build())
            .build()
        )

        java_file = JavaFile.builder("com.example", record).build()

        result = str(java_file)
        self.assertIn("record Container", result)
        self.assertIn("List<String> items", result)

    def test_record_implements_interface(self):
        """Test record implementing interface."""
        record = (
            TypeSpec.record_builder("Point")
            .add_record_component(ParameterSpec.builder("int", "x").build())
            .add_record_component(ParameterSpec.builder("int", "y").build())
            .add_superinterface(ClassName.get("java.io", "Serializable"))
            .build()
        )

        java_file = JavaFile.builder("com.example", record).build()

        result = str(java_file)
        self.assertIn("record Point", result)
        self.assertIn("implements Serializable", result)


class JavaFileReadWriteTest(unittest.TestCase):
    """Test file reading functionality."""

    def setUp(self):
        """Set up test with a sample Java file."""
        self.temp_dir = Path(tempfile.mkdtemp())

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
        self.file_path = self.java_file.write_to_dir(self.temp_dir)

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
            ("", "Test", Path("Test.java")),
            ("com.example", "Test", Path("com", "example", "Test.java")),
            ("deeply.nested.package", "Test", Path("deeply", "nested", "package", "Test.java")),
        ]

        for package, class_name, expected_relative_path in test_cases:
            type_spec = TypeSpec.class_builder(class_name).build()
            java_file = JavaFile.builder(package, type_spec).build()

            relative_path = java_file.get_relative_path()
            self.assertEqual(relative_path, expected_relative_path)

    def test_java_file_object_kind(self):
        """Test JavaFileObject kind detection."""
        # Test that we can identify Java source files
        self.assertTrue(self.file_path.suffix == ".java")

        # Test file extension handling
        type_spec = TypeSpec.class_builder("Test").build()
        java_file = JavaFile.builder("com.example", type_spec).build()

        relative_path = java_file.get_relative_path()
        self.assertTrue(relative_path.suffix == ".java")

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
        unicode_file_path = java_file.write_to_dir(self.temp_dir)

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
        file_path = java_file.write_to_dir(self.temp_dir)

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
        file_path = java_file.write_to_dir(self.temp_dir)

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
            .add_javadoc_line("This is a documented method.")
            .add_javadoc_line()
            .add_javadoc_line("@param none no parameters")
            .add_javadoc_line("@return nothing")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_raw_line("// Single line comment")
            .add_raw_line("/* Block comment */")
            .build()
        )

        type_spec = (
            TypeSpec.class_builder("Commented")
            .add_javadoc_line("This is a documented class.")
            .add_method(method)
            .build()
        )

        java_file = (
            JavaFile.builder("com.example", type_spec)
            .indent("    ")
            .add_file_comment_line("This is a documented file.\n")
            .add_file_comment_line("@generated")
            .add_file_comment_line("Generated by pyjavapoet")
            .build()
        )

        file_path = java_file.write_to_dir(self.temp_dir)

        # Read and verify comments are preserved
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        expected = """\
/**
 * This is a documented file.
 * 
 * @generated
 * Generated by pyjavapoet
 */
package com.example;

/**
 * This is a documented class.
 */
class Commented {
    /**
     * This is a documented method.
     * 
     * @param none no parameters
     * @return nothing
     */
    public void documented() {
        // Single line comment
        /* Block comment */
    }
}
"""
        self.assertEqual(content, expected)

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
        file_path = java_file.write_to_dir(self.temp_dir)

        # Read and verify
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain all methods
        for i in range(50):
            self.assertIn(f"public void method{i}(int param{i})", content)
            self.assertIn(f'"Method {i}: "', content)

    def test_relative_path_calculation(self):
        """Test relative path calculation for different package structures."""
        test_cases: list[tuple[str, str, Path]] = [
            ("", "Test", Path("Test.java")),
            ("com", "Test", Path("com", "Test.java")),
            ("com.example", "Test", Path("com", "example", "Test.java")),
            (
                "org.springframework.boot",
                "Application",
                Path("org", "springframework", "boot", "Application.java"),
            ),
        ]

        for package, class_name, expected_path in test_cases:
            type_spec = TypeSpec.class_builder(class_name).build()
            java_file = JavaFile.builder(package, type_spec).build()

            relative_path = java_file.get_relative_path()
            self.assertEqual(relative_path, expected_path)


if __name__ == "__main__":
    unittest.main()
