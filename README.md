# PyJavaPoet

`PyJavaPoet` is a Python API for generating `.java` source files, inspired by [JavaPoet](https://github.com/square/javapoet).

## Overview

Source file generation can be useful when doing things such as annotation processing or interacting
with metadata files (e.g., database schemas, protocol formats). By generating code, you eliminate
the need to write boilerplate while also keeping a single source of truth for the metadata.

## Installation

TODO

## Example

Here's how to generate a simple "HelloWorld" Java class using PyJavaPoet:

```python
from pyjavapoet import MethodSpec, TypeSpec, JavaFile, Modifier

# Create the main method
main = MethodSpec.method_builder("main") \
    .add_modifiers(Modifier.PUBLIC, Modifier.STATIC) \
    .returns("void") \
    .add_parameter("String[]", "args") \
    .add_statement('$T.out.println($S)', "System", "Hello, PyJavaPoet!") \
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
    System.out.println("Hello, PyJavaPoet!");
  }
}
```

## Features

- Generate Java classes, interfaces, enums, and annotations
- Create methods, fields, constructors, and parameters
- Support for modifiers, annotations, and Javadoc
- Proper handling of imports and type references
- Formatted output with proper indentation and line breaks

## These are a list of TODOs for the project

1. Text wrapping on CodeWriter
2. Code Block update statement to use `$[` and `$]`
3. Support positional arguments in CodeBlock and others
4. Add support for dictionary arguments in CodeBlock and others
5. Name Allocator if we so desire (?)
6. Annotation member has to be valid java identifier
7. Multiple imports with same ClassName should use package name
8. Handle primitive types better in ClassName i.e. validation
9. Improve tests with exact output strings and also slim down unneeded tests
10. Pass in TypeSpec for Types as well (for nested classes) ? It might work and we can include a self key too

## License

PyJavaPoet is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

Credit: This project is inspired by [JavaPoet](https://github.com/square/javapoet) and is licensed under the Apache License 2.0.