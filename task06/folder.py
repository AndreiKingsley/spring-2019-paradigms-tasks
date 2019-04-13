#!/usr/bin/env python3

from model import *


class ConstantFolder(ASTNodeVisitor):
    def visit_number(self, number_obj):
        return Number(number_obj.value)

    def visit_function(self, function_obj):
        return Function(
            function_obj.args,
            [statement.accept(self)
             for statement in function_obj.body]
        )

    def visit_function_definition(self, function_definition_obj):
        return FunctionDefinition(
            function_definition_obj.name,
            function_definition_obj.function.accept(self)
        )

    def visit_conditional(self, conditional_obj):
        return Conditional(
            conditional_obj.condition.accept(self),
            [statement.accept(self)
             for statement in conditional_obj.if_true or []],
            [statement.accept(self)
             for statement in conditional_obj.if_false or []]
        )

    def visit_print(self, print_obj):
        return Print(print_obj.expr.accept(self))

    def visit_read(self, read_obj):
        return Read(read_obj.name)

    def visit_function_call(self, function_call_obj):
        return FunctionCall(
            function_call_obj.fun_expr.accept(self),
            [expr.accept(self)
             for expr in function_call_obj.args]
        )

    def visit_reference(self, reference_obj):
        return Reference(reference_obj.name)

    def visit_binary_operation(self, binary_operation_obj):
        lhs = binary_operation_obj.lhs.accept(self)
        rhs = binary_operation_obj.rhs.accept(self)
        op = binary_operation_obj.op
        if isinstance(lhs, Number) and isinstance(rhs, Number):
            return BinaryOperation(lhs, op, rhs).evaluate(Scope())
        if op == '*':
            left_is_zero = isinstance(lhs, Number) and lhs == Number(0)
            right_is_zero = isinstance(rhs, Number) and rhs == Number(0)
            left_is_ref = isinstance(lhs, Reference)
            right_is_ref = isinstance(rhs, Reference)
            if (left_is_zero and right_is_ref) \
                    or (right_is_zero and left_is_ref):
                return Number(0)
        if op == '-':
            left_name = lhs.name if isinstance(lhs, Reference) else None
            right_name = rhs.name if isinstance(rhs, Reference) else None
            if left_name and left_name == right_name:
                return Number(0)
        return BinaryOperation(lhs, op, rhs)

    def visit_unary_operation(self, unary_operation_obj):
        folded_op = UnaryOperation(
            unary_operation_obj.op,
            unary_operation_obj.expr.accept(self)
        )
        if isinstance(unary_operation_obj.expr.accept(self), Number):
            return folded_op.evaluate(Scope())
        return folded_op

    def visit_program(self, program):
        return program.accept(self)


def fold_constants(program):
    folder = ConstantFolder()
    return folder.visit_program(program)
