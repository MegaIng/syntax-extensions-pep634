__package__ = "syntax-extensions-pep634"
__author__ = "MegaIng"
__version__ = "0.1.0"
__extra_info__ = {}

from itertools import takewhile

from lark import Transformer, Tree, v_args, Token
from lark.visitors import Transformer_InPlace
from syntax_extensions.base.python_parsing import PythonCodeTemplate, tup, string
from syntax_extensions.extensions.pep634.runtime import __all__ as all_names

GRAMMAR = """

%extend compound_stmt: match_stmt

match_stmt: "match" test ":" cases

cases: _NEWLINE _INDENT case+ _DEDENT

case: "case" pat ["if" test] ":" suite

?pat: seq_item "," _sequence -> sequence
    | as_pattern
?as_pattern: or_pattern ("as" NAME)?
?or_pattern: closed_pattern ("|" closed_pattern)*
?closed_pattern: literal
               | NAME -> capture
               | "_" -> any
               | attr
               | "(" as_pattern ")"
               | "[" _sequence "]" -> sequence
               | "(" (seq_item "," _sequence)? ")" -> sequence
               | "{" (mapping_item ("," mapping_item)* ","?)?"}" -> mapping
               | "{" (mapping_item ("," mapping_item)* ",")? "**" NAME ","? "}" -> mapping_star
               | class_pattern

literal: inner_literal

?inner_literal: "None" -> const_none
              | "True" -> const_true
              | "False" -> const_false
              | STRING -> string
              | number

attr: NAME ("." NAME)+ -> value

name_or_attr: NAME ("." NAME)* -> value

mapping_item: (literal|attr) ":" as_pattern

_sequence: (seq_item ("," seq_item)* ","?)?
?seq_item: as_pattern
         | "*" NAME -> star_pattern

class_pattern: name_or_attr "(" [arguments ","?] ")"
arguments: pos ["," keyws] | keyws -> no_pos

pos: as_pattern ("," as_pattern)*
keyws: keyw ("," keyw)*
keyw: NAME "=" as_pattern

"""
USED_NAMES = ('compound_stmt', 'test', 'suite', 'STRING', 'number', 'NAME', '_DEDENT', '_INDENT', '_NEWLINE')

TEMPLATE_MATCH = PythonCodeTemplate("""
if True:
    from syntax_extensions.extensions.pep634.runtime import %s
    with _syntax_extension_pep634_Matcher_($atom:value$) as $atom:matcher_name$:
        $suite:cases*$
""".strip() % ', '.join(all_names))

TEMPLATE_CASE = PythonCodeTemplate("""\
if $atom:matcher_name$.case($atom:pattern$, $atom:names_strings$):
    $atom:names_vars$ = $atom:matcher_name$.values
    if $atom:test_expr$:
        $suite:action_stmts*$
    else:
        $atom:matcher_name$.values = None
""")

TEMPLATE_LITERAL = PythonCodeTemplate("""
_syntax_extension_pep634_literal_($atom:value$)
""".strip(), start='expr')

TEMPLATE_CAPTURE = PythonCodeTemplate("""
_syntax_extension_pep634_capture_($atom:name$)
""".strip(), start='expr')

TEMPLATE_ANY = PythonCodeTemplate("""
_syntax_extension_pep634_any_
""".strip(), start='expr')

TEMPLATE_FIXED_SEQUENCE = PythonCodeTemplate("""
_syntax_extension_pep634_fixed_sequence_($atom:values$)
""".strip(), start='expr')

TEMPLATE_VARIABLE_SEQUENCE = PythonCodeTemplate("""
_syntax_extension_pep634_variable_sequence_($atom:pre$, $atom:name$, $atom:post$)
""".strip(), start='expr')

TEMPLATE_CLASS = PythonCodeTemplate("""
_syntax_extension_pep634_class_($atom:cls$, $atom:pos$, $atom:kw$)
""".strip(), start='expr')

TEMPLATE_OR = PythonCodeTemplate("""
_syntax_extension_pep634_or_($atom:options$)
""".strip(), start='expr')

TEMPLATE_AS = PythonCodeTemplate("""
_syntax_extension_pep634_as_($atom:pat$, $atom:name$)
""".strip(), start='expr')

PATTERN_MAPPING = PythonCodeTemplate("""
_syntax_extension_pep634_mapping_($atom:elms$)
""".strip(), start='expr')


class Match2Python(Transformer_InPlace):
    def __init__(self, name):
        self.name = Tree('var', [Token('NAME', name)])

    def __default__(self, data, children, meta):
        if data.startswith('pep634__') and data != 'pep634__cases':
            raise NotImplementedError((data, children, meta))
        else:
            return super(Match2Python, self).__default__(data, children, meta)

    def pep634__match_stmt(self, children):
        expr, cases = children
        return TEMPLATE_MATCH.format(value=expr, matcher_name=self.name, cases=cases.children)

    def pep634__case(self, children):
        if len(children) == 3:
            (names, pattern), test, suite = children
        else:
            (names, pattern), suite = children
            test = Tree('const_true', [])
        names_vars = tup(*(Tree('var', [Token('NAME', n)]) for n in names))
        names_strings = tup(*(string(repr(n)) for n in names))
        return TEMPLATE_CASE.format(matcher_name=self.name, pattern=pattern, names_vars=names_vars, names_strings=names_strings,
                                    test_expr=test, action_stmts=suite.children)

    def pep634__literal(self, children):
        return set(), TEMPLATE_LITERAL.format(value=children[0])

    def pep634__any(self, children):
        return set(), TEMPLATE_ANY.format()

    def pep634__value(self, children):
        value = Tree('var', [children[0]])
        for n in children[1:]:
            value = Tree('getattr', [value, Token('NAME', n)])
        return set(), TEMPLATE_LITERAL.format(value=value)

    def pep634__capture(self, children):
        return {children[0].value}, TEMPLATE_CAPTURE.format(name=string(repr(children[0].value)))

    def pep634__star_pattern(self, children):
        return set(), children[0].value

    def pep634__sequence(self, children):
        if not children:
            return set(), TEMPLATE_FIXED_SEQUENCE.format(values=tup())
        names, pats = zip(*children)
        names = set.union(*names)
        if any(isinstance(p, str) for p in pats):
            pre = tuple(takewhile(lambda c: not isinstance(c, str), pats))
            star = pats[len(pre)]
            post = pats[len(pre) + 1:]
            assert not any(isinstance(c, str) for c in post)
            return names | {star}, TEMPLATE_VARIABLE_SEQUENCE.format(pre=tup(*pre), name=string(repr(star)), post=tup(*post))
        else:
            return names, TEMPLATE_FIXED_SEQUENCE.format(values=tup(*pats))

    def pep634__pos(self, children):
        names, pats = zip(*children)
        names = set.union(*names)
        return names, tup(*pats)

    def pep634__keyw(self, children):
        return children[1][0], tup(string(repr(children[0].value)), children[1][1])

    def pep634__keyws(self, children):
        names, pats = zip(*children)
        names = set.union(*names)
        return names, tup(*pats)

    def pep634__arguments(self, ch):
        if len(ch) == 2:
            pos, kw = ch
        else:
            pos, kw = *ch, None
        pos_names, pos = pos or (set(), tup())
        kw_names, kw = kw or (set(), tup())
        return pos_names | kw_names, (pos, kw)

    def pep634__no_pos(self, ch):
        kw, = ch
        kw_names, kw = kw or (set(), tup())
        return kw_names, (tup(), kw)

    def pep634__class_pattern(self, children):
        if len(children) == 2:
            (names, cls), (args_names, (pos, kw)) = children
            names.update(args_names)
        else:
            (names, cls), = children
            pos, kw = tup(), tup()
        return names, TEMPLATE_CLASS.format(cls=cls, pos=pos, kw=kw)
    
    def pep634__or_pattern(self, children):
        names, pats = zip(*children)
        names = set.union(*names)
        return names, TEMPLATE_OR.format(options=tup(*pats))
    
    def pep634__as_pattern(self, children):
        (names, pat), name = children
        return names | {name.value}, TEMPLATE_AS.format(pat=pat, name=string(repr(name.value)))
    
    def pep634__string(self, children):
        return Tree('string', children)
    
    def pep634__mapping_item(self, children):
        (names_key, key), (names_value, value) = children
        assert len(names_key) == 0
        return names_value, tup(key, value)
    
    def pep634__mapping(self, children):
        names, pats = zip(*children)
        names = set.union(*names)
        return names, PATTERN_MAPPING.format(elms=tup(*pats))


class PEP634TopLevelTransformer(Transformer_InPlace):
    def __init__(self):
        self.counter = 0

    @v_args(tree=True)
    def pep634__match_stmt(self, tree):
        name = f"_syntax_extension_pep634_match{self.counter}"
        m2p = Match2Python(name)
        return m2p.transform(tree)


def get_extension_impl():
    return GRAMMAR, USED_NAMES, PEP634TopLevelTransformer()
