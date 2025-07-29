"""
PyJavaPoet: A Python API for generating Java source files.
"""

__version__ = "0.0.0"

# ruff: noqa
# PyJavaPoet top-level package: expose main classes for convenience
from pyjavapoet.annotation_spec import AnnotationSpec
from pyjavapoet.code_block import CodeBlock
from pyjavapoet.field_spec import FieldSpec
from pyjavapoet.java_file import JavaFile
from pyjavapoet.method_spec import MethodSpec
from pyjavapoet.modifier import Modifier
from pyjavapoet.parameter_spec import ParameterSpec
from pyjavapoet.type_name import (
    ArrayTypeName,
    ClassName,
    ParameterizedTypeName,
    TypeName,
    TypeVariableName,
    WildcardTypeName,
)
from pyjavapoet.type_spec import TypeSpec
