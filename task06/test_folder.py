#!/usr/bin/env python3

from folder import *
from printer import *


def test_binop_num_num():
    op = BinaryOperation(Number(3), '*', Number(6))
    assert fold_constants(op) == Number(18)


def test_unop_num():
    op = UnaryOperation('!', Number(6))
    assert fold_constants(op) == Number(0)


def test_multiplication_zero_left():
    op = BinaryOperation(Number(0), '*', Number(6))
    assert fold_constants(op) == Number(0)


def test_multiplication_zero_right():
    op = BinaryOperation(Reference('x'), '*', Number(0))
    assert fold_constants(op) == Number(0)


def test_difference_same():
    op = BinaryOperation(Reference('x'), '-', Reference('x'))
    assert fold_constants(op) == Number(0)


def test_fold_constants_with_pretty_printer(capsys):
    pretty_print(fold_constants(
        BinaryOperation(
            Number(10),
            '-',
            UnaryOperation(
                '-',
                BinaryOperation(
                    Number(3),
                    '+',
                    BinaryOperation(
                        Reference('x'),
                        '-',
                        Reference('x')
                    )
                )
            )
        )
    ))
    expected_result = '13;\n'
    out, err = capsys.readouterr()
    assert not err
    assert out == expected_result


if __name__ == "__main__":
    pytest.main()
