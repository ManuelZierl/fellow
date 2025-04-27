import ast
import os

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class GetCodeInput(CommandInput):
    filepath: str = Field(..., description="Path to the Python file to analyze.")
    element: str = Field(
        ...,
        description="Name of the class, function, or method (e.g., 'MyClass', 'my_function', or 'MyClass.my_method').",
    )


def get_code(args: GetCodeInput, context: CommandContext) -> str:
    """
    Extract the source code of a function, class, or class method from a Python file.
    """
    full_path = os.path.abspath(args.filepath)

    if not os.path.isfile(full_path):
        return f"[ERROR] File not found: {args.filepath}"

    if not full_path.endswith(".py"):
        return f"[ERROR] Not a Python file: {args.filepath}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            source = f.read()
            tree = ast.parse(source, filename=args.filepath)
            lines = source.splitlines()

        parts = args.element.split(".")
        if len(parts) == 1:
            # Class or top-level function
            name = parts[0]
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return "\n".join(lines[node.lineno - 1 : node.end_lineno])
                if isinstance(node, ast.ClassDef) and node.name == name:
                    return "\n".join(lines[node.lineno - 1 : node.end_lineno])
            return f"[INFO] Element '{args.element}' not found in {args.filepath}"

        elif len(parts) == 2:
            class_name, method_name = parts
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for child in node.body:
                        if (
                            isinstance(child, ast.FunctionDef)
                            and child.name == method_name
                        ):
                            return "\n".join(lines[child.lineno - 1 : child.end_lineno])
            return f"[INFO] Method '{args.element}' not found in {args.filepath}"

        else:
            return f"[ERROR] Invalid element format: {args.element}. Use 'name' or 'ClassName.method'."

    except SyntaxError as e:
        return f"[ERROR] Could not parse file due to syntax error: {e}"
    except Exception as e:
        return f"[ERROR] Failed to read or parse the file: {e}"
