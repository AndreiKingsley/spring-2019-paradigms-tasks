#!/usr/bin/env python3

from model import *

DEFAULT_INDENT = 4


class PrettyPrint(ASTNodeVisitor):
    def __init__(self):
        self.indent_size = 0

    def get_indent(self):
        return '' + self.indent_size * ' '

    @staticmethod
    def make_end_of_statement(res):
        if not res.endswith('}'):
            res += ';'
        res += '\n'
        return res

    @staticmethod
    def check_in_brackets(expr):
        if not (expr.startswith('(')
                and expr.endswith(')')):
            expr = '(' + expr + ')'
        return expr

    def make_new_level_of_statements(self, res, statements):
        self.indent_size += DEFAULT_INDENT
        for statement in statements or []:
            res += self.get_indent() + statement.accept(self)
            res = self.make_end_of_statement(res)
        self.indent_size -= DEFAULT_INDENT
        return res

    def visit_number(self, number_obj):
        return str(number_obj.value)

    def visit_function(self, function_obj):
        raise TypeError(
            "Can\'t call \'PrettyPrint\' for \'model.Function\' object")

    def visit_function_definition(self, function_definition_obj):
        res = 'def ' + function_definition_obj.name
        cur_func = function_definition_obj.function
        res += '('
        if cur_func.args:
            res += ', '.join(cur_func.args)
        res += ')'
        res += ' {\n'
        res = self.make_new_level_of_statements(res, cur_func.body)
        res += self.get_indent() + '}'
        return res

    def visit_conditional(self, conditional_obj):
        condition = self.check_in_brackets(
            conditional_obj.condition.accept(self))
        res = 'if ' + condition + ' {\n'
        res = self.make_new_level_of_statements(res, conditional_obj.if_true)
        if conditional_obj.if_false:
            res += self.get_indent() + '} else {\n'
            res = self.make_new_level_of_statements(
                res,
                conditional_obj.if_false
            )
        res += self.get_indent() + '}'
        return res

    def visit_print(self, print_obj):
        return 'print ' + print_obj.expr.accept(self)

    def visit_read(self, read_obj):
        return 'read ' + read_obj.name

    def visit_function_call(self, function_call_obj):
        res = function_call_obj.fun_expr.accept(self)
        res += '('
        if function_call_obj.args:
            res += ', '.join(
                arg.accept(self) for arg in function_call_obj.args
            )
        res += ')'
        return res

    def visit_reference(self, reference_obj):
        return reference_obj.name

    def visit_binary_operation(self, binary_operation_obj):
        lhs = self.check_in_brackets(binary_operation_obj.lhs.accept(self))
        rhs = self.check_in_brackets(binary_operation_obj.rhs.accept(self))
        return '(' + lhs + ' ' + binary_operation_obj.op + ' ' + rhs + ')'

    def visit_unary_operation(self, unary_operation_obj):
        expr = self.check_in_brackets(unary_operation_obj.expr.accept(self))
        return '(' + unary_operation_obj.op + expr + ')'

    def visit_program(self, program):
        res = program.accept(self)
        if not res.endswith('}'):
            res += ';'
        return res


def pretty_print(program):
    printer = PrettyPrint()
    print(printer.visit_program(program))
