try:
    import unittest2 as unittest
except ImportError:
    import unittest
import ast
import sys
from astmonkey import visitors, transformers


class GraphNodeVisitorTest(unittest.TestCase):

    def setUp(self):
        self.visitor = visitors.GraphNodeVisitor()

    def test_has_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        self.assertTrue(self.visitor.graph.get_edge(str(node), str(node.body[0])))

    def test_does_not_have_edge(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        self.assertFalse(self.visitor.graph.get_edge(str(node), str(node.body[0].value)))

    def test_node_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        dot_node = self.visitor.graph.get_node(str(node.body[0].value))[0]
        self.assertEqual(dot_node.get_label(), 'ast.Num(n=1)')

    def test_edge_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1'))

        self.visitor.visit(node)

        dot_edge = self.visitor.graph.get_edge(str(node), str(node.body[0]))[0]
        self.assertEqual(dot_edge.get_label(), 'body[0]')

    def test_multi_parents_node_label(self):
        node = transformers.ParentNodeTransformer().visit(ast.parse('x = 1\nx = 2'))

        self.visitor.visit(node)

        dot_node = self.visitor.graph.get_node(str(node.body[0].targets[0]))[0]
        self.assertEqual(dot_node.get_label(), "ast.Name(id='x', ctx=ast.Store())")


class SourceGeneratorNodeVisitorTest(unittest.TestCase):

    def assert_code_equal(self, code):
        node = ast.parse(code)
        generated = visitors.to_source(node, indent_with='\t')
        self.assertEqual(code, generated)

    def test_import(self):
        self.assert_code_equal('import x')

    def test_import_from(self):
        self.assert_code_equal('from x import y as z, q as p')

    def test_import_from_relative_level_1(self):
        self.assert_code_equal("from . import x")

    def test_import_from_relative_level_1_with_source_name(self):
        self.assert_code_equal("from .y import x")

    def test_import_from_relative_level_2(self):
        self.assert_code_equal("from .. import x")

    def test_assign(self):
        self.assert_code_equal('x = 1')

    def test_assign_with_unpack(self):
        self.assert_code_equal('(x, y) = z')

    def test_aug_assign(self):
        self.assert_code_equal('x += 1')

    def test_function_def(self):
        self.assert_code_equal('def foo(x, y=1, *args, **kwargs):\n\tpass')

    def test_decorator(self):
        self.assert_code_equal('@x(y)\ndef foo():\n\tpass')

    def test_class_def(self):
        self.assert_code_equal('class X(A, B):\n\tpass')

    @unittest.skipIf(sys.version_info < (3, 0), 'not supported Python version')
    def test_class_def_with_metaclass(self):
        self.assert_code_equal('class X(metaclass=A, *x, **y):\n\tpass')

    def test_if(self):
        self.assert_code_equal('if x:\n\tpass\nelif y:\n\tpass\nelse:\n\tpass')

    def test_for(self):
        self.assert_code_equal('for x in y:\n\tpass\nelse:\n\tpass')

    def test_while(self):
        self.assert_code_equal('while x:\n\tpass\nelse:\n\tpass')

    @unittest.skipIf(sys.version_info >= (3, 0), 'not supported Python version')
    def test_print(self):
        self.assert_code_equal('print >> y, x,')

    def test_delete(self):
        self.assert_code_equal('del x, y')

    def test_global(self):
        self.assert_code_equal('global x, y')

    def test_return(self):
        self.assert_code_equal('def foo(x):\n\treturn x')

    def test_break(self):
        self.assert_code_equal('while x:\n\tbreak')

    def test_continue(self):
        self.assert_code_equal('while x:\n\tcontinue')

    def test_raise(self):
        self.assert_code_equal('raise x')

    @unittest.skipIf(sys.version_info >= (3, 0), 'not supported Python version')
    def test_raise_with_msg_and_tb(self):
        self.assert_code_equal('raise x, y, z')

    @unittest.skipIf(sys.version_info < (3, 0), 'not supported Python version')
    def test_raise_from(self):
        self.assert_code_equal('raise x from y')

    def test_attribute(self):
        self.assert_code_equal('x.y')

    def test_call(self):
        self.assert_code_equal('x(y, z=1, *args, **kwargs)')

    def test_str(self):
        self.assert_code_equal("'x'")

    def test_num(self):
        self.assert_code_equal('1')

    def test_tuple(self):
        self.assert_code_equal('(1, 2)')

    def test_list(self):
        self.assert_code_equal('[1, 2]')

    @unittest.skipIf(sys.version_info < (2, 7), 'not supported Python version')
    def test_set(self):
        self.assert_code_equal('{1, 2}')

    def test_dict(self):
        self.assert_code_equal('{1: 2, 3: 4}')

    def test_bin_op(self):
        self.assert_code_equal('x + y')

    def test_bool_op(self):
        self.assert_code_equal('(x and y)')

    def test_compare(self):
        self.assert_code_equal('x < y')

    def test_unary_op(self):
        self.assert_code_equal('(not x)')

    def test_subscript(self):
        self.assert_code_equal('x[y]')

    def test_slice(self):
        self.assert_code_equal('x[y:z:q]')

    def test_extended_slice(self):
        self.assert_code_equal('x[1:2, 3:4]')

    def test_yield(self):
        self.assert_code_equal('def foo(x):\n\tyield x')

    def test_lambda(self):
        self.assert_code_equal('lambda x: x')

    def test_list_comp(self):
        self.assert_code_equal('[x for x in y if x]')

    def test_generator_exp(self):
        self.assert_code_equal('(x for x in y if x)')

    @unittest.skipIf(sys.version_info < (2, 7), 'not supported Python version')
    def test_set_comp(self):
        self.assert_code_equal('{x for x in y if x}')

    @unittest.skipIf(sys.version_info < (2, 7), 'not supported Python version')
    def test_dict_comp(self):
        self.assert_code_equal('{x: y for x in y if x}')

    def test_if_exp(self):
        self.assert_code_equal('x if y else z')

    def test_try_except(self):
        self.assert_code_equal('try:\n\tpass\nexcept X as x:\n\tpass')

    def test_try_finally(self):
        self.assert_code_equal('try:\n\tpass\nfinally:\n\tpass')

    def test_with(self):
        self.assert_code_equal('with x as y:\n\tpass')

    @unittest.skipIf(sys.version_info < (3, 3), 'not supported Python version')
    def test_yield_from(self):
        self.assert_code_equal('def foo():\n\tyield from x')

    @unittest.skipIf(sys.version_info >= (3, 0), 'not supported Python version')
    def test_repr(self):
        self.assert_code_equal('`x`')

    def test_empty_lines(self):
        self.assert_code_equal('\n\n\nx')

    @unittest.skipIf(sys.version_info < (3, 0), 'not supported Python version')
    def test_nonlocal(self):
        self.assert_code_equal('def foo(x, y):\n\tdef bar():\n\t\tnonlocal x, y')

    @unittest.skipIf(sys.version_info < (3, 0), 'not supported Python version')
    def test_bytes(self):
        self.assert_code_equal("b'x'")

    def test_ellipsis(self):
        self.assert_code_equal('x[...]')

    @unittest.skipIf(sys.version_info < (3, 0), 'not supported Python version')
    def test_starred(self):
        self.assert_code_equal('*x = y')

    def test_alias(self):
        self.assert_code_equal('import x as y')

    def test_assert_with_message(self):
        self.assert_code_equal("assert True, 'message'")

    def test_assert_without_message(self):
        self.assert_code_equal("assert True")

