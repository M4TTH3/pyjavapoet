import unittest
from io import StringIO

from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName, ParameterizedTypeName, TypeName, TypeVariableName
from pyjavapoet.type_spec import TypeSpec


class TestComplex(unittest.TestCase):
    def test_complex(self):
        """Generate a DataProcessor Java class and print it to stdout."""
        # Create type variables
        t = TypeVariableName.get("T")
        r = TypeVariableName.get("R")

        # Define classes we'll use
        list_class = ClassName.get("java.util", "List")
        array_list_class = ClassName.get("java.util", "ArrayList")
        objects_class = ClassName.get("java.util", "Objects")
        override_annotation = ClassName.get("java.lang", "Override")

        # Create a field for the processor name
        name_field = FieldSpec.builder(TypeName.STRING, "name").add_modifiers(Modifier.PRIVATE, Modifier.FINAL).build()

        # Create a counter field
        counter_field = (
            FieldSpec.builder(TypeName.get("int"), "processCount")
            .add_modifiers(Modifier.PRIVATE)
            .set_initializer("0")
            .build()
        )

        # Create a constructor
        constructor = (
            MethodSpec.constructor_builder()
            .add_modifiers(Modifier.PUBLIC)
            .add_parameter(TypeName.STRING, "name")
            .add_statement("this.$N = $T.requireNonNull($N)", "name", objects_class, "name")
            .build()
        )

        # Create a process method
        process_method = (
            MethodSpec.method_builder("process")
            .add_modifiers(Modifier.PUBLIC)
            .add_type_variable(t)
            .add_type_variable(r)
            .returns(ParameterizedTypeName.get(list_class, r))
            .add_parameter(ParameterizedTypeName.get(list_class, t), "input")
            .add_parameter("java.util.function.Function<T, R>", "transformer")
            .add_statement("$T<$T> result = new $T<>()", list_class, r, array_list_class)
            .begin_control_flow("for ($T item : input)", t)
            .add_statement("result.add(transformer.apply(item))")
            .end_control_flow()
            .add_statement("processCount++")
            .add_statement("return result")
            .build()
        )

        # Create a toString method with @Override annotation
        to_string = (
            MethodSpec.method_builder("toString")
            .add_annotation(AnnotationSpec.get(override_annotation))
            .add_modifiers(Modifier.PUBLIC)
            .returns(TypeName.STRING)
            .add_statement("return $S + name + $S + processCount", "DataProcessor{name='", "', processCount=")
            .build()
        )

        # Create the DataProcessor class
        processor = (
            TypeSpec.class_builder("DataProcessor")
            .add_modifiers(Modifier.PUBLIC)
            .add_field(name_field)
            .add_field(counter_field)
            .add_method(constructor)
            .add_method(process_method)
            .add_method(to_string)
            .build()
        )

        # Create the Java file
        java_file = (
            JavaFile.builder("com.example.processor", processor)
            .add_file_comment("This is a generated file. Do not edit!")
            .build()
        )

        # Print the Java file to stdout
        io = StringIO()
        java_file.write_to(io)
        print(io.getvalue())
        assert False