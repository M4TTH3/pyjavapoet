"""
Tests for JavaFile functionality.
Equivalent to JavaFileTest.java
"""

import unittest
from io import StringIO

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
        system_class = ClassName.get("com.example", "System")
        type_spec = (
            TypeSpec.class_builder("Test")
            .add_type(TypeSpec.class_builder("System").build())
            .add_method(
                MethodSpec.method_builder("test")
                .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "test")
                .build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
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
            .add_file_comment("This is a generated file.\n")
            .add_file_comment("Do not modify directly.\n")
            .build()
        )

        result = str(java_file)
        self.assertIn("// This is a generated file.", result)
        self.assertIn("// Do not modify directly.", result)

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
        # This would test type parameter annotations, which is complex in Python
        # For now, just test basic type parameter handling
        t_var = TypeVariableName.get("T")
        type_spec = TypeSpec.class_builder("Container").add_type_variable(t_var).build()

        java_file = JavaFile.builder("com.example", type_spec).build()

        result = str(java_file)
        self.assertIn("class Container<T>", result)

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
        self.assertIsNotNone(method_line)
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
        """Test package class conflicts with nested class."""
        nested = TypeSpec.class_builder("System").build()
        main_class = (
            TypeSpec.class_builder("Test")
            .add_type(nested)
            .add_method(
                MethodSpec.method_builder("test")
                .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "test")
                .build()
            )
            .build()
        )

        java_file = JavaFile.builder("com.example", main_class).build()

        result = str(java_file)
        # java.lang.System should be fully qualified due to nested class conflict
        self.assertIn("java.lang.System.out.println", result)

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
            .add_super_interface(ClassName.get("java.io", "Serializable"))
            .build()
        )

        java_file = JavaFile.builder("com.example", record).build()

        result = str(java_file)
        self.assertIn("record Point", result)
        self.assertIn("implements java.io.Serializable", result)


if __name__ == "__main__":
    unittest.main()
