# PyPoet

`PyPoet` is a Python API for generating `.java` source files, inspired by [JavaPoet](https://github.com/palantir/javapoet).

## Overview

Source file generation can be useful when doing things such as annotation processing or interacting
with metadata files (e.g., database schemas, protocol formats). By generating code, you eliminate
the need to write boilerplate while also keeping a single source of truth for the metadata.

## Installation

```bash
pip install pypoet
```

## Example

Here's how to generate a simple "HelloWorld" Java class using PyPoet:

```python
from pypoet import MethodSpec, TypeSpec, JavaFile, Modifier

# Create the main method
main = MethodSpec.method_builder("main") \
    .add_modifiers(Modifier.PUBLIC, Modifier.STATIC) \
    .returns("void") \
    .add_parameter("String[]", "args") \
    .add_statement('$T.out.println($S)', "System", "Hello, PyPoet!") \
    .build()

# Create the HelloWorld class
hello_world = TypeSpec.class_builder("HelloWorld") \
    .add_modifiers(Modifier.PUBLIC, Modifier.FINAL) \
    .add_method(main) \
    .build()

# Create the Java file
java_file = JavaFile.builder("com.example.helloworld", hello_world) \
    .build()

# Print the Java file to stdout
java_file.write_to(sys.stdout)
```

This will generate:

```java
package com.example.helloworld;

public final class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello, PyPoet!");
  }
}
```

## Features

- Generate Java classes, interfaces, enums, and annotations
- Create methods, fields, constructors, and parameters
- Support for modifiers, annotations, and Javadoc
- Proper handling of imports and type references
- Formatted output with proper indentation and line breaks

## License

MIT License