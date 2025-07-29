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

from typing import Any


def is_ascii_upper(s: str) -> bool:
    return s.isascii() and s.isupper()


def deep_copy(obj: Any) -> Any:
    if isinstance(obj, list):
        return [deep_copy(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: deep_copy(value) for key, value in obj.items()}
    elif hasattr(obj, "copy"):
        return obj.copy()
    else:
        return obj


def is_valid_java_identifier(s: str) -> bool:
    return s.isidentifier() and s not in JAVA_KEYWORDS


def throw_if_invalid_java_identifier(s: str) -> None:
    if not is_valid_java_identifier(s):
        raise ValueError(f"String '{s}' is not a valid Java identifier")


JAVA_KEYWORDS = {
    # All Java keywords (including reserved literals)
    # that cannot be used as identifiers for fields, parameters, or values.
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
    # Reserved literals
    "true",
    "false",
    "null",
}
