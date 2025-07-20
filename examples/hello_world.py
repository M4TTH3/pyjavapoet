#!/usr/bin/env python3
"""
Simple example showing how to generate a HelloWorld Java class using PyPoet.
"""

import os
import sys

# Add the parent directory to the path so we can import pypoet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


def main():
    """Generate a HelloWorld Java class and print it to stdout."""
    # Create the main method
    main_method = (
        MethodSpec.method_builder("main")
        .add_modifiers(Modifier.PUBLIC, Modifier.STATIC)
        .returns("void")
        .add_parameter("String[]", "args")
        .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Hello, PyPoet!")
        .build()
    )

    # Create the HelloWorld class
    hello_world = (
        TypeSpec.class_builder("HelloWorld")
        .add_modifiers(Modifier.PUBLIC, Modifier.FINAL)
        .add_method(main_method)
        .build()
    )

    # Create the Java file
    java_file = JavaFile.builder("com.example.helloworld", hello_world).build()

    # Print the Java file to stdout
    java_file.write_to()


if __name__ == "__main__":
    main()
