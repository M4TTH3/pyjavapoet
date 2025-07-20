"""
Basic tests for PyPoet, focusing on the HelloWorld example from the README.
"""

import unittest
from io import StringIO

from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


class HelloWorldTest(unittest.TestCase):
    """Test the HelloWorld example from the README."""

    def test_hello_world(self):
        """Test generating a simple HelloWorld class."""
        # Create the main method
        main = (
            MethodSpec.method_builder("main")
            .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
            .returns("void")
            .add_parameter("String[]", "args")
            .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Hello, PyPoet!")
            .build()
        )

        # Create the HelloWorld class
        hello_world = (
            TypeSpec.class_builder("HelloWorld").add_modifiers(Modifier.PUBLIC, Modifier.FINAL).add_method(main).build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.helloworld", hello_world).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output
        expected = """package com.example.helloworld;

import java.lang.System;

public final class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello, PyPoet!");
  }
}
"""
        self.assertEqual(expected, out.getvalue())


if __name__ == "__main__":
    unittest.main()
