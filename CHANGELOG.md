# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README with usage examples and generated Java code samples
- Installation instructions for pip and source installation
- Examples covering all major features:
  - Basic class, interface, and enum creation
  - Generic types and type variables
  - Annotations and Javadoc
  - Complex control flow structures
  - Records (Java 14+)
  - File I/O operations

### Changed
- Updated README structure with clear Python-to-Java code mappings
- Enhanced documentation with working examples

## [0.0.1] - 2025-07-29

Initial port of JavaPoet from Java to Python, maintaining the fluent builder pattern and core functionality while adapting for Python conventions.

### Core API Structure
- **Fluent Builder Pattern**: Maintains JavaPoet's signature `.builder()...build()` pattern
- **Auto-importing**: Automatic import management with conflict resolution
- **String Substitution**: Similar `$T`, `$S`, `$L`, `$N` placeholder functionality
- **Code Generation**: Proper indentation, formatting, and Java syntax generation

### Key API Differences from Square's JavaPoet

#### Type System Adaptations
- **Python Native Types**: Support for Python string literals for simple Java types (`"int"`, `"String[]"`)
- **ClassName Usage**: More verbose - requires `ClassName.get("java.lang", "String")` instead of direct string for complex types
- **Type Variables**: `TypeVariableName.get("T")` follows same pattern as original
- **Parameterized Types**: `ParameterizedTypeName.get()` and `.with_type_arguments()` methods

#### Method Differences
- **Constructor Methods**: `MethodSpec.constructor_builder()` instead of `MethodSpec.constructorBuilder()`
- **Method Names**: Python snake_case conventions (e.g., `add_modifiers()` vs `addModifiers()`)
- **Parameter Handling**: Support for both string types and `ParameterSpec` objects
- **Control Flow**: `begin_control_flow()`, `next_control_flow()`, `end_control_flow()`

#### File Operations
- **Output Methods**: `print(java_file)` for console output, `.write_to()` for file streams
- **Directory Writing**: `.write_to_dir()` creates full package directory structure
- **Path Handling**: Uses Python's `pathlib.Path` for cross-platform compatibility

#### Python-Specific Features
- **String Handling**: Proper escaping for Python string literals in generated Java code
- **Import System**: Python-style imports in the library itself while generating Java imports
- **Error Handling**: Python exceptions and validation patterns

### Complete Codebase Port

All major JavaPoet components successfully ported:

- **`annotation_spec.py`** - Annotation generation with members and nested annotations
- **`code_writer.py`** - Core formatting engine adapted for Python I/O patterns
- **`field_spec.py`** - Field declarations with modifiers, initializers, and annotations
- **`java_file.py`** - File-level structure with package, imports, and type declarations
- **`method_spec.py`** - Method/constructor generation with parameters, exceptions, generics
- **`parameter_spec.py`** - Method parameters with annotations and modifiers
- **`type_name.py`** - Complete type system (ClassName, TypeVariableName, ParameterizedTypeName, etc.)
- **`type_spec.py`** - Class, interface, enum, annotation, and record generation

and the following files were added:
- **`code_block.py`** - Code block abstraction with placeholder substitution  
- **`modifier.py`** - Java modifiers (PUBLIC, PRIVATE, STATIC, etc.)
- **`util.py`** - Utility functions for validation and formatting

### Development Evolution

#### Initial Implementation (commits fd8321d - 7fad391)
- Set up basic project structure and core type system
- Implemented `TypeName` hierarchy and `CodeWriter` foundation
- Established string substitution and formatting patterns

#### Core Builder Implementation (commits 88fb813 - ad72d69)  
- Completed `ParameterSpec` and `MethodSpec` builders
- Implemented fluent API patterns throughout codebase
- Added comprehensive method generation capabilities

#### Full Feature Set (commits b30c4c1 - a6f5bc6)
- Completed all spec builders (`TypeSpec`, `FieldSpec`, `AnnotationSpec`)
- Added enum, interface, and record support
- Implemented complete type system with generics

#### Testing & Refinement (commits 351049b - 328240f)
- Comprehensive test suite covering all major features
- Import conflict resolution and canonical name handling
- Code formatting and style consistency with ruff

#### Final Polish (commits f856f45 - e39c0c6)
- Fixed inner class imports and canonical name usage
- Cleaned up copyright headers and licensing
- Removed experimental Nix configuration
- Finalized project structure and dependencies

### Added Features
- Complete Java source code generation API
- Support for all Java constructs: classes, interfaces, enums, annotations, records
- Generic types and bounded type variables  
- Method generation with complex control flow
- Field declarations with initializers
- Comprehensive annotation support
- Javadoc generation with proper formatting
- Automatic import management with conflict resolution
- File I/O with package directory structure creation
- Cross-platform path handling

### Python Ecosystem Integration
- Standard `setup.py`/`pyproject.toml` packaging
- Apache License 2.0 for compatibility
- Comprehensive test coverage with Python unittest
- Code quality tools integration (ruff formatting)
- Type hints and Python best practices