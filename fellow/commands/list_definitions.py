import ast
import os
from _ast import AST
from typing import Optional, cast

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class ListDefinitionsInput(CommandInput):
    filepath: str = Field(..., description="Path to the Python file to analyze.")


def format_arg(arg: ast.arg, default: Optional[ast.expr]) -> str:
    annotation = (
        ast.unparse(cast(AST, arg.annotation))
        if isinstance(arg.annotation, ast.AST)
        else ""
    )
    default_str = f" = {ast.unparse(default)}" if isinstance(default, ast.AST) else ""
    return f"{arg.arg}: {annotation}{default_str}".strip(": ")


def format_function(node: ast.FunctionDef) -> str:
    total_args = len(node.args.args)
    defaults_start = total_args - len(node.args.defaults)

    args_with_defaults = []
    for i, arg in enumerate(node.args.args):
        if i >= defaults_start:
            default_index = i - defaults_start
            default = node.args.defaults[default_index]
        else:
            default = None
        args_with_defaults.append(format_arg(arg, default))

    args_str = ", ".join(args_with_defaults)
    returns = (
        f" -> {ast.unparse(cast(AST, node.returns))}"
        if isinstance(node.returns, ast.AST)
        else ""
    )
    signature = f"{node.name}({args_str}){returns}"

    doc = ast.get_docstring(node)
    doc_str = f'    """{doc}"""' if doc else ""

    return f"  - {signature}\n{doc_str}" if doc else f"  - {signature}"


def list_definitions(args: ListDefinitionsInput, context: CommandContext) -> str:
    """
    List all functions and classes in a Python file, including args, types, and docstrings.
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

        top_functions = []
        classes = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                top_functions.append(format_function(node))
            elif isinstance(node, ast.ClassDef):
                class_doc = ast.get_docstring(node)
                doc_str = f'  """{class_doc}"""' if class_doc else ""
                class_header = (
                    f"- {node.name}\n{doc_str}" if doc_str else f"- {node.name}"
                )
                methods = [
                    format_function(child)
                    for child in node.body
                    if isinstance(child, ast.FunctionDef)
                ]
                classes.append(f"{class_header}\n" + "\n".join(methods))

        output_lines = []

        if top_functions:
            output_lines.append(
                f"[INFO] Found {len(top_functions)} top-level function(s):"
            )
            output_lines.extend(top_functions)

        if classes:
            output_lines.append(f"\n[INFO] Found {len(classes)} class(es):")
            output_lines.extend(classes)

        if not output_lines:
            return f"[INFO] No functions or classes found in {args.filepath}"

        return "\n".join(output_lines)

    except SyntaxError as e:
        return f"[ERROR] Could not parse file due to syntax error: {e}"
    except Exception as e:
        return f"[ERROR] Failed to read or parse the file: {e}"
