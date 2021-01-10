from typing import Any

from pattern_matching.pattern_engine import Pattern, PtLiteral, PtCapture, PtFixedSequence, PtClass, PtVariableSequence, PtOr, PtCaptureAs, \
    PtMapping


class _syntax_extension_pep634_Matcher_:
    def __init__(self, value: Any):
        self.__value__ = value
        self.values = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def case(self, pattern: Pattern, names):
        assert isinstance(pattern, Pattern)
        if self.values is not None:
            return False
        var = pattern.match(self.__value__, None)
        if var is not None:
            self.values = [var[n] for n in names]
            return True
        else:
            return False


_syntax_extension_pep634_literal_ = PtLiteral
_syntax_extension_pep634_capture_ = PtCapture
_syntax_extension_pep634_any_ = PtCapture('_')
_syntax_extension_pep634_fixed_sequence_ = PtFixedSequence
_syntax_extension_pep634_variable_sequence_ = PtVariableSequence
_syntax_extension_pep634_class_ = PtClass
_syntax_extension_pep634_or_ = PtOr
_syntax_extension_pep634_as_ = PtCaptureAs
_syntax_extension_pep634_mapping_ = PtMapping

__all__ = ['_syntax_extension_pep634_Matcher_', '_syntax_extension_pep634_literal_', '_syntax_extension_pep634_any_',
           '_syntax_extension_pep634_fixed_sequence_', '_syntax_extension_pep634_variable_sequence_',
           '_syntax_extension_pep634_capture_', '_syntax_extension_pep634_class_', '_syntax_extension_pep634_or_',
           '_syntax_extension_pep634_as_', '_syntax_extension_pep634_mapping_']