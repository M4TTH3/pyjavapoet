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

**Interface Method Modifiers:**

PyJavaPoet correctly handles interface methods with and without explicit modifiers:

**Python Code:**
```python
# Interface method with explicit public modifier  
interface_with_modifiers = TypeSpec.interface_builder("TestInterface") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(MethodSpec.method_builder("word")
                .add_modifiers(Modifier.PUBLIC)
                .returns("void")
                .build()) \
    .build()

java_file = JavaFile.builder("com.example", interface_with_modifiers).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

public interface TestInterface {
  public void word();
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
    .add_javadoc_line("Service class for managing users.") \
    .add_javadoc_line() \
    .add_javadoc_line("@author PyJavaPoet") \
    .add_javadoc_line("@since 1.0") \
    .add_field(FieldSpec.builder(ClassName.get("java.lang", "String"), "name")
               .add_annotation(nullable)
               .add_modifiers(Modifier.PRIVATE)
               .build()) \
    .add_method(MethodSpec.method_builder("getName")
                .add_javadoc_line("Gets the user name.")
                .add_javadoc_line()
                .add_javadoc_line("@return the user name, or null if not set")
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

### 7. Statement Chaining

PyJavaPoet supports fluent method chaining for building statements:

**Python Code:**
```python
from pyjavapoet import MethodSpec, TypeSpec, JavaFile, Modifier

# Method with statement chaining
method = MethodSpec.method_builder("buildString") \
    .add_modifiers(Modifier.PUBLIC) \
    .returns("String") \
    .add_statement("StringBuilder $L = new StringBuilder()", "builder") \
    .begin_statement_chain("$L", "builder") \
    .add_chained_item(".append($S)", "Hello") \
    .add_chained_item(".append($S)", " ") \
    .add_chained_item(".append($S)", "World") \
    .end_statement_chain() \
    .add_statement("return $L.toString()", "builder") \
    .build()

clazz = TypeSpec.class_builder("StringBuilderExample") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(method) \
    .build()

java_file = JavaFile.builder("com.example", clazz).build()
print(java_file)
```

**Generated Java Code:**
```java
package com.example;

public class StringBuilderExample {
  public String buildString() {
    StringBuilder builder = new StringBuilder();
    builder
        .append("Hello")
        .append(" ")
        .append("World");
    return builder.toString();
  }
}
```

### 8. Records (Java 14+)

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

### 9. Writing Files to Disk

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

## API Reference

This section provides detailed documentation for each PyJavaPoet component with examples and their generated output.

### TypeName Classes

TypeName is the foundation for representing Java types in PyJavaPoet.

#### ClassName

Represents class and interface types, including nested classes.

```python
from pyjavapoet import ClassName

# Basic class names
string_class = ClassName.get("java.lang", "String")
print(str(string_class))  # Output: java.lang.String

list_class = ClassName.get("java.util", "List")  
print(str(list_class))    # Output: java.util.List

# Nested classes
nested_class = ClassName.get("com.example", "Outer", "Inner")
print(str(nested_class))  # Output: com.example.Outer.Inner

# Common predefined types
print(str(ClassName.OBJECT))    # Output: java.lang.Object
print(str(ClassName.STRING))    # Output: java.lang.String
```

#### TypeName

Base class for all type representations, provides common type constants.

```python
from pyjavapoet import TypeName

# Primitive types
print(str(TypeName.get("int")))     # Output: int
print(str(TypeName.get("boolean"))) # Output: boolean
print(str(TypeName.get("void")))    # Output: void

# Predefined constants
print(str(ClassName.INT))     # Output: int
print(str(ClassName.BOOLEAN)) # Output: boolean
print(str(ClassName.VOID))    # Output: void
print(str(ClassName.STRING))  # Output: java.lang.String
```

#### ArrayTypeName

Represents array types with support for multi-dimensional arrays.

```python
from pyjavapoet import ArrayTypeName, ClassName

string_class = ClassName.get("java.lang", "String")

# Single-dimensional array
string_array = ArrayTypeName.of(string_class)
print(str(string_array))     # Output: String[]

# Multi-dimensional arrays
int_2d_array = ArrayTypeName.of(ArrayTypeName.of("int"))
print(str(int_2d_array))     # Output: int[][]

# Primitive arrays
int_array = ArrayTypeName.of("int")
print(str(int_array))        # Output: int[]
```

#### ParameterizedTypeName

Represents generic types with type arguments.

```python
from pyjavapoet import ParameterizedTypeName, ClassName

list_class = ClassName.get("java.util", "List")
string_class = ClassName.get("java.lang", "String")
integer_class = ClassName.get("java.lang", "Integer")

# List<String>
list_of_strings = ParameterizedTypeName.get(list_class, string_class)
print(str(list_of_strings))  # Output: List<String>

# Alternative syntax
list_of_strings2 = list_class.with_type_arguments(string_class)
print(str(list_of_strings2)) # Output: List<String>

# Map<String, Integer>  
map_class = ClassName.get("java.util", "Map")
map_string_int = ParameterizedTypeName.get(map_class, string_class, integer_class)
print(str(map_string_int))   # Output: Map<String, Integer>

# Nested parameterized types: Map<String, List<String>>
list_of_strings = ParameterizedTypeName.get(list_class, string_class)
map_nested = ParameterizedTypeName.get(map_class, string_class, list_of_strings)
print(str(map_nested))       # Output: Map<String, List<String>>
```

#### TypeVariableName

Represents generic type variables with optional bounds.

```python
from pyjavapoet import TypeVariableName, ClassName

# Basic type variable
t_var = TypeVariableName.get("T")
print(str(t_var))            # Output: T

# Bounded type variable
number_class = ClassName.get("java.lang", "Number")
bounded_t = TypeVariableName.get("T", number_class)
print(str(bounded_t))        # Output: T extends Number

# Multiple bounds
comparable_class = ClassName.get("java.lang", "Comparable")
serializable_class = ClassName.get("java.io", "Serializable")
multi_bounded = TypeVariableName.get("T", number_class, comparable_class, serializable_class)
print(str(multi_bounded))    # Output: T extends Number & Comparable & Serializable
```

#### WildcardTypeName

Represents wildcard types with upper and lower bounds.

```python
from pyjavapoet import WildcardTypeName, ClassName

number_class = ClassName.get("java.lang", "Number")
object_class = ClassName.get("java.lang", "Object")

# ? extends Number
extends_number = WildcardTypeName.subtypes_of(number_class)
print(str(extends_number))   # Output: ? extends Number

# ? super Number
super_number = WildcardTypeName.supertypes_of(number_class)
print(str(super_number))     # Output: ? super Number

# Unbounded wildcard (? extends Object becomes just ?)
unbounded = WildcardTypeName.subtypes_of(object_class)
print(str(unbounded))        # Output: ?
```

### Specification Classes

#### FieldSpec

Represents field declarations with modifiers, initializers, and annotations.

```python
from pyjavapoet import FieldSpec, Modifier, ClassName, AnnotationSpec

# Basic field
basic_field = FieldSpec.builder("int", "count").build()
print(str(basic_field))      # Output: int count;

# Field with modifiers
private_field = FieldSpec.builder(ClassName.get("java.lang", "String"), "name") \
    .add_modifiers(Modifier.PRIVATE, Modifier.FINAL) \
    .build()
print(str(private_field))    # Output: private final String name;

# Field with initializer
initialized_field = FieldSpec.builder("int", "counter") \
    .add_modifiers(Modifier.PRIVATE, Modifier.STATIC) \
    .initializer("$L", 0) \
    .build()
print(str(initialized_field)) # Output: private static int counter = 0;

# Field with annotation
nullable = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
annotated_field = FieldSpec.builder(ClassName.get("java.lang", "String"), "value") \
    .add_annotation(nullable) \
    .build()
print(str(annotated_field))  # Output: @Nullable\nString value;

# Generic field
list_class = ClassName.get("java.util", "List")
string_class = ClassName.get("java.lang", "String")
list_field = FieldSpec.builder(list_class.with_type_arguments(string_class), "items") \
    .add_modifiers(Modifier.PRIVATE, Modifier.FINAL) \
    .initializer("new $T<>()", ClassName.get("java.util", "ArrayList")) \
    .build()
print(str(list_field))       # Output: private final List<String> items = new ArrayList<>();
```

#### ParameterSpec

Represents method/constructor parameters with annotations.

```python
from pyjavapoet import ParameterSpec, ClassName, AnnotationSpec

# Basic parameter
basic_param = ParameterSpec.builder("int", "value").build()
print(str(basic_param))      # Output: int value

# Parameter with annotation
nullable = AnnotationSpec.builder(ClassName.get("javax.annotation", "Nullable")).build()
annotated_param = ParameterSpec.builder(ClassName.get("java.lang", "String"), "name") \
    .add_annotation(nullable) \
    .build()
print(str(annotated_param))  # Output: @Nullable String name

# Generic parameter
list_class = ClassName.get("java.util", "List")
string_class = ClassName.get("java.lang", "String")
generic_param = ParameterSpec.builder(list_class.with_type_arguments(string_class), "items").build()
print(str(generic_param))    # Output: List<String> items

# Varargs parameter  
varargs_param = ParameterSpec.builder("String...", "args").build()
print(str(varargs_param))    # Output: String... args
```

#### MethodSpec

Represents method and constructor declarations with full support for Java features.

```python
from pyjavapoet import MethodSpec, Modifier, ClassName, TypeVariableName, ParameterSpec

# Basic method
basic_method = MethodSpec.method_builder("getName") \
    .add_modifiers(Modifier.PUBLIC) \
    .returns(ClassName.get("java.lang", "String")) \
    .add_statement("return this.name") \
    .build()
print(str(basic_method))
# Output:
# public String getName() {
#   return this.name;
# }

# Constructor
constructor = MethodSpec.constructor_builder() \
    .add_modifiers(Modifier.PUBLIC) \
    .add_parameter(ClassName.get("java.lang", "String"), "name") \
    .add_statement("this.name = name") \
    .build()
print(str(constructor))
# Output:
# public <init>(String name) {
#   this.name = name;
# }

# Generic method
t_var = TypeVariableName.get("T")
generic_method = MethodSpec.method_builder("identity") \
    .add_type_variable(t_var) \
    .add_modifiers(Modifier.PUBLIC, Modifier.STATIC) \
    .returns(t_var) \
    .add_parameter(t_var, "input") \
    .add_statement("return input") \
    .build()
print(str(generic_method))
# Output:
# public static <T> T identity(T input) {
#   return input;
# }

# Method with Javadoc
documented_method = MethodSpec.method_builder("calculate") \
    .add_javadoc_line("Calculates the result.") \
    .add_javadoc_line() \
    .add_javadoc_line("@param input the input value") \
    .add_javadoc_line("@return the calculated result") \
    .add_modifiers(Modifier.PUBLIC) \
    .returns("int") \
    .add_parameter("int", "input") \
    .add_statement("return input * 2") \
    .build()
print(str(documented_method))
# Output:
# /**
#  * Calculates the result.
#  * 
#  * @param input the input value
#  * @return the calculated result
#  */
# public int calculate(int input) {
#   return input * 2;
# }

# Abstract method (no body)
abstract_method = MethodSpec.method_builder("process") \
    .add_modifiers(Modifier.PUBLIC, Modifier.ABSTRACT) \
    .returns("void") \
    .add_parameter("Object", "data") \
    .build()
print(str(abstract_method))
# Output: public abstract void process(Object data);
```

#### AnnotationSpec

Represents Java annotations with members and values.

```python
from pyjavapoet import AnnotationSpec, ClassName

# Basic annotation
override = AnnotationSpec.builder(ClassName.get("java.lang", "Override")).build()
print(str(override))         # Output: @Override

# Annotation with single value
component = AnnotationSpec.builder(ClassName.get("org.springframework.stereotype", "Component")) \
    .add_member("value", "$S", "userService") \
    .build()
print(str(component))        # Output: @Component("userService")

# Annotation with multiple members
request_mapping = AnnotationSpec.builder(ClassName.get("org.springframework.web.bind.annotation", "RequestMapping")) \
    .add_member("value", "$S", "/api/users") \
    .add_member("method", "$T.GET", ClassName.get("org.springframework.web.bind.annotation", "RequestMethod")) \
    .build()
print(str(request_mapping))
# Output: @RequestMapping(value = "/api/users", method = RequestMethod.GET)

# Annotation with array values
suppress_warnings = AnnotationSpec.builder(ClassName.get("java.lang", "SuppressWarnings")) \
    .add_member("value", "{$S, $S}", "unchecked", "rawtypes") \
    .build()
print(str(suppress_warnings)) # Output: @SuppressWarnings({"unchecked", "rawtypes"})

# Shorthand for single-member annotations
get_annotation = AnnotationSpec.get(ClassName.get("java.lang", "Override"))
print(str(get_annotation))   # Output: @Override
```

#### TypeSpec

Represents type declarations: classes, interfaces, enums, annotations, and records.

```python
from pyjavapoet import TypeSpec, Modifier, ClassName, FieldSpec, MethodSpec

# Basic class
basic_class = TypeSpec.class_builder("BasicClass").build()
print(str(basic_class))
# Output:
# class BasicClass {
# }

# Class with inheritance and interfaces
extended_class = TypeSpec.class_builder("MyClass") \
    .add_modifiers(Modifier.PUBLIC) \
    .superclass(ClassName.get("com.example", "BaseClass")) \
    .add_superinterface(ClassName.get("java.io", "Serializable")) \
    .add_superinterface(ClassName.get("java.lang", "Cloneable")) \
    .build()
print(str(extended_class))
# Output:
# public class MyClass extends BaseClass implements Serializable, Cloneable {
# }

# Interface
interface = TypeSpec.interface_builder("Drawable") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(MethodSpec.method_builder("draw")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PUBLIC)
                .returns("void")
                .build()) \
    .build()
print(str(interface))
# Output:
# public interface Drawable {
#   public abstract void draw();
# }

# Enum
color_enum = TypeSpec.enum_builder("Color") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_enum_constant("RED") \
    .add_enum_constant("GREEN") \
    .add_enum_constant("BLUE") \
    .build()
print(str(color_enum))
# Output:
# public enum Color {
#   RED,
#   GREEN,
#   BLUE
# }

# Annotation type
annotation_type = TypeSpec.annotation_builder("MyAnnotation") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_method(MethodSpec.method_builder("value")
                .add_modifiers(Modifier.ABSTRACT, Modifier.PUBLIC)
                .returns(ClassName.get("java.lang", "String"))
                .build()) \
    .build()
print(str(annotation_type))
# Output:
# public @interface MyAnnotation {
#   public abstract String value();
# }

# Record (Java 14+)
point_record = TypeSpec.record_builder("Point") \
    .add_modifiers(Modifier.PUBLIC) \
    .add_record_component(ParameterSpec.builder("int", "x").build()) \
    .add_record_component(ParameterSpec.builder("int", "y").build()) \
    .build()
print(str(point_record))
# Output:
# public record Point(int x, int y) {
# }

# Anonymous class
anonymous = TypeSpec.anonymous_class_builder("") \
    .add_superinterface(ClassName.get("java.lang", "Runnable")) \
    .add_method(MethodSpec.method_builder("run")
                .add_modifiers(Modifier.PUBLIC)
                .returns("void")
                .add_statement("System.out.println($S)", "Running!")
                .build()) \
    .build()
print(str(anonymous))
# Output:
# new Runnable() {
#   @Override
#   public void run() {
#     System.out.println("Running!");
#   }
# }
```

#### JavaFile

Represents a complete Java source file with package, imports, and type declarations.

```python
from pyjavapoet import JavaFile, TypeSpec, Modifier

# Basic Java file
simple_class = TypeSpec.class_builder("HelloWorld") \
    .add_modifiers(Modifier.PUBLIC) \
    .build()

java_file = JavaFile.builder("com.example", simple_class).build()
print(str(java_file))
# Output:
# package com.example;
# 
# public class HelloWorld {
# }

# Java file with imports and file comment
java_file_with_imports = JavaFile.builder("com.example", simple_class) \
    .add_file_comment_line("This is a generated file.") \
    .add_file_comment_line("Do not edit manually.") \
    .add_static_import(ClassName.get("java.lang", "System"), "out") \
    .build()
print(str(java_file_with_imports))
# Output:  
# /**
#  * This is a generated file.
#  * Do not edit manually.
#  */
# package com.example;
# 
# import static java.lang.System.out;
# 
# public class HelloWorld {
# }
```

### Builder Pattern Methods

All spec classes follow the builder pattern with these common methods:

- **`.builder()`** - Creates a new builder instance
- **`.to_builder()`** - Creates a builder from existing spec  
- **`.build()`** - Builds the final immutable spec
- **`.add_*(...)`** - Adds elements (modifiers, annotations, etc.)
- **`.returns(type)`** - Sets return type (MethodSpec only)
- **`.add_statement(format, ...args)`** - Adds code statements
- **`.begin_control_flow()`** / **`.end_control_flow()`** - Control structures

### Placeholder Syntax

PyJavaPoet uses placeholder syntax for safe code generation:

- **`$T`** - Type (TypeName, ClassName, etc.)
- **`$S`** - String literal (automatically escaped)  
- **`$L`** - Literal (numbers, variables, etc.)
- **`$N`** - Name (field/method names from specs)

```python
# Examples of placeholder usage
method = MethodSpec.method_builder("example") \
    .add_statement("$T list = new $T<>()", ClassName.get("java.util", "List"), ClassName.get("java.util", "ArrayList")) \
    .add_statement("list.add($S)", "Hello World") \
    .add_statement("int size = $L", 42) \
    .build()
```

## TODOs
I think of these as nice-ities, but they are more about convenience rather than correctness. There are work-arounds/other tools that can be used to create these desired affects.

1. TreeSitter API to synactically validate java file
2. Add kwargs to method spec builder. Currently code block will have an issue of overwriting previous
   keys if re-specified and so I have removed it.
3. Text wrapping on CodeWriter
4. Code Block update statement to use `$[` and `$]`
5. Name Allocator if we so desire (?)
6. Annotation member has to be valid java identifier
7. Handle primitive types better in ClassName i.e. validation
8. Pass in TypeSpec for Types as well (for nested classes) ? It might work and we can include a self key too

## License

PyJavaPoet is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

Credit: This project is inspired by [JavaPoet](https://github.com/square/javapoet) and is licensed under the Apache License 2.0.
