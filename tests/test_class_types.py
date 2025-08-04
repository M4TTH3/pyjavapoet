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
from io import StringIO
from textwrap import dedent

from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName, TypeVariableName
from pyjavapoet.type_spec import TypeSpec


class ClassTypesTest(unittest.TestCase):
    """Test different class types in PyPoet."""

    def test_interface(self):
        """Test generating an interface."""
        # Create a constant field
        constant = (
            FieldSpec.builder(ClassName.STRING, "ONLY_THING_THAT_IS_CONSTANT")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC, Modifier.FINAL)
            .initializer("$S", "change")
            .build()
        )

        # Create a method
        beep = MethodSpec.method_builder("beep").add_modifiers(Modifier.PUBLIC, Modifier.ABSTRACT).build()

        # Create the interface
        hello_world = (
            TypeSpec.interface_builder("HelloWorld")
            .add_modifiers(Modifier.PUBLIC)
            .add_field(constant)
            .add_method(beep)
            .build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.hello", hello_world).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output - note that in interfaces, modifiers like PUBLIC and ABSTRACT are implicit
        expected = dedent("""\
          package com.example.hello;

          public interface HelloWorld {
            public static final String ONLY_THING_THAT_IS_CONSTANT = "change";

            public abstract void beep();
          }
        """)
        print(out.getvalue())
        self.assertEqual(expected, out.getvalue())

    def test_enum(self):
        """Test generating an enum."""
        # Create the enum with constants
        roshambo = (
            TypeSpec.enum_builder("Roshambo")
            .add_modifiers(Modifier.PUBLIC)
            .add_enum_constant("ROCK")
            .add_enum_constant("SCISSORS")
            .add_enum_constant("PAPER")
            .build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.game", roshambo).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output
        expected = """\
package com.example.game;

public enum Roshambo {
  ROCK,
  SCISSORS,
  PAPER
}
"""
        self.assertEqual(expected, out.getvalue())

    def test_class_with_generics(self):
        """Test generating a class with generic type parameters."""
        # Create a type variable
        t = TypeVariableName.get("T", "java.lang.Comparable")

        # Create a method
        identity = (
            MethodSpec.method_builder("identity")
            .add_modifiers(Modifier.PUBLIC)
            .returns(t)
            .add_parameter(t, "value")
            .add_statement("return value")
            .build()
        )

        # Create the class
        identity_mixer = (
            TypeSpec.class_builder("IdentityMixer")
            .add_modifiers(Modifier.PUBLIC)
            .add_type_variable(t)
            .add_method(identity)
            .build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.util", identity_mixer).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output
        expected = """\
package com.example.util;

public class IdentityMixer<T extends Comparable> {
  public T identity(T value) {
    return value;
  }
}
"""
        self.assertEqual(expected, out.getvalue())
