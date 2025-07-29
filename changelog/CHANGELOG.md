## 2025-07-29
- Initial port of JavaPoet to Python.
  - Similar APIs structure using fluent builder pattern and auto-importing.
  - Also allows for similar string substitution functionality.
  - Uses a similar API to JavaPoet's CodeWriter, but adapted for Python.
  - Supports python native types for substitution, but is limited to other java classes and need to be more verbose.
- Specific API usage will probably be changed and/or limited, see the README.md for more details on the current API

Code Ported:
- pyjavapoet/annotation_spec.py
- pyjavapoet/code_block.py
- pyjavapoet/code_writer.py
- pyjavapoet/field_spec.py
- pyjavapoet/java_file.py
- pyjavapoet/method_spec.py
- pyjavapoet/parameter_spec.py
- pyjavapoet/type_name.py (includes all TypeName implementations)
- pyjavapoet/type_spec.py
