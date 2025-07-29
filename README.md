# PyJavaPoet

`PyJavaPoet` is a Python API for generating `.java` source files, inspired by [JavaPoet](https://github.com/square/javapoet).

## Overview

Source file generation can be useful when doing things such as annotation processing or interacting
with metadata files (e.g., database schemas, protocol formats). By generating code, you eliminate
the need to write boilerplate while also keeping a single source of truth for the metadata.

## Features

- Generate Java classes, interfaces, enums, and annotations
- Create methods, fields, constructors, and parameters
- Support for modifiers, annotations, and Javadoc
- Proper handling of imports and type references
- Formatted output with proper indentation

## Warning

The current APIs are arguably too powerful and can generate syntactically invalid java code. Be cautious of usage, this API can create what you want, but it can also create what you don't want. 

*In the future, a tree-sitter API will be added to validate the generated code.*

## Installation

```bash
pip install pyjavapoet
```

Or install from source:

```bash
git clone https://github.com/m4tth3/python-java-poet.git
cd python-java-poet
pip install -e .
```

## Quick Start

Here's how to generate a simple "HelloWorld" Java class using PyJavaPoet:

**Python Code:**
```python
from pyjavapoet import MethodSpec, TypeSpec, JavaFile, Modifier, ClassName

# Create the main method
main = MethodSpec.method_builder("main") \
    .add_modifiers(Modifier.PUBLIC, Modifier.STATIC) \
    .returns("void") \
    .add_parameter("String[]", "args") \
    .add_statement("$T.out.println($S)", ClassName.get("java.lang", "System"), "Hello, PyJavaPoet!") \
    .build()

# Create the HelloWorld class
hello_world = TypeSpec.class_builder("HelloWorld") \
    .add_modifiers(Modifier.PUBLIC, Modifier.FINAL) \
    .add_method(main) \
    .build()

# Create the Java file
java_file = JavaFile.builder("com.example.helloworld", hello_world) \
    .build()

# Print the generated code
print(java_file)
```

**Generated Java Code:**
```java
package com.example.helloworld;

public final class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello, PyJavaPoet!");
  }
}
```

## Usage Examples

### 1. Creating a Data Class

**Python Code:**
```python
from pyjavapoet import TypeSpec, FieldSpec, MethodSpec, Modifier, ClassName, JavaFile

# Create a Person class
person_class = TypeSpec.class_builder("Person") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_field(FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
               .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
               .build()) \
    .add_field(FieldSpec.builder("int", "age")
               .add_modifiers(Modifier.PRIVATE)
               .build()) \
    .add_method(MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_parameter(ClassName.get("java.lang", "String"), "name")
                .add_parameter("int", "age")
                .add_statement("this.name = name")
                .add_statement("this.age = age")
                .build()) \
    .add_method(MethodSpec.method_builder("getName")
                .add_modifiers(Modifier.PUBLIC)
                .returns(ClassName.get("java.lang", "String"))
                .add_statement("return this.name")
                .build()) \
    .add_method(MethodSpec.method_builder("getAge")
                .add_modifiers(Modifier.PUBLIC)
                .returns("int")
                .add_statement("return this.age")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", person_class).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

public class Person {
  private final String name;
  private int age;

  public Person(String name, int age) {
    this.name = name;
    this.age = age;
  }

  public String getName() {
    return this.name;
  }

  public int getAge() {
    return this.age;
  }
}
```

### 2. Creating Interfaces with Default Methods

**Python Code:**
```python
from pyjavapoet import TypeSpec, MethodSpec, Modifier, JavaFile

drawable = TypeSpec.interface_builder("Drawable") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(MethodSpec.method_builder("draw")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PUBLIC)
                .returns("void")
                .build()) \
    .add_method(MethodSpec.method_builder("paint")
                .add_modifiers(Modifier.DEFAULT, Modifier.PUBLIC)
                .returns("void")
                .add_statement("draw()")
                .add_statement("System.out.println($S)", "Painting completed")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", drawable).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

public interface Drawable {
  public abstract void draw();

  public default void paint() {
    draw();
    System.out.println("Painting completed");
  }
}
```

### 3. Creating Enums with Custom Methods

**Python Code:**
```python
from pyjavapoet import TypeSpec, MethodSpec, Modifier, AnnotationSpec, ClassName, JavaFile

roshambo = TypeSpec.enum_builder("Roshambo") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_enum_constant_with_class_body("ROCK",
        TypeSpec.anonymous_class_builder("")
        .add_method(MethodSpec.method_builder("toString")
                    .add_annotation(AnnotationSpec.get(ClassName.get("java.lang", "Override")))
                    .add_modifiers(Modifier.PUBLIC)
                    .returns(ClassName.get("java.lang", "String"))
                    .add_statement("return $S", "Rock beats scissors!")
                    .build())
        .build()) \
    .add_enum_constant("PAPER") \
    .add_enum_constant("SCISSORS") \
    .build()

java_file = JavaFile.builder("com.example", roshambo).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

public enum Roshambo {
  ROCK {
    @Override
    public String toString() {
      return "Rock beats scissors!";
    }
  },
  PAPER,
  SCISSORS
}
```

### 4. Working with Generics and Type Variables

**Python Code:**
```python
from pyjavapoet import TypeSpec, MethodSpec, FieldSpec, Modifier, ClassName, TypeVariableName, ParameterizedTypeName, JavaFile

# Create type variables
t = TypeVariableName.get("T")
r = TypeVariableName.get("R")

# Define classes we'll use
list_class = ClassName.get("java.util", "List")
array_list_class = ClassName.get("java.util", "ArrayList")
function_class = ParameterizedTypeName.get(ClassName.get("java.util.function", "Function"), t, r)

# Create a generic data processor class
processor = TypeSpec.class_builder("DataProcessor") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_field(FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
               .add_modifiers(Modifier.PRIVATE, Modifier.FINAL)
               .build()) \
    .add_method(MethodSpec.constructor_builder()
                .add_modifiers(Modifier.PUBLIC)
                .add_parameter(ClassName.get("java.lang", "String"), "name")
                .add_statement("this.name = name")
                .build()) \
    .add_method(MethodSpec.method_builder("process")
                .add_modifiers(Modifier.PUBLIC)
                .add_type_variable(t)
                .add_type_variable(r)
                .returns(ParameterizedTypeName.get(list_class, r))
                .add_parameter(ParameterizedTypeName.get(list_class, t), "input")
                .add_parameter(function_class, "transformer")
                .add_statement("$T<$T> result = new $T<>()", list_class, r, array_list_class)
                .begin_control_flow("for ($T item : input)", t)
                .add_statement("result.add(transformer.apply(item))")
                .end_control_flow()
                .add_statement("return result")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", processor).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class DataProcessor {
  private final String name;

  public DataProcessor(String name) {
    this.name = name;
  }

  public <T, R> List<R> process(List<T> input, Function<T, R> transformer) {
    List<R> result = new ArrayList<>();
    for (T item : input) {
      result.add(transformer.apply(item));
    }
    return result;
  }
}
```

### 5. Adding Annotations and Javadoc

**Python Code:**
```python
from pyjavapoet import TypeSpec, MethodSpec, FieldSpec, AnnotationSpec, Modifier, ClassName, JavaFile

# Create annotations
nullable = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
component = AnnotationSpec.builder(ClassName.get("org.springframework.stereotype", "Component")) \
    .add_member("value", "$S", "userService") \
    .build()

# Create a service class with annotations and javadoc
service = TypeSpec.class_builder("UserService") \
    .add_annotation(component) \
    .add_modifiers(Modifier.PUBLIC) \
    .add_javadoc("Service class for managing users.\n") \
    .add_javadoc("\n") \
    .add_javadoc("@author PyJavaPoet\n") \
    .add_javadoc("@since 1.0\n") \
    .add_field(FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
               .add_annotation(nullable)
               .add_modifiers(Modifier.PRIVATE)
               .build()) \
    .add_method(MethodSpec.method_builder("getName")
                .add_javadoc("Gets the user name.\n")
                .add_javadoc("\n")
                .add_javadoc("@return the user name, or null if not set\n")
                .add_annotation(nullable)
                .add_modifiers(Modifier.PUBLIC)
                .returns(ClassName.get("java.lang", "String"))
                .add_statement("return this.name")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", service).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

import javax.annotation.Nullable;
import org.springframework.stereotype.Component;

/**
 * Service class for managing users.
 * 
 * @author PyJavaPoet
 * @since 1.0
 */
@Component("userService")
public class UserService {
  @Nullable
  private String name;

  /**
   * Gets the user name.
   * 
   * @return the user name, or null if not set
   */
  @Nullable
  public String getName() {
    return this.name;
  }
}
```

### 6. Complex Control Flow

**Python Code:**
```python
from pyjavapoet import MethodSpec, Modifier, ClassName, JavaFile, TypeSpec

# Method with complex control flow
process_method = MethodSpec.method_builder("processItems") \
    .add_modifiers(Modifier.PUBLIC) \
    .returns("void") \
    .add_parameter(ClassName.get("java.util", "List").with_type_arguments(ClassName.get("java.lang", "String")), "items") \
    .begin_control_flow("for (String item : items)") \
    .begin_control_flow("if (item != null && !item.isEmpty())") \
    .add_statement("System.out.println($S + item)", "Processing: ") \
    .begin_control_flow("try") \
    .add_statement("processItem(item)") \
    .next_control_flow("catch ($T e)", ClassName.get("java.lang", "Exception")) \
    .add_statement("System.err.println($S + e.getMessage())", "Error processing item: ") \
    .end_control_flow() \
    .next_control_flow("else") \
    .add_statement("System.out.println($S)", "Skipping null or empty item") \
    .end_control_flow() \
    .end_control_flow() \
    .build()

# Wrap in a class for complete example
processor_class = TypeSpec.class_builder("ItemProcessor") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(process_method) \
    .add_method(MethodSpec.method_builder("processItem")
                .add_modifiers(Modifier.PRIVATE)
                .returns("void")
                .add_parameter(ClassName.get("java.lang", "String"), "item")
                .add_exception(ClassName.get("java.lang", "Exception"))
                .add_statement("// Process the item")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", processor_class).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

import java.util.List;

public class ItemProcessor {
  public void processItems(List<String> items) {
    for (String item : items) {
      if (item != null && !item.isEmpty()) {
        System.out.println("Processing: " + item);
        try {
          processItem(item);
        } catch (Exception e) {
          System.err.println("Error processing item: " + e.getMessage());
        }
      } else {
        System.out.println("Skipping null or empty item");
      }
    }
  }

  private void processItem(String item) throws Exception {
    // Process the item
  }
}
```

### 7. Records (Java 14+)

**Python Code:**
```python
from pyjavapoet import TypeSpec, ParameterSpec, Modifier, ClassName, JavaFile

# Create a record
point_record = TypeSpec.record_builder("Point") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_record_component(ParameterSpec.builder("int", "x").build()) \
    .add_record_component(ParameterSpec.builder("int", "y").build()) \
    .add_superinterface(ClassName.get("java.io", "Serializable")) \
    .build()

java_file = JavaFile.builder("com.example", point_record).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

import java.io.Serializable;

public record Point(int x, int y) implements Serializable {
}
```

### 8. Writing Files to Disk

```python
from pyjavapoet import JavaFile
from pathlib import Path

# Create a Java file and write it to disk
java_file = JavaFile.builder("com.example", my_class).build()

# Write to a directory (creates package structure)
output_dir = Path("src/main/java")
file_path = java_file.write_to_dir(output_dir)
print(f"File written to: {file_path}")

# Or write to a specific file
with open("MyClass.java", "w") as f:
    java_file.write_to(f)
```

## Extra Usages

### MethodSpec
We provide the following API alternative to .add_statement(...)

**Python Code**
```py
MethodSpec.method_builder("test") \
.add_statement("StringBuilder $L = new StringBuilder()", "builder") \
.begin_statement("$L", "builder") \
.add_statement_item(".append($S)", "hello") \
.add_statement_item(".append($S)", "world") \
.end_statement()
.build()
```

**Generated Java Code**
```java
void test() {
  StringBuilder builder = new StringBuilder();
  builder
      .append("hello")
      .append("world");
}
```

## TODOs

1. Add better api for beginStatement and endStatement in MethodSpec
2. TreeSitter API to synactically validate java file
3. Add kwargs to method spec builder. Currently code block will have an issue of overwriting previous
   keys if re-specified and so I have removed it.
4. Text wrapping on CodeWriter
5. Code Block update statement to use `$[` and `$]`
6. Name Allocator if we so desire (?)
7. Annotation member has to be valid java identifier
8. Handle primitive types better in ClassName i.e. validation
9. Improve tests with exact output strings and also slim down unneeded tests
10. Pass in TypeSpec for Types as well (for nested classes) ? It might work and we can include a self key too

## License

PyJavaPoet is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

Credit: This project is inspired by [JavaPoet](https://github.com/square/javapoet) and is licensed under the Apache License 2.0.
