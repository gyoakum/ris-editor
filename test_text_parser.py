import unittest
from unittest.mock import Mock

from text_parser import parse_helpfile
from errors import ParseError


def provide_file(func, name=None):
    """Inject the test source file with the same name into the test"""
    test_name = name if name else func.__name__[5:]
    filename = 'tests/unit/{}.txt'.format(test_name)
    def wrapped_func(instance):
        with open(filename) as f:
            func(instance, f)
    return wrapped_func


class TestTextParser(unittest.TestCase):

    def _parse_fails(self, src, **kwargs):
        """Verifies that the parse attempt fails with the given parameters"""
        with self.assertRaises(ParseError) as cm:
            parse_helpfile(src)
        err = cm.exception
        for key, val in kwargs.items():
            self.assertEqual(getattr(err, key), val)

    #----------- Line parsing -------------------

    # TEST invalid id line

    # TEST invalid % lines caught

    # TEST permissive flag allows % flexibility

    # TEST invalid . lines
    @provide_file
    def test_invalid_color_line(self, src):
        """Check that invalid color specifiers trigger errors"""
        self._parse_fails(src, line_number=6)

    @provide_file
    def test_color_out_of_bounds(self, src):
        """Check that color specifiers greater than 255 fail parsing"""
        self._parse_fails(src, line_number=6)

    # TEST char swap on Longest Line lines with ';' <=> '\x19'

    @provide_file
    def test_maximum_line_length(self, src):
        self._parse_fails(src, line_number=19)

    @provide_file
    def test_invalid_text_character(self, src):
        warn = Mock()
        parse_helpfile(src, warn=warn)
        self.assertTrue(warn.called)
        _, kwargs = warn.call_args
        self.assertEqual(kwargs['line_number'], 18)

    #----------- File parsing -------------------

    @provide_file
    def test_ids_must_be_alphanumeric(self, src):
        """Test that a non-alphanumeral id fails parsing"""
        self._parse_fails(src, line_number=17)

    @provide_file
    def test_record_must_have_a_setting_line(self, src):
        """Check that a record missing a % line fails parsing"""
        self._parse_fails(src, line_number=16)

    @provide_file
    def test_record_codes_cannot_exceed_six_bytes(self, src):
        """Ensure record codes cannot exceed 6 bytes"""
        self._parse_fails(src, line_number=17)

    @provide_file
    def test_cannot_have_duplicate_record_codes(self, src):
        """Check that no two records can have an identical id code"""
        self._parse_fails(src, line_number=48)

    @provide_file
    def test_no_settings_before_records(self, src):
        """Ensure %-lines cannot precede record definitions"""
        self._parse_fails(src, line_number=2)

    @provide_file
    def test_only_one_setting_line_per_record(self, src):
        """Test that a record cannot have more than one %-line"""
        self._parse_fails(src, line_number=19)

    @provide_file
    def test_no_color_changes_before_records(self, src):
        """Color change lines cannot precede the initial record definition"""
        self._parse_fails(src, line_number=3)

    # TEST warn on adjacent .-lines

    @provide_file
    def test_no_text_before_record_definition(self, src):
        """Text lines cannot precede the initial record definition"""
        self._parse_fails(src, line_number=3)

    # TEST warn on trailing lines

    # TEST error on trailing lines if allow_trailing is false

    # TEST error on lowercase text if allow_lowercase is false

    @provide_file
    def test_line_length_specifier(self, src):
        """Test that line length specifier comments are enforced"""
        self._parse_fails(src, line_number=10)

    @unittest.skip('Not yet implemented')
    def test_allocated_line_count_must_be_met(self, src):
        """Requires that the line count specified in the %-line is met"""
        self._parse_fails(src, line_number=10)


if __name__ == '__main__':
    unittest.main()
