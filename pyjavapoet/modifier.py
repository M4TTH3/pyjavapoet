"""
Represents Java modifiers like public, private, static, etc.
"""

from enum import Enum


class Modifier(Enum):
    """
    Java modifiers used for classes, methods, fields, etc.

    This enum provides constants for all Java language modifiers.
    """

    # Access modifiers
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"

    # Method and class modifiers
    ABSTRACT = "abstract"
    DEFAULT = "default"
    STATIC = "static"
    FINAL = "final"
    SYNCHRONIZED = "synchronized"
    NATIVE = "native"
    STRICTFP = "strictfp"
    TRANSIENT = "transient"
    VOLATILE = "volatile"

    # Class-specific modifiers
    SEALED = "sealed"
    NON_SEALED = "non-sealed"

    @staticmethod
    def ordered_modifiers(modifiers: set["Modifier"]) -> list["Modifier"]:
        # Java modifier order: public, protected, private, abstract, static, final,
        # transient, volatile, synchronized, native, strictfp, sealed, non-sealed, default
        order = [
            Modifier.PUBLIC,
            Modifier.PROTECTED,
            Modifier.PRIVATE,
            Modifier.ABSTRACT,
            Modifier.STATIC,
            Modifier.FINAL,
            Modifier.TRANSIENT,
            Modifier.VOLATILE,
            Modifier.SYNCHRONIZED,
            Modifier.NATIVE,
            Modifier.STRICTFP,
            Modifier.SEALED,
            Modifier.NON_SEALED,
            Modifier.DEFAULT,
        ]
        order_map = {mod: i for i, mod in enumerate(order)}
        return sorted(modifiers, key=lambda x: order_map.get(x, 100))

    @staticmethod
    def check_method_modifiers(modifiers):
        # Check for invalid combinations
        if Modifier.ABSTRACT in modifiers and Modifier.FINAL in modifiers:
            raise ValueError("Method cannot be both abstract and final")

        if Modifier.ABSTRACT in modifiers and Modifier.PRIVATE in modifiers:
            raise ValueError("Method cannot be both abstract and private")

        if Modifier.ABSTRACT in modifiers and Modifier.STATIC in modifiers:
            raise ValueError("Method cannot be both abstract and static")

    @staticmethod
    def check_field_modifiers(modifiers):
        # Check for invalid combinations
        if Modifier.FINAL in modifiers and Modifier.VOLATILE in modifiers:
            raise ValueError("Field cannot be both final and volatile")

    @staticmethod
    def check_class_modifiers(modifiers):
        # Check for invalid combinations
        if Modifier.ABSTRACT in modifiers and Modifier.FINAL in modifiers:
            raise ValueError("Class cannot be both abstract and final")

        if Modifier.SEALED in modifiers and Modifier.FINAL in modifiers:
            raise ValueError("Class cannot be both sealed and final")
