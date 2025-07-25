"""
Tests for MethodSpec functionality.
Equivalent to MethodSpecTest.java
"""

import unittest

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import ClassName, TypeVariableName


class MethodSpecTest(unittest.TestCase):
    """Test the MethodSpec class."""

    def test_basic_method_creation(self):
        """Test basic method creation."""
        method = (
            MethodSpec.method_builder("getName")
            .add_modifiers(Modifier.PUBLIC)
            .returns(ClassName.get("java.lang", "String"))
            .add_statement("return this.name")
            .build()
        )

        result = str(method)
        self.assertEqual(result, "public String getName() {\n  return this.name;\n}\n")

    def test_method_with_parameters(self):
        """Test method with parameters."""
        method = (
            MethodSpec.method_builder("setName")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_parameter(ClassName.get("java.lang", "String"), "name")
            .add_statement("this.name = name")
            .build()
        )

        result = str(method)
        self.assertEqual(result, "public void setName(String name) {\n  this.name = name;\n}\n")

    def test_method_with_javadoc(self):
        """Test method with javadoc."""
        method = (
            MethodSpec.method_builder("calculate")
            .add_javadoc("Calculates the result.")
            .add_javadoc()
            .add_javadoc("@param $L", "input the input value")
            .add_javadoc("@return the calculated result")
            .add_modifiers(Modifier.PUBLIC)
            .returns("int")
            .add_parameter("int", "input")
            .add_statement("return input * 2")
            .build()
        )

        result = str(method)
        print(result)
        self.assertIn(
"""\
/**
 * Calculates the result.
 * 
 * @param input the input value
 * @return the calculated result
 */"""
        , result)

    def test_constructor_creation_and_set_name(self):
        """Test constructor creation."""
        constructor = (
            MethodSpec.constructor_builder()
            .add_modifiers(Modifier.PUBLIC)
            .add_parameter(ClassName.get("java.lang", "String"), "name")
            .add_statement("this.name = name")
            .build()
        )

        result = str(constructor)
        self.assertIn("public <init>(String name)", result)
        self.assertIn("this.name = name;", result)
        result = str(constructor.to_builder().set_name("ClassName").build())
        self.assertIn("public ClassName(String name)", result)

    def test_abstract_method(self):
        """Test abstract method creation."""
        method = (
            MethodSpec.method_builder("process")
            .add_modifiers(Modifier.PUBLIC, Modifier.ABSTRACT)
            .returns("void")
            .add_parameter(ClassName.get("java.lang", "Object"), "data")
            .build()
        )

        result = str(method)
        self.assertIn("public abstract void process", result)
        # Abstract methods should not have a body
        self.assertNotIn("{", result)

    def test_method_with_exceptions(self):
        """Test method with exceptions."""
        method = (
            MethodSpec.method_builder("readFile")
            .add_modifiers(Modifier.PUBLIC)
            .returns(ClassName.get("java.lang", "String"))
            .add_parameter(ClassName.get("java.lang", "String"), "filename")
            .add_exception(ClassName.get("java.io", "IOException"))
            .add_exception(ClassName.get("java.lang", "SecurityException"))
            .add_comment("implementation")
            .add_statement("return null")
            .build()
        )

        result = str(method)
        self.assertEqual(
"""\
public String readFile(String filename) throws IOException, SecurityException {
  // implementation
  return null;
}"""
        , result)

    def test_method_with_type_variables(self):
        """Test method with type variables."""
        t_var = TypeVariableName.get("T")
        method = (
            MethodSpec.method_builder("identity")
            .add_type_variable(t_var)
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
            .returns(t_var)
            .add_parameter(t_var, "input")
            .add_statement("return input")
            .build()
        )

        result = str(method)
        expected = (
"""\
public static <T> T identity(T input) {
  return input;
}""")
        self.assertEqual(expected, result)

    def test_method_with_bounded_type_variables(self):
        """Test method with bounded type variables."""
        t_var = TypeVariableName.get("T", ClassName.get("java.lang", "Number"))
        method = (
            MethodSpec.method_builder("process")
            .add_type_variable(t_var)
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_parameter(t_var, "number")
            .add_statement("// process number")
            .build()
        )

        result = str(method)
        self.assertIn("<T extends java.lang.Number>", result)

    def test_static_method(self):
        """Test static method creation."""
        method = (
            MethodSpec.method_builder("valueOf")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
            .returns(ClassName.get("com.example", "MyClass"))
            .add_parameter("int", "value")
            .add_statement("return new $T(value)", ClassName.get("com.example", "MyClass"))
            .build()
        )

        result = str(method)
        self.assertIn("public static", result)
        self.assertIn("MyClass valueOf", result)

    def test_method_with_annotations(self):
        """Test method with annotations."""
        override = AnnotationSpec.builder(ClassName.get("java.lang", "Override")).build()
        deprecated = AnnotationSpec.builder(ClassName.get("java.lang", "Deprecated")).build()

        method = (
            MethodSpec.method_builder("oldMethod")
            .add_annotation(override)
            .add_annotation(deprecated)
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("// old implementation")
            .build()
        )

        result = str(method)
        self.assertIn("@java.lang.Override", result)
        self.assertIn("@java.lang.Deprecated", result)

    def test_method_with_varargs(self):
        """Test method with varargs parameter."""
        method = (
            MethodSpec.method_builder("format")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
            .returns(ClassName.get("java.lang", "String"))
            .add_parameter(ClassName.get("java.lang", "String"), "format")
            .add_parameter("Object...", "args")  # Varargs
            .add_statement("return $T.format(format, args)", ClassName.get("java.lang", "String"))
            .build()
        )

        result = str(method)
        self.assertIn("Object... args", result)

    def test_equals_and_hash_code(self):
        """Test equals and hash code functionality."""
        a = MethodSpec.method_builder("test").add_modifiers(Modifier.PUBLIC).returns("void").build()
        b = MethodSpec.method_builder("test").add_modifiers(Modifier.PUBLIC).returns("void").build()
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_duplicate_exceptions_ignored(self):
        """Test that duplicate exceptions are ignored."""
        method = (
            MethodSpec.method_builder("test")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_exception(ClassName.get("java.io", "IOException"))
            .add_exception(ClassName.get("java.io", "IOException"))  # Duplicate
            .build()
        )

        result = str(method)
        # Should only appear once
        self.assertEqual(result.count("java.io.IOException"), 1)

    def test_method_to_builder(self):
        """Test method to builder conversion."""
        original = MethodSpec.method_builder("test").add_modifiers(Modifier.PUBLIC).returns("void").build()

        modified = original.to_builder().add_statement("// modified").build()

        original_str = str(original)
        modified_str = str(modified)

        self.assertNotIn("// modified", original_str)
        self.assertIn("// modified", modified_str)

    def test_control_flow_with_named_code_blocks(self):
        """Test control flow with named code blocks."""
        method = (
            MethodSpec.method_builder("example")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_named_code("$L", "if (condition)")
            .begin_control_flow("")
            .add_statement("doSomething()")
            .end_control_flow()
            .build()
        )

        result = str(method)
        self.assertIn("if (condition)", result)
        self.assertIn("doSomething();", result)

    def test_ensure_trailing_newline(self):
        """Test that methods end with proper newlines."""
        method = (
            MethodSpec.method_builder("test")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("System.out.println($S)", "test")
            .build()
        )

        result = str(method)
        self.assertTrue(result.endswith("}\n"))

    def test_interface_method(self):
        """Test interface method (no body)."""
        method = (
            MethodSpec.method_builder("calculate")
            .add_modifiers(Modifier.PUBLIC, Modifier.ABSTRACT)
            .returns("int")
            .add_parameter("int", "input")
            .build()
        )

        result = str(method)
        self.assertIn("public abstract int calculate(int input)", result)
        # Interface methods should not have a body
        self.assertNotIn("{", result)

    def test_native_method(self):
        """Test native method declaration."""
        method = (
            MethodSpec.method_builder("nativeCall")
            .add_modifiers(Modifier.PUBLIC, Modifier.NATIVE)
            .returns("int")
            .add_parameter("long", "value")
            .build()
        )

        result = str(method)
        self.assertIn("public native int nativeCall", result)
        # Native methods should not have a body
        self.assertNotIn("{", result)

    def test_synchronized_method(self):
        """Test synchronized method."""
        method = (
            MethodSpec.method_builder("synchronizedMethod")
            .add_modifiers(Modifier.PUBLIC, Modifier.SYNCHRONIZED)
            .returns("void")
            .add_statement("// synchronized implementation")
            .build()
        )

        result = str(method)
        self.assertIn("public synchronized void", result)

    def test_method_with_complex_body(self):
        """Test method with complex code body."""
        method = (
            MethodSpec.method_builder("complexMethod")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_parameter("java.util.List<String>", "items")
            .begin_control_flow("for (String item : items)")
            .begin_control_flow("if (item != null)")
            .add_statement("System.out.println(item)")
            .next_control_flow("else")
            .add_statement("System.out.println($S)", "null item")
            .end_control_flow()
            .end_control_flow()
            .build()
        )

        result = str(method)
        self.assertIn("for (String item : items) {", result)
        self.assertIn("if (item != null) {", result)
        self.assertIn("} else {", result)
        self.assertIn("System.out.println(item);", result)

    def test_method_with_parameter_specs(self):
        """Test method with ParameterSpec objects."""
        param = (
            ParameterSpec.builder(ClassName.get("java.lang", "String"), "name")
            .add_annotation(AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build())
            .build()
        )

        method = (
            MethodSpec.method_builder("process")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_parameter(param)
            .add_statement("// process name")
            .build()
        )

        result = str(method)
        self.assertIn("@javax.annotation.Nullable java.lang.String name", result)


if __name__ == "__main__":
    unittest.main()
