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

from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.type_name import ClassName
from pyjavapoet.type_spec import TypeSpec


class ControlFlowTest(unittest.TestCase):
    """Test control flow generation in PyPoet."""

    def test_if_else(self):
        """Test generating if/else control flow."""
        # Create a method with if/else logic
        check_time = (
            MethodSpec.method_builder("checkTime")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .add_statement("long now = $T.currentTimeMillis()", ClassName.get("java.lang", "System"))
            .begin_control_flow("if ($T.currentTimeMillis() < now)", ClassName.get("java.lang", "System"))
            .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Time travelling, woo hoo!")
            .next_control_flow("else if ($T.currentTimeMillis() == now)", ClassName.get("java.lang", "System"))
            .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Time stood still!")
            .next_control_flow("else")
            .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Ok, time still moving forward")
            .end_control_flow()
            .build()
        )

        # Create the class
        time_checker = (
            TypeSpec.class_builder("TimeChecker").add_modifiers(Modifier.PUBLIC).add_method(check_time).build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.time", time_checker).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output
        expected = """\
package com.example.time;

public class TimeChecker {
  public void checkTime() {
    long now = System.currentTimeMillis();
    if (System.currentTimeMillis() < now) {
      System.out.println("Time travelling, woo hoo!");
    } else if (System.currentTimeMillis() == now) {
      System.out.println("Time stood still!");
    } else {
      System.out.println("Ok, time still moving forward");
    }
  }
}
"""
        print(out.getvalue())
        self.assertEqual(expected, out.getvalue())

    def test_try_catch(self):
        """Test generating try/catch control flow."""
        # Create a method with try/catch logic
        unsafe_method = (
            MethodSpec.method_builder("unsafeOperation")
            .add_modifiers(Modifier.PUBLIC)
            .returns("void")
            .begin_control_flow("try")
            .add_statement("throw new $T($S)", ClassName.get("java.lang", "Exception"), "Failed")
            .next_control_flow("catch ($T e)", ClassName.get("java.lang", "Exception"))
            .add_statement("throw new $T(e)", ClassName.get("com.example.error", "CustomException"))
            .end_control_flow()
            .build()
        )

        # Create the class
        error_handler = (
            TypeSpec.class_builder("ErrorHandler").add_modifiers(Modifier.PUBLIC).add_method(unsafe_method).build()
        )

        # Create the Java file
        java_file = JavaFile.builder("com.example.error", error_handler).build()

        # Write to a string buffer
        out = StringIO()
        java_file.write_to(out)

        # Check the output
        expected = """\
package com.example.error;

public class ErrorHandler {
  public void unsafeOperation() {
    try {
      throw new Exception("Failed");
    } catch (Exception e) {
      throw new CustomException(e);
    }
  }
}
"""
        self.assertEqual(expected, out.getvalue())
