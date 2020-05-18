import sys

def _repr(obj):
    """
    Get the representation of an object, with dedicated pprint-like format for lists.
    """
    if isinstance(obj, list):
        return '[' + (',\n '.join((_repr(e).replace('\n', '\n ') for e in obj))) + '\n]'
    else:
        return repr(obj) 
    
class Node(object):
    """ Abstract base class for AST nodes.
    """
    __slots__ = ()

    def __repr__(self):
        """ Generates a python representation of the current node
        """
        result = self.__class__.__name__ + '('
        indent = ''
        separator = ''
        for name in self.__slots__[:-1]:
            result += separator
            result += indent
            result += name + '=' + (_repr(getattr(self, name)).replace('\n', '\n  ' + (' ' * (len(name) + len(self.__class__.__name__)))))
            separator = ','
            indent = ' ' * len(self.__class__.__name__)
        result += indent + ')'
        return result


    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass


    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and children (recursively) to a buffer.
            buf:
                Open IO buffer into which the Node is printed.
            offset:
                Initial offset (amount of leading spaces)
            attrnames:
                True if you want to see the attribute names in name=value pairs. False to only see the values.
            nodenames:
                True if you want to see the actual node names within their parents.
            showcoord:
                Do you want the coordinates of each Node to be displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__+ ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__+ ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self, n)) for n in self.attr_names if getattr(self, n) is not None]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            if self.coord:
                buf.write('%s' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)

class Coord(object):
    """ Coordinates of a syntactic element. Consists of:
            - Line number
            - (optional) column number, for the Lexer
    """
    __slots__ = ('line', 'column')

    def __init__(self, line, column=None):
        self.line = line
        self.column = column

    def __str__(self):
        """ Converte linha em uma padrão de saída string
        """
        if self.line:
            coord_str = "   @ %s:%s" % (self.line, self.column)
        else:
            coord_str = ""
        return coord_str

class PtrDecl(Node):
    __slots__ = ('type', 'coord')
    def __init__(self, type, coord=None):
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type

    attr_names = ()

class BinaryOp(Node):
    __slots__ = ('op', 'left', 'right', 'coord', 'type')
    def __init__(self, op, left, right, coord=None, type=None):
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord
        self.type = type

    def children(self):
        nodelist = []
        if self.left is not None: nodelist.append(("left", self.left))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    def __iter__(self):
        if self.left is not None:
            yield self.left
        if self.right is not None:
            yield self.right

    attr_names = ('op', )

class ParamList(Node):
    __slots__ = ('params', 'coord')
    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.params or []):
            yield child

    attr_names = ()

class Cast(Node):
    __slots__ = ('to_type', 'expr', 'coord', 'type')
    def __init__(self, to_type, expr, coord=None, type=None):
        self.to_type = to_type
        self.expr = expr
        self.coord = coord
        self.type = type

    def children(self):
        nodelist = []
        if self.to_type is not None: nodelist.append(("to_type", self.to_type))
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    def __iter__(self):
        if self.to_type is not None:
            yield self.to_type
        if self.expr is not None:
            yield self.expr

    attr_names = ()

class Assignment(Node):
    __slots__ = ('op', 'lvalue', 'rvalue', 'coord')
    def __init__(self, op, lvalue, rvalue, coord=None):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.coord = coord

    def children(self):
        nodelist = []
        if self.lvalue is not None: nodelist.append(("lvalue", self.lvalue))
        if self.rvalue is not None: nodelist.append(("rvalue", self.rvalue))
        return tuple(nodelist)

    def __iter__(self):
        if self.lvalue is not None:
            yield self.lvalue
        if self.rvalue is not None:
            yield self.rvalue

    attr_names = ('op', )

class ExprList(Node):
    __slots__ = ('exprs', 'coord')
    def __init__(self, exprs, coord=None):
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[{}]".format(i), child))
        return tuple(nodelist)

    def __iter__(self):
       for child in (self.exprs or []):
           yield child

    attr_names = ()

class Constant(Node):
    __slots__ = ('type', 'value', 'coord')
    def __init__(self, type, value, coord=None):
        self.type = type
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('type', 'value', )

class Compound(Node):
    __slots__ = ('block_items', 'coord')
    def __init__(self, block_items, coord=None):
        self.block_items = block_items
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.block_items or []):
            nodelist.append(("block_items[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.block_items or []):
            yield child

    attr_names = ()

class While(Node):
    __slots__ = ('cond', 'stmt', 'coord')
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    def __iter__(self):
        if self.cond is not None:
            yield self.cond
        if self.stmt is not None:
            yield self.stmt

    attr_names = ()

class For(Node):
    __slots__ = ('init', 'cond', 'next', 'stmt', 'coord')
    def __init__(self, init, cond, next, stmt, coord=None):
        self.init = init
        self.cond = cond
        self.next = next
        self.stmt = stmt
        self.coord = coord

    def children(self):
        nodelist = []
        if self.init is not None: nodelist.append(("init", self.init))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.next is not None: nodelist.append(("next", self.next))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    def __iter__(self):
        if self.init is not None:
            yield self.init
        if self.cond is not None:
            yield self.cond
        if self.next is not None:
            yield self.next
        if self.stmt is not None:
            yield self.stmt

    attr_names = ()

class Return(Node):
    __slots__ = ('expr', 'coord')
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    def __iter__(self):
        if self.expr is not None:
            yield self.expr

    attr_names = ()

class Break(Node):
    __slots__ = ('coord')
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ()

class EmptyStatement(Node):
    __slots__ = ('coord')
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ()

class UnaryOp(Node):
    __slots__ = ('op', 'expr', 'coord', 'type')
    def __init__(self, op, expr, coord=None, type=None):
        self.op = op
        self.expr = expr
        self.coord = coord
        self.type = type

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    def __iter__(self):
        if self.expr is not None:
            yield self.expr

    attr_names = ('op', )

class ArrayRef(Node):
    __slots__ = ('name', 'subscript', 'coord', 'type')
    def __init__(self, name, subscript, coord=None, type=None):
        self.name = name
        self.subscript = subscript
        self.coord = coord
        self.type =type

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.subscript is not None: nodelist.append(("subscript", self.subscript))
        return tuple(nodelist)

    def __iter__(self):
        if self.name is not None:
            yield self.name
        if self.subscript is not None:
            yield self.subscript

    attr_names = ()

class Program(Node):
    __slots__ = ('gdecls', 'coord')

    def __init__(self, gdecls, coord=None):
        self.gdecls = gdecls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.gdecls or []):
            nodelist.append(("gdecls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Type(Node):
    __slots__ = ('names', 'coord')

    def __init__(self, names, coord=None):
        self.names = names
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('names', )

class Assert(Node):
    __slots__ = ('expr', 'coord')

    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("assert", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Print(Node):
    __slots__ = ('expr', 'coord')

    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("print", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Read(Node):
    __slots__ = ('expr', 'coord')

    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("read", self.expr))
        return tuple(nodelist)

    attr_names = ()

class If(Node):
    __slots__ = ('cond', 'iftrue', 'iffalse', 'coord')

    def __init__(self, cond, iftrue, iffalse, coord=None):
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.iftrue is not None: nodelist.append(("iftrue", self.iftrue))
        if self.iffalse is not None: nodelist.append(("iffalse", self.iffalse))
        return tuple(nodelist)

    attr_names = ()

class FuncDef(Node):
    __slots__ = ('spec', 'decl', 'param_decls', 'body', 'coord')
    def __init__(self, spec, decl, param_decls, body, coord=None):
        self.spec = spec
        self.decl = decl
        self.param_decls = param_decls
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.spec is not None: nodelist.append(("decl", self.spec))
        if self.decl is not None: nodelist.append(("decl", self.decl))
        if self.body is not None: nodelist.append(("body", self.body))
        for i, child in enumerate(self.param_decls or []):
            nodelist.append(("param_decls[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        if self.spec is not None:
            yield self.spec
        if self.decl is not None:
            yield self.decl
        if self.body is not None:
            yield self.body
        for child in (self.param_decls or []):
            yield child

    attr_names = ()

class ID(Node):
    __slots__ = ('name', 'coord', 'type', 'value')
    def __init__(self, name, coord=None, type=None, value=None):
        self.name = name
        self.coord = coord
        self.type = type
        self.value = value

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('name', )

class InitList(Node):
    __slots__ = ('exprs', 'coord', 'type', 'values', 'dimaux')
    def __init__(self, exprs, coord=None, type=None, values=None, dimaux=[None]):
        self.exprs = exprs
        self.coord = coord
        self.type = type
        self.values = values
        self.dimaux = dimaux

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[{}]".format(i), child))
        return tuple(nodelist)

    attr_names = ()

class FuncCall(Node):
    __slots__ = ('name', 'args', 'coord', 'type')
    def __init__(self, name, args, coord=None, type=None):
        self.name = name
        self.args = args
        self.coord = coord
        self.type = type

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.args is not None: nodelist.append(("args", self.args))
        return tuple(nodelist)

    def __iter__(self):
        if self.name is not None:
            yield self.name
        if self.args is not None:
            yield self.args

    attr_names = ()

class Decl(Node):
    __slots__ = ('name', 'type', 'init','coord')
    def __init__(self, name, type, init, coord=None):
        self.name = name
        self.type = type
        self.init = init
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.init is not None: nodelist.append(("init", self.init))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type
        if self.init is not None:
            yield self.init

    attr_names = ('name',)

class VarDecl(Node):
    __slots__ = ('declname', 'type', 'coord', 'value', 'valuetmp')
    def __init__(self, declname, type, coord=None, value=None, valuetmp=None):
        self.declname = declname
        self.type = type
        self.coord = coord
        self.value = value
        self.valuetmp = valuetmp

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ()

class ArrayDecl(Node):
    __slots__ = ('type', 'dim', 'coord', 'typeaux', 'auxdim', 'values', 'name', 'aux')
    def __init__(self, type, dim, coord=None, value=None, auxdim=None, values=None, typeaux=None, name=None, aux=None):
        self.type = type
        self.dim = dim
        self.coord = coord
        self.typeaux = typeaux
        self.auxdim = auxdim
        self.values = values
        self.name = name
        self.aux = aux

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.dim is not None: nodelist.append(("dim", self.dim))
        return tuple(nodelist)

    attr_names = ()

class FuncDecl(Node):
    __slots__ = ('args', 'type', 'coord')
    def __init__(self, args, type, coord=None):
        self.args = args
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.args is not None: nodelist.append(("args", self.args))
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ()

class GlobalDecl(Node):
    __slots__ = ('decls', 'coord')
    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i,decl in enumerate(self.decls if self.decls is not None else []):
            if self.decls is not None:
                nodelist.append(("decls[%d]" % i, decl))
        return tuple(nodelist)

    def __iter__(self):
        if self.decls is not None:
            yield self.decls

    attr_names = ()

class DeclList(Node):
    __slots__ = ('decls', 'coord')
    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.decls or []):
            yield child

    attr_names = ()