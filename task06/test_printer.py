#!/usr/bin/env python3

import pytest
from textwrap import *
from model import *
from printer import *


def test_visit_conditional():
    res = PrettyPrint().visit_conditional(Conditional(Number(42), [], []))
    expected_result = 'if (42) {\n}'
    assert res == expected_result


def test_visit_function_definition():
    res = PrettyPrint().visit_function_definition(
        FunctionDefinition('foo', Function([], []))
    )
    expected_result = 'def foo() {\n}'
    assert res == expected_result


def test_visit_print():
    res = PrettyPrint().visit_print(Print(Number(42)))
    expected_result = 'print 42'
    assert res == expected_result


def test_visit_read():
    res = PrettyPrint().visit_read(Read('x'))
    expected_result = 'read x'
    assert res == expected_result


def test_visit_number():
    res = PrettyPrint().visit_number(Number(10))
    expected_result = '10'
    assert res == expected_result


def test_visit_reference():
    res = PrettyPrint().visit_reference(Reference('x'))
    expected_result = 'x'
    assert res == expected_result


def test_visit_binary_operation():
    add = BinaryOperation(Number(2), '+', Number(3))
    mul = BinaryOperation(Number(1), '*', add)
    res = PrettyPrint().visit_binary_operation(mul)
    expected_result = '(1) * ((2) + (3))'
    assert res == expected_result


def test_visit_unary_operation():
    res = PrettyPrint().visit_unary_operation(
        UnaryOperation('-', Number(42))
    )
    expected_result = '-(42)'
    assert res == expected_result


def test_pretty_print(capsys):
    pretty_print(FunctionDefinition('main', Function(['arg1'], [
        Read('x'),
        Print(Reference('x')),
        Conditional(
            BinaryOperation(Number(2), '==', Number(3)),
            [
                Conditional(Number(1), [], [])
            ],
            [
                FunctionCall(Reference('exit'), [
                    UnaryOperation('-', Reference('arg1'))
                ])
            ],
        ),
    ])))
    expected_result = dedent('''\
    def main(arg1) {
        read x;
        print x;
        if ((2) == (3)) {
            if (1) {
            }
        } else {
            exit(-(arg1));
        }
    }\n
    ''')
    out, err = capsys.readouterr()
    assert not err
    assert out == expected_result


if __name__ == '__main__':
    pytest.main()
