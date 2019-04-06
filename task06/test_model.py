#!/usr/bin/env python3

import pytest
import model


def test_scope():
    a, b, c = object(), object(), object()
    parent = model.Scope()
    parent['foo'] = a
    parent['bar'] = b
    scope = model.Scope(parent)

    assert scope['bar'] == b
    assert parent['bar'] == b

    scope['bar'] = c

    assert scope['bar'] == c
    assert parent['bar'] == b
    assert scope['foo'] == a

    child = model.Scope(scope)

    assert child['foo'] == a


def test_scope_not_found():
    s1 = model.Scope()
    s2 = model.Scope(s1)

    with pytest.raises(KeyError) as error:
        s2['water']
    assert error.value.args[0] == 'water'


def test_function_definition():
    func = model.Function(['a'], [])
    op1 = model.FunctionDefinition(
        'useless',
        func
    )
    s = model.Scope()
    op1.evaluate(s)
    func = s['useless']

    assert s['useless'] is func


def test_conditional_if_true():
    s = model.Scope()
    op1 = model.Conditional(
        model.Number(1),
        [model.Number(1)],
        [model.Number(3)]
    )

    assert op1.evaluate(s) == model.Number(1)


def test_conditional_if_false():
    s = model.Scope()
    op2 = model.Conditional(
        model.Number(0),
        [model.Number(3)],
        [model.Number(7)]
    )

    assert op2.evaluate(s) == model.Number(7)


def test_conditional_empty():
    s = model.Scope()
    op1 = model.Conditional(
        model.Number(1),
        [],
        []
    )
    assert not op1.evaluate(s)


def test_conditional_none():
    s = model.Scope()
    op2 = model.Conditional(
        model.Number(0),
        None,
        None
    )
    assert not op2.evaluate(s)


def test_print(capsys):
    s = model.Scope()
    op1 = model.Print(model.Number(666))
    op1.evaluate(s)
    out, err = capsys.readouterr()
    assert not err
    assert out == '666\n'


def test_read(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: '2000')
    s = model.Scope()
    op1 = model.Read('foo')
    op1.evaluate(s)
    assert s['foo'] == model.Number(2000)


def test_function_call():
    s = model.Scope()
    s['useless'] = model.Function(
        ['a', 'b'],
        [model.Reference('a')]
    )
    op1 = model.FunctionCall(
        model.Reference('useless'),
        [model.Number(1), model.Number(2)]
    )

    assert op1.evaluate(s) == model.Number(1)


def test_reference():
    s = model.Scope()
    a = object()
    s['digit'] = a
    op1 = model.Reference('digit')

    assert op1.evaluate(s) == a


def test_binary_op_mul():
    s = model.Scope()
    op1 = model.BinaryOperation(
        model.Number(4),
        '*',
        model.Number(7)
    )

    assert op1.evaluate(s) == model.Number(28)


def test_binary_op_logical_or():
    s = model.Scope()
    op1 = model.BinaryOperation(
        model.Number(0),
        '||',
        model.Number(1)
    )

    assert op1.evaluate(s) == model.Number(1)


def test_binary_op_unknown_op():
    with pytest.raises(RuntimeError) as error:
        op1 = model.BinaryOperation(
            model.Number(0),
            '?',
            model.Number(0)
        )
    assert error.value.args[0] == 'Unknown operation: ?'


def test_unary_op_minus():
    s = model.Scope()
    op1 = model.UnaryOperation(
        '-',
        model.Number(3)
    )

    assert op1.evaluate(s) == model.Number(-3)


def test_unary_op_negation():
    s = model.Scope()
    op1 = model.UnaryOperation(
        '!',
        model.Number(0)
    )

    assert op1.evaluate(s) == model.Number(1)


def test_unary_op_unknown_op():
    with pytest.raises(RuntimeError) as error:
        op1 = model.UnaryOperation(
            '#',
            model.Number(3)
        )
    assert error.value.args[0] == 'Unknown operation: #'


def test_factorial(capsys, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: '7')
    s = model.Scope()
    op1 = model.Read('n')
    op1.evaluate(s)
    op2 = model.FunctionDefinition(
        'fact',
        model.Function(
            ['n'],
            [
                model.Conditional(
                    model.BinaryOperation(
                        model.Reference('n'),
                        '==',
                        model.Number(1)
                    ),
                    [model.Reference('n')],
                    [
                        model.BinaryOperation(
                            model.Reference('n'),
                            '*',
                            model.FunctionCall(
                                model.Reference('fact'),
                                [
                                    model.BinaryOperation(
                                        model.Reference('n'),
                                        '-',
                                        model.Number(1)
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )
    )
    op2.evaluate(s)
    op3 = model.Print(
        model.FunctionCall(model.Reference('fact'), [model.Reference('n')])
    )
    op3.evaluate(s)
    out, err = capsys.readouterr()
    assert not err
    assert out == '5040\n'


if __name__ == "__main__":
    pytest.main()
