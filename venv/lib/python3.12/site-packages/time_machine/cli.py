from __future__ import annotations

import argparse
import ast
import sys
import warnings
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from functools import partial

from tokenize_rt import (
    UNIMPORTANT_WS,
    Offset,
    Token,
    reversed_enumerate,
    src_to_tokens,
    tokens_to_src,
)

CODE = "CODE"
DEDENT = "DEDENT"


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the migration tool."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Migrate Python files from freezegun to time-machine",
    )
    migrate_parser.add_argument("file", nargs="+")

    args = parser.parse_args(argv)

    if args.command == "migrate":
        return migrate_files(files=args.file)
    else:  # pragma: no cover
        # Unreachable
        raise NotImplementedError(f"Command {args.command} does not exist.")


def migrate_files(files: list[str]) -> int:
    returncode = 0
    for filename in files:
        returncode |= migrate_file(filename)
    return returncode


def migrate_file(filename: str) -> int:
    if filename == "-":
        contents_bytes = sys.stdin.buffer.read()
    else:
        with open(filename, "rb") as fb:
            contents_bytes = fb.read()

    try:
        contents_text_orig = contents_text = contents_bytes.decode()
    except UnicodeDecodeError:
        print(f"{filename} is non-utf-8 (not supported)")
        return 1

    contents_text = migrate_contents(contents_text)

    if filename == "-":
        print(contents_text, end="")
    elif contents_text != contents_text_orig:
        print(f"Rewriting {filename}", file=sys.stderr)
        with open(filename, "w", encoding="UTF-8", newline="") as f:
            f.write(contents_text)

    return contents_text != contents_text_orig


def migrate_contents(contents_text: str) -> str:
    """Migrate a single text from freezegun to time-machine."""
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text

    callbacks = visit(ast_obj)

    if not callbacks:
        return contents_text

    tokens = src_to_tokens(contents_text)

    fixup_dedent_tokens(tokens)

    for i, token in reversed_enumerate(tokens):
        if not token.src:
            continue
        # though this is a defaultdict, by using `.get()` this function's
        # self time is almost 50% faster
        for callback in callbacks.get(token.offset, ()):
            callback(tokens, i)

    # no types for tokenize-rt
    return tokens_to_src(tokens)  # type: ignore [no-any-return]


def ast_parse(contents_text: str) -> ast.Module:
    # intentionally ignore warnings, we can't do anything about them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ast.parse(contents_text.encode())


def fixup_dedent_tokens(tokens: list[Token]) -> None:  # pragma: no cover
    """For whatever reason the DEDENT / UNIMPORTANT_WS tokens are misordered

    | if True:
    |     if True:
    |         pass
    |     else:
    |^    ^- DEDENT
    |+----UNIMPORTANT_WS
    """
    for i, token in enumerate(tokens):
        if token.name == UNIMPORTANT_WS and tokens[i + 1].name == DEDENT:
            tokens[i], tokens[i + 1] = tokens[i + 1], tokens[i]


TokenFunc = Callable[[list[Token], int], None]


def visit(tree: ast.Module) -> Mapping[Offset, list[TokenFunc]]:
    """
    Visit the AST and return a list of callbacks to apply to the tokens.
    This is a placeholder function; actual implementation would depend on
    the specific migration logic.
    """
    ret = defaultdict(list)
    freezegun_import_seen = False
    freeze_time_import_seen = False
    for node in ast.walk(tree):
        # On Python 3.10+, this would look a lot better with the match statement
        if isinstance(node, ast.Import):
            if (
                len(node.names) == 1
                and (alias := node.names[0]).name == "freezegun"
                and alias.asname is None
            ):
                freezegun_import_seen = True
                ret[ast_start_offset(node)].append(replace_import)
        elif isinstance(node, ast.ImportFrom):
            if (
                node.module == "freezegun"
                and len(node.names) == 1
                and (alias := node.names[0]).name == "freeze_time"
                and alias.asname is None
            ):
                freeze_time_import_seen = True
                ret[ast_start_offset(node)].append(
                    partial(replace_import_from, node=node)
                )
        elif isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and migratable_call(decorator)
                    and (
                        (
                            freezegun_import_seen
                            and isinstance(decorator.func, ast.Attribute)
                            and decorator.func.attr == "freeze_time"
                            and isinstance(decorator.func.value, ast.Name)
                            and decorator.func.value.id == "freezegun"
                        )
                        or (
                            freeze_time_import_seen
                            and isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "freeze_time"
                        )
                    )
                ):
                    ret[ast_start_offset(decorator.func)].append(
                        partial(switch_to_travel, node=decorator.func)
                    )
                    ret[ast_start_offset(decorator)].append(
                        partial(add_tick_false, node=decorator)
                    )

        elif isinstance(node, ast.ClassDef):
            if node.decorator_list and looks_like_unittest_class(node):
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and migratable_call(decorator)
                        and (
                            (
                                freezegun_import_seen
                                and isinstance(decorator.func, ast.Attribute)
                                and decorator.func.attr == "freeze_time"
                                and isinstance(decorator.func.value, ast.Name)
                                and decorator.func.value.id == "freezegun"
                            )
                            or (
                                freeze_time_import_seen
                                and isinstance(decorator.func, ast.Name)
                                and decorator.func.id == "freeze_time"
                            )
                        )
                    ):
                        ret[ast_start_offset(decorator.func)].append(
                            partial(switch_to_travel, node=decorator.func)
                        )
                        ret[ast_start_offset(decorator)].append(
                            partial(add_tick_false, node=decorator)
                        )

        elif isinstance(node, ast.With):
            for item in node.items:
                context_expr = item.context_expr
                if (
                    isinstance(context_expr, ast.Call)
                    and migratable_call(context_expr)
                    and item.optional_vars is None
                    and (
                        (
                            freezegun_import_seen
                            and isinstance(context_expr.func, ast.Attribute)
                            and context_expr.func.attr == "freeze_time"
                            and isinstance(context_expr.func.value, ast.Name)
                            and context_expr.func.value.id == "freezegun"
                        )
                        or (
                            freeze_time_import_seen
                            and isinstance(context_expr.func, ast.Name)
                            and context_expr.func.id == "freeze_time"
                        )
                    )
                ):
                    ret[ast_start_offset(context_expr.func)].append(
                        partial(switch_to_travel, node=context_expr.func)
                    )
                    ret[ast_start_offset(context_expr)].append(
                        partial(add_tick_false, node=context_expr)
                    )

    return ret  # type: ignore [return-value]


def migratable_call(node: ast.Call) -> bool:
    return (
        len(node.args) == 1
        # We could allow tick being set, as long as we didn't then add it
        and len(node.keywords) == 0
    )


def looks_like_unittest_class(node: ast.ClassDef) -> bool:
    """
    Heuristically determine if a class is a unittest.TestCase subclass.
    """
    for base in node.bases:
        if (
            isinstance(base, ast.Name)
            and base.id.endswith("TestCase")
            or (
                isinstance(base, ast.Attribute)
                and isinstance(base.value, ast.Name)
                and base.value.id == "unittest"
                and base.attr.endswith("TestCase")
            )
        ):
            return True

    subnode: ast.AST
    for subnode in node.body:
        if isinstance(subnode, ast.FunctionDef) and subnode.name in (
            "setUp",
            "setUpClass",
            "tearDown",
            "tearDownClass",
            "setUpTestData",
        ):
            return True
        if isinstance(subnode, ast.AsyncFunctionDef) and subnode.name in (
            "asyncSetUp",
            "asyncTearDown",
        ):
            return True

    for subnode in ast.walk(node):
        if (
            isinstance(subnode, ast.Attribute)
            and isinstance(subnode.value, ast.Name)
            and subnode.value.id == "self"
            and subnode.attr in UNITTEST_ASSERT_NAMES
        ):
            return True

    return False


UNITTEST_ASSERT_NAMES = frozenset(
    [
        "assertAlmostEqual",
        "assertCountEqual",
        "assertDictEqual",
        "assertEqual",
        "assertFalse",
        "assertGreater",
        "assertGreaterEqual",
        "assertIn",
        "assertIs",
        "assertIsInstance",
        "assertIsNone",
        "assertIsNot",
        "assertIsNotNone",
        "assertLess",
        "assertLessEqual",
        "assertListEqual",
        "assertLogs",
        "assertMultiLineEqual",
        "assertNoLogs",
        "assertNotAlmostEqual",
        "assertNotEqual",
        "assertNotIn",
        "assertNotIsInstance",
        "assertNotRegex",
        "assertRaises",
        "assertRaisesRegex",
        "assertRegex",
        "assertSequenceEqual",
        "assertSetEqual",
        "assertTrue",
        "assertTupleEqual",
        "assertWarns",
        "assertWarnsRegex",
    ]
)


def ast_start_offset(node: ast.alias | ast.expr | ast.keyword | ast.stmt) -> Offset:
    return Offset(node.lineno, node.col_offset)


def replace_import(tokens: list[Token], i: int) -> None:
    while True:
        if tokens[i].name == "NAME" and tokens[i].src == "freezegun":
            break
        i += 1
    tokens[i] = Token(name="NAME", src="time_machine")


def replace_import_from(tokens: list[Token], i: int, node: ast.ImportFrom) -> None:
    j = find_last_token(tokens, i, node=node)
    tokens[i : j + 1] = [Token(name=CODE, src="import time_machine")]


def switch_to_travel(
    tokens: list[Token], i: int, node: ast.Attribute | ast.Name
) -> None:
    j = find_last_token(tokens, i, node=node)
    tokens[i : j + 1] = [Token(name=CODE, src="time_machine.travel")]


def add_tick_false(tokens: list[Token], i: int, node: ast.Call) -> None:
    """
    Add `tick=False` to the function call.
    """
    j = find_last_token(tokens, i, node=node)
    tokens.insert(j, Token(name=CODE, src=", tick=False"))


# Token functions


def find_last_token(
    tokens: list[Token], i: int, *, node: ast.expr | ast.keyword | ast.stmt
) -> int:
    """
    Find the last token corresponding to the given ast node.
    """
    while (
        tokens[i].line is None or tokens[i].line < node.end_lineno
    ):  # pragma: no cover
        i += 1
    while (
        tokens[i].utf8_byte_offset is None
        or tokens[i].utf8_byte_offset < node.end_col_offset
    ):
        i += 1
    return i - 1
