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
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import ClassName, TypeVariableName, WildcardTypeName
from pyjavapoet.type_spec import TypeSpec


class TypeSpecTest(unittest.TestCase):
    """Test the TypeSpec class."""

    def test_basic(self):
        """Test basic class creation."""
        taco = TypeSpec.class_builder("Taco").build()

        result = str(taco)
        self.assertIn("class Taco", result)

    def test_interesting_types(self):
        """Test complex parameterized types."""
        bound = WildcardTypeName.subtypes_of(ClassName.get("java.lang", "Number"))
        list_of_numbers = ClassName.get("java.util", "List").with_type_arguments(bound)

        method = (
            MethodSpec.method_builder("getNumbers")
            .add_modifiers(Modifier.ABSTRACT, Modifier.PROTECTED)
            .returns(list_of_numbers)
            .build()
        )

        taco = TypeSpec.class_builder("Taco").add_modifiers(Modifier.ABSTRACT).add_method(method).build()

        result = str(taco)
        self.assertIn("List<? extends Number>", result)
        self.assertIn("protected abstract", result)

    def test_anonymous_inner_class(self):
        """Test anonymous inner class creation."""
        anonymous = (
            TypeSpec.anonymous_class_builder("")
            .add_superinterface(ClassName.get("java.lang", "Runnable"))
            .add_method(
                MethodSpec.method_builder("run")
                .add_annotation(AnnotationSpec.builder(ClassName.get("java.lang", "Override")).build())
                .add_modifiers(Modifier.PUBLIC)
                .returns("void")
                .add_statement("System.out.println($S)", "Running!")
                .build()
            )
            .build()
        )

        result = str(anonymous)
        self.assertIn("new Runnable()", result)
        self.assertIn("@Override", result)
        self.assertIn("public void run()", result)

    def test_annotated_parameters(self):
        """Test annotated method parameters."""
        service = AnnotationSpec.builder(ClassName.get("javax.inject", "Named"))

        constructor = (
            MethodSpec.constructor_builder()
            .add_modifiers(Modifier.PUBLIC)
            .add_parameter_spec(
                ParameterSpec.builder(ClassName.get("com.example", "Service"), "service")
                .add_annotation(service.add_member("value", "$S", "foobar").build())
                .build()
            )
            .add_statement("this.service = service")
            .build()
        )

        taco = TypeSpec.class_builder("Taco").add_method(constructor).build()

        result = str(taco)
        self.assertIn('public Taco(@Named("foobar") Service service)', result)

    def test_annotated_field(self):
        """Test field with annotations."""
        field = (
            FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_modifiers(Modifier.PRIVATE)
            .add_annotation(AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build())
            .build()
        )

        taco = TypeSpec.class_builder("Taco").add_field(field).build()

        result = str(taco)
        self.assertIn("@Nullable", result)
        self.assertIn("private String name", result)

    def test_annotated_class(self):
        """Test class with annotations."""
        annotation = (
            AnnotationSpec.builder(ClassName.get("com.example", "Component"))
            .add_member("value", "$S", "TacoComponent")
            .build()
        )

        taco = TypeSpec.class_builder("Taco").add_annotation(annotation).add_modifiers(Modifier.PUBLIC).build()

        result = str(taco)
        self.assertIn("@Component", result)
        self.assertIn('("TacoComponent")', result)
        self.assertIn("public class Taco", result)

    def test_enum_with_subclassing(self):
        """Test enum with anonymous subclasses."""
        roshambo = (
            TypeSpec.enum_builder("Roshambo")
            .add_modifiers(Modifier.PUBLIC)
            .add_enum_constant_with_class_body(
                "ROCK",
                TypeSpec.anonymous_class_builder("")
                .add_method(
                    MethodSpec.method_builder("toString")
                    .add_annotation(AnnotationSpec.builder(ClassName.get("java.lang", "Override")).build())
                    .add_modifiers(Modifier.PUBLIC)
                    .returns(ClassName.get("java.lang", "String"))
                    .add_statement("return $S", "avalanche!")
                    .build()
                )
                .build(),
            )
            .add_enum_constant("PAPER")
            .add_enum_constant("SCISSORS")
            .build()
        )

        result = str(roshambo)
        self.assertIn("public enum Roshambo", result)
        self.assertIn("ROCK {", result)
        self.assertIn('return "avalanche!";', result)

    def test_enums_may_define_abstract_methods(self):
        """Test enum with abstract methods."""
        roshambo = (
            TypeSpec.enum_builder("Roshambo")
            .add_method(
                MethodSpec.method_builder("play")
                .add_modifiers(Modifier.ABSTRACT)
                .add_parameter(ClassName.get("", "Roshambo"), "other")
                .returns("boolean")
                .build()
            )
            .add_enum_constant_with_class_body(
                "ROCK",
                TypeSpec.anonymous_class_builder("")
                .add_method(
                    MethodSpec.method_builder("play")
                    .add_annotation(AnnotationSpec.builder(ClassName.get("java.lang", "Override")).build())
                    .add_parameter(ClassName.get("", "Roshambo"), "other")
                    .returns("boolean")
                    .add_statement("return other != ROCK")
                    .build()
                )
                .build(),
            )
            .build()
        )

        result = str(roshambo)
        self.assertIn("abstract boolean play(Roshambo other)", result)

    def test_no_enum_constants(self):
        """Test enum without constants."""
        roshambo = (
            TypeSpec.enum_builder("Roshambo")
            .add_method(
                MethodSpec.method_builder("values")
                .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
                .returns(ClassName.get("", "Roshambo").array())
                .add_statement("return new Roshambo[0]")
                .build()
            )
            .build()
        )

        result = str(roshambo)
        self.assertIn("enum Roshambo", result)

    def test_interface_creation(self):
        """Test interface creation."""
        drawable = (
            TypeSpec.interface_builder("Drawable")
            .add_modifiers(Modifier.PUBLIC)
            .add_method(
                MethodSpec.method_builder("draw")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PUBLIC)
                .returns("void")
                .build()
            )
            .add_method(MethodSpec.method_builder("random").returns("void").build())
            .build()
        )

        result = str(drawable)
        expected = """\
public interface Drawable {
  public abstract void draw();

  void random();
}\
"""
        self.assertEqual(result, expected)

    def test_interface_with_default_method(self):
        """Test interface with default method."""
        drawable = (
            TypeSpec.interface_builder("Drawable")
            .add_modifiers(Modifier.PUBLIC)
            .add_method(
                MethodSpec.method_builder("paint")
                .add_modifiers(Modifier.DEFAULT, Modifier.PUBLIC)
                .returns("void")
                .add_statement("draw()")
                .build()
            )
            .build()
        )

        result = str(drawable)
        self.assertIn("public default void paint()", result)

    def test_annotation_type(self):
        """Test annotation type creation."""
        header_annotation = (
            TypeSpec.annotation_builder("Header")
            .add_modifiers(Modifier.PUBLIC)
            .add_method(
                MethodSpec.method_builder("value")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PUBLIC)
                .returns(ClassName.get("java.lang", "String"))
                .build()
            )
            .build()
        )

        result = str(header_annotation)
        self.assertIn("public @interface Header", result)
        self.assertIn("public abstract String value()", result)

    def test_inner_class(self):
        """Test inner class creation."""
        inner = (
            TypeSpec.class_builder("Inner")
            .add_modifiers(Modifier.PRIVATE, Modifier.STATIC)
            .add_field(FieldSpec.builder("int", "value").add_modifiers(Modifier.PRIVATE).build())
            .build()
        )

        outer = TypeSpec.class_builder("Outer").add_modifiers(Modifier.PUBLIC).add_type(inner).build()

        result = str(outer)
        self.assertIn("public class Outer", result)
        self.assertIn("private static class Inner", result)

    def test_class_with_generic_parameters(self):
        """Test class with generic type parameters."""
        t = TypeVariableName.get("T")
        container = (
            TypeSpec.class_builder("Container")
            .add_type_variable(t)
            .add_modifiers(Modifier.PUBLIC)
            .add_field(FieldSpec.builder(t, "value").add_modifiers(Modifier.PRIVATE).build())
            .build()
        )

        result = str(container)
        self.assertIn("public class Container<T>", result)
        self.assertIn("private T value", result)

    def test_class_with_bounded_generic_parameters(self):
        """Test class with bounded generic parameters."""
        t = TypeVariableName.get("T", ClassName.get("java.lang", "Number"))
        calculator = TypeSpec.class_builder("Calculator").add_type_variable(t).add_modifiers(Modifier.PUBLIC).build()

        result = str(calculator)
        self.assertIn("public class Calculator<T extends Number>", result)

    def test_class_with_superclass(self):
        """Test class with superclass."""
        child = (
            TypeSpec.class_builder("Child")
            .superclass(ClassName.get("com.example", "Parent"))
            .add_modifiers(Modifier.PUBLIC)
            .build()
        )

        result = str(child)
        self.assertIn("public class Child extends Parent", result)

    def test_class_with_interfaces(self):
        """Test class implementing interfaces."""
        implementation = (
            TypeSpec.class_builder("Implementation")
            .add_superinterface(ClassName.get("java.io", "Serializable"))
            .add_superinterface(ClassName.get("java.lang", "Cloneable"))
            .add_modifiers(Modifier.PUBLIC)
            .build()
        )

        result = str(implementation)
        self.assertIn("public class Implementation implements Serializable, Cloneable", result)

    def test_abstract_class(self):
        """Test abstract class creation."""
        abstract_class = (
            TypeSpec.class_builder("AbstractClass")
            .add_modifiers(Modifier.PUBLIC, Modifier.ABSTRACT)
            .add_method(
                MethodSpec.method_builder("abstractMethod")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PROTECTED)
                .returns("void")
                .build()
            )
            .build()
        )

        result = str(abstract_class)
        self.assertIn("public abstract class AbstractClass", result)
        self.assertIn("protected abstract void abstractMethod()", result)

    def test_final_class(self):
        """Test final class creation."""
        final_class = TypeSpec.class_builder("FinalClass").add_modifiers(Modifier.PUBLIC, Modifier.FINAL).build()

        result = str(final_class)
        self.assertIn("public final class FinalClass", result)

    def test_static_nested_class(self):
        """Test static nested class."""
        nested = TypeSpec.class_builder("Nested").add_modifiers(Modifier.PUBLIC, Modifier.STATIC).build()

        outer = TypeSpec.class_builder("Outer").add_modifiers(Modifier.PUBLIC).add_type(nested).build()

        result = str(outer)
        self.assertIn("public static class Nested", result)

    def test_class_with_constructor(self):
        """Test class with constructor."""
        constructor = (
            MethodSpec.constructor_builder()
            .add_modifiers(Modifier.PUBLIC)
            .add_parameter("java.lang.String", "name")
            .add_statement("this.name = name")
            .build()
        )

        clazz = TypeSpec.class_builder("MyClass").add_modifiers(Modifier.PUBLIC).add_method(constructor).build()

        result = str(clazz)
        self.assertIn("public MyClass(String name)", result)

    def test_class_with_javadoc(self):
        """Test class with javadoc."""
        clazz = (
            TypeSpec.class_builder("Documented")
            .add_javadoc_line("This is a documented class.\n")
            .add_javadoc_line("\n")
            .add_javadoc_line("@author PyJavaPoet\n")
            .add_javadoc_line("@since 1.0\n")
            .add_modifiers(Modifier.PUBLIC)
            .build()
        )

        result = str(clazz)
        self.assertIn("/**", result)
        self.assertIn("This is a documented class.", result)
        self.assertIn("@author PyJavaPoet", result)
        self.assertIn("@since 1.0", result)
        self.assertIn("*/", result)

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = TypeSpec.class_builder("Test").build()
        b = TypeSpec.class_builder("Test").build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_empty_class(self):
        """Test completely empty class."""
        empty = TypeSpec.class_builder("Empty").build()

        result = str(empty)
        self.assertIn("class Empty", result)
        self.assertIn("{", result)
        self.assertIn("}", result)

    def test_record_creation(self):
        """Test record creation (Java 14+ feature)."""
        record = (
            TypeSpec.record_builder("Point")
            .add_modifiers(Modifier.PUBLIC)
            .add_record_component(ParameterSpec.builder("int", "x").build())
            .add_record_component(ParameterSpec.builder("int", "y").build())
            .build()
        )

        result = str(record)
        self.assertIn("public record Point", result)
        self.assertIn("int x", result)
        self.assertIn("int y", result)


if __name__ == "__main__":
    unittest.main()
