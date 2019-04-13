#!/usr/bin/env python3

import pytest
from textwrap import *
from model import *
from printer import *


def test_vist_conditional():
    res = PrettyPrint().visit_program(Conditional(Number(42), [], []))
    expected_result = 'if (42) {\n}'
    assert res == expected_result


def test_vist_function_definition():
    res = PrettyPrint().visit_program(
        FunctionDefinition("foo", Function([], []))
    )
    expected_result = 'def foo() {\n}'
    assert res == expected_result


def test_vist_print():
    res = PrettyPrint().visit_program(Print(Number(42)))
    expected_result = 'print 42;'
    assert res == expected_result


def test_vist_read():
    res = PrettyPrint().visit_program(Read('x'))
    expected_result = 'read x;'
    assert res == expected_result


def test_vist_number():
    res = PrettyPrint().visit_program(Number(10))
    expected_result = '10;'
    assert res == expected_result


def test_vist_reference():
    res = PrettyPrint().visit_program(Reference('x'))
    expected_result = 'x;'
    assert res == expected_result


def test_vist_binary_operation():
    add = BinaryOperation(Number(2), '+', Number(3))
    mul = BinaryOperation(Number(1), '*', add)
    res = PrettyPrint().visit_program(mul)
    expected_result = '((1) * ((2) + (3)));'
    assert res == expected_result


def test_vist_unary_operation():
    res = PrettyPrint().visit_program(UnaryOperation('-', Number(42)))
    expected_result = '(-(42));'
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
            exit((-(arg1)));
        }
    }
    ''')
    out, err = capsys.readouterr()
    assert not err
    assert out == expected_result


if __name__ == '__main__':
    pytest.main()
