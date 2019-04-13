#!/usr/bin/env python3

from model import *

DEFAULT_INDENT = 4


class PrettyPrint(ASTNodeVisitor):
    def __init__(self):
        self.indent_size = 0

    def get_indent(self):
        res = ''
        return res + self.indent_size * ' '

    def make_end_of_statement(self, res):
        if not res.endswith('}'):
            res += ';'
        res += '\n'
        return res

    def check_in_brackets(self, expr):
        if not (expr.startswith('(')
                and expr.endswith(')')):
            expr = '(' + expr + ')'
        return expr

    def visit_number(self, number_obj):
        return str(number_obj.value)

    def visit_function(self, function_obj):
        raise TypeError(
            'Can\'t call \'PrettyPrint\' for \'model.Function\' object')

    def visit_function_definition(self, function_definition_obj):
        res = 'def ' + function_definition_obj.name
        self.indent_size += DEFAULT_INDENT
        cur_func = function_definition_obj.function
        res += '('
        if cur_func.args:
            res += cur_func.args[0]
            for arg in cur_func.args[1:]:
                res += ', ' + arg
        res += ')'
        res += ' {\n'
        for statement in cur_func.body:
            res += self.get_indent() + statement.accept(self)
            res = self.make_end_of_statement(res)
        self.indent_size -= DEFAULT_INDENT
        res += self.get_indent() + '}'
        return res

    def visit_conditional(self, conditional_obj):
        condition = self.check_in_brackets(
            conditional_obj.condition.accept(self))
        res = 'if ' + condition + ' {\n'
        self.indent_size += DEFAULT_INDENT
        for statement in conditional_obj.if_true or []:
            res += self.get_indent() + statement.accept(self)
            res = self.make_end_of_statement(res)
        self.indent_size -= DEFAULT_INDENT
        if conditional_obj.if_false:
            res += self.get_indent() + '} else {\n'
            self.indent_size += DEFAULT_INDENT
            for statement in conditional_obj.if_false or []:
                res += self.get_indent() + statement.accept(self)
                res = self.make_end_of_statement(res)
            self.indent_size -= DEFAULT_INDENT
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
            res += function_call_obj.args[0].accept(self)
            for arg in function_call_obj.args[1:]:
                res += ', ' + arg.accept(self)
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
