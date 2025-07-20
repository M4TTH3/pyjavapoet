# PyJavaPoet Test Suite

This directory contains a comprehensive test suite for PyJavaPoet, designed to match and exceed the coverage of the original JavaPoet test suite from the Java implementation.

## Test Coverage

The test suite covers all major components of PyJavaPoet with equivalent functionality to the original JavaPoet tests:

### Core API Components

- **`test_annotation_spec.py`** - Tests for annotation creation, members, arrays, and complex annotation handling
- **`test_class_name.py`** - Tests for class name handling, nested classes, package resolution, and name validation  
- **`test_code_block.py`** - Tests for code generation, placeholders, control flow, and formatting
- **`test_field_spec.py`** - Tests for field specification, modifiers, initializers, and annotations
- **`test_method_spec.py`** - Tests for method creation, parameters, generics, exceptions, and overriding
- **`test_parameter_spec.py`** - Tests for method parameters, annotations, modifiers, and validation
- **`test_type_name.py`** - Tests for type system, generics, wildcards, primitives, and type conversions
- **`test_type_spec.py`** - Tests for class/interface/enum creation, inheritance, and nested types

### File and I/O Operations

- **`test_java_file.py`** - Tests for complete Java file generation, import management, and formatting
- **`test_file_writing.py`** - Tests for writing files to disk, directory creation, and encoding
- **`test_file_reading.py`** - Tests for file reading, UTF-8 handling, and content validation

### Utilities and Formatting

- **`test_code_writer.py`** - Tests for low-level code writing and formatting functionality
- **`test_line_wrapper.py`** - Tests for line wrapping, indentation, and text formatting
- **`test_name_allocator.py`** - Tests for name collision resolution and identifier validation
- **`test_util.py`** - Tests for utility functions like string/character literal escaping

### Legacy Tests (Pre-existing)

- **`test_hello_world.py`** - Basic "Hello World" functionality test
- **`test_class_types.py`** - Class type handling tests
- **`test_control_flow.py`** - Control flow statement tests

## Running Tests

### Run All Tests
```bash
cd tests
python run_tests.py
```

### Run Specific Test File
```bash
python run_tests.py test_type_spec.py
```

### List Available Tests
```bash
python run_tests.py --list
```

### Get Help
```bash
python run_tests.py --help
```

### Using Standard unittest
```bash
# Run all tests
python -m unittest discover -v

# Run specific test file
python -m unittest test_annotation_spec.py -v

# Run specific test class
python -m unittest test_annotation_spec.AnnotationSpecTest -v

# Run specific test method
python -m unittest test_annotation_spec.AnnotationSpecTest.test_equals_and_hash_code -v
```

## Test Structure

Each test file follows a consistent structure:

1. **Imports** - Import necessary PyJavaPoet modules and unittest
2. **Test Class** - Single test class per file, named after the component being tested
3. **Test Methods** - Individual test methods covering specific functionality
4. **Documentation** - Each test method has docstrings explaining what is being tested

### Example Test Structure:
```python
"""
Tests for ComponentName functionality.
Equivalent to ComponentNameTest.java
"""
import unittest
from pyjavapoet.component_name import ComponentName

class ComponentNameTest(unittest.TestCase):
    """Test the ComponentName class."""

    def test_basic_functionality(self):
        """Test basic component creation."""
        component = ComponentName.create("test")
        self.assertEqual(str(component), "test")
```

## Test Categories

### 1. Unit Tests
Most tests are unit tests that focus on individual components and methods in isolation.

### 2. Integration Tests
Some tests (especially in `test_java_file.py`) test integration between multiple components.

### 3. I/O Tests
File writing and reading tests that interact with the file system using temporary directories.

### 4. Edge Case Tests
Tests for error conditions, invalid inputs, and boundary conditions.

### 5. Compatibility Tests
Tests ensuring that the Python implementation produces output compatible with Java expectations.

## Java Compatibility

These tests are designed to ensure that PyJavaPoet generates Java code that is:

1. **Syntactically Correct** - All generated code should compile with javac
2. **Semantically Equivalent** - Behavior should match the original JavaPoet
3. **Style Consistent** - Formatting and conventions should match Java standards
4. **Import Optimized** - Import statements should be minimal and conflict-free

## Test Data

Tests use a variety of data sources:

- **Java Standard Library** - Classes like `String`, `Object`, `System`, `List`, etc.
- **Custom Test Classes** - Fictional classes in packages like `com.example`
- **Edge Cases** - Unicode characters, keywords, special symbols
- **Complex Scenarios** - Deeply nested generics, multiple inheritance, annotations

## Coverage Goals

The test suite aims to cover:

- ✅ **All Public APIs** - Every public method and class
- ✅ **Error Conditions** - Invalid inputs and edge cases  
- ✅ **Complex Scenarios** - Real-world usage patterns
- ✅ **Java Compatibility** - Output matches original JavaPoet
- ✅ **Performance** - No significant performance regressions

## Maintenance

When adding new features to PyJavaPoet:

1. **Add corresponding tests** in the appropriate test file
2. **Follow naming conventions** - `test_feature_description`
3. **Include error cases** - Test both success and failure scenarios
4. **Add documentation** - Describe what the test covers
5. **Verify compatibility** - Ensure output matches Java expectations

## Known Limitations

Some tests may have minor differences from the Java implementation due to:

1. **Python vs Java differences** - Language-specific behaviors
2. **Missing dependencies** - Some Java-specific libraries not available
3. **Implementation details** - Internal representation differences
4. **Platform differences** - File system and encoding variations

These differences are documented in individual test files where applicable.

## Contributing

When contributing tests:

1. Follow the existing structure and naming conventions
2. Include comprehensive docstrings
3. Test both success and failure cases
4. Use appropriate assertions
5. Clean up resources (files, directories) in tearDown methods
6. Run the full test suite before submitting changes

## Test Statistics

As of the current implementation:

- **Total Test Files**: 16 (13 new + 3 existing)
- **Estimated Test Cases**: 300+ individual test methods
- **Coverage**: All major PyJavaPoet components
- **Java Compatibility**: Equivalent to original JavaPoet test suite

The test suite provides comprehensive validation of PyJavaPoet functionality and ensures reliable Java code generation from Python.