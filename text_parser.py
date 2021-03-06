import re

from errors import ParseError, LineLengthError
from help_record import HelpRecord


MAX_LINE_LENGTH = 40


def contains_lowercase(line):
    """Checks if the string contains a a character [a-z]"""
    return bool(re.search(r'[a-z]', line))

def invalid_char(line, allow_lowercase=True):
    pattern = r"[^A-Z0-9-+.,:& !@#%()/<>'*^?\u0014]"
    flags = re.IGNORECASE if allow_lowercase else 0
    return re.search(pattern, line, flags=flags)

def noop(*args, **kargs):
    pass


def check_line(line, permissive = True):
    '''Validate the line in the help file'''
    if line.startswith(';='):
        match = re.search(r'^;=\s*(\w{1,6})\s*$', line)
        if match:
            return match.group(1), None
        else:
            return None, 'Invalid code'
    elif line.startswith('%'):
        pattern = r'^%(\d{2})\D(\d)\s*$' if permissive else r'^%(\d{2}):(\d)$'
        match = re.search(pattern, line)
        if match:
            return (int(match.group(1)), int(match.group(2))), None
        else:
            return None, 'Invalid % specifier'
    elif line.startswith('.'):
        pattern = r'^\.(\d{3})(\s+;.*)?\s*$' if permissive else r'^\.(\d{3})$';
        match = re.search(pattern, line)
        if not match:
            return None, 'Invalid color specifier'
        elif int(match.group(1)) > 255 :
            return None, 'Color value out of bounds'
        else:
            return match.group(1), None
    elif line.startswith(';'):
        if re.search(r'Longest Line:\s*;$', line):
            return line[:-1] + '\x19', None
        return line, None
    else:
        if len(line.encode()) > MAX_LINE_LENGTH:
            return None, 'Line exceeds maximum length'
        char = invalid_char(line)
        if char:
            return line, 'Invalid character "{}"'.format(char.group())
        return line, None


def parse_helpfile(help_file,
        allow_lowercase=True, allow_trailing=True, warn=noop):
    '''Read a plaintext help file and create a list of records'''
    records = []
    current_record = None
    # Track which id codes have already been used
    code_set = set()
    options_set = False
    # Put inside a loop
    for line_number, line in enumerate(help_file, start = 1):
        # print('{:0>3} {}'.format(line_number, line.rstrip()))
        if line.startswith(';='):
            # warn('New record', line=line, line_number=line_number)
            if current_record and not options_set:
                message = 'Record "{}" must contain a % settings line'
                raise ParseError(message.format(current_record.code),
                        line=line,
                        line_number=line_number)
            match, issue = check_line(line.rstrip())
            if not match:
                raise ParseError('Invalid record code',
                        line=line,
                        line_number=line_number)
            # Enforce maximum code size
            if len(match.encode()) > 6:
                raise ParseError('Record code exceeds maximum length of 6 bytes',
                        line=line,
                        line_number=line_number)
            if match in code_set:
                raise ParseError('Duplicate record code',
                        line=line,
                        line_number=line_number)
            # start new record
            if current_record:
                records.append(current_record)
            current_record = HelpRecord(match)
            code_set.add(match)
            options_set = False
        elif line.startswith('%'):
            if not current_record:
                raise ParseError(
                        'Invalid placement of % line outside of record',
                        line=line,
                        line_number=line_number)
            if options_set:
                raise ParseError('Line length and mode already set',
                        line=line,
                        line_number=line_number)
            match, issue = check_line(line.rstrip())
            if match:
                options_set = True
                current_record.set_options(*match)
            else:
                raise ParseError('Unable to parse % expression',
                        line=line,
                        line_number=line_number)
        elif line.startswith('.'):
            if not current_record:
                raise ParseError(
                        'Invalid use of color specifier outside of record',
                        line=line,
                        line_number=line_number)
            match, issue = check_line(line.rstrip())
            if match:
                current_record.add_color(match)
            else:
                raise ParseError('Invalid color specifier',
                        line=line,
                        line_number=line_number)
        elif line.startswith(';'):
            if current_record:
                match, issue = check_line(line.rstrip())
                current_record.add_comment(match)
        else:
            if not current_record:
                raise ParseError(
                        'Invalid placement of text before record definition',
                        line=line,
                        line_number=line_number)
            match, issue = check_line(line.rstrip('\r\n'))
            if match is not None:
                # Handle trailing lines in record after the number allocated in
                # the % line.
                if current_record.line_count > current_record.max_lines:
                    if allow_trailing:
                        if not re.search(r'^!?\s*$', match):
                            warn('Additional line in record "{}"'.format(
                                current_record.code),
                                line=line,
                                line_number=line_number)
                    else:
                        raise ParseError('Additional line in record {}'.format(
                            current_record.code),
                            line=line,
                            line_number=line_number)
                if contains_lowercase(match):
                    if allow_lowercase:
                        match = match.upper()
                    else:
                        raise ParseError('Lowercase text is not permitted',
                                line=line,
                                line_number=line_number)
                if issue:
                    warn(issue, line=line, line_number=line_number)
                try:
                    current_record.add_line(match)
                except LineLengthError as err:
                    raise ParseError(
                            'Line exceeds length specifier ({} vs {})'.format(
                                err.line_length,
                                err.max_length),
                            line=line,
                            line_number=line_number)
            else:
                raise ParseError(issue,
                        line=line,
                        line_number=line_number)
    if current_record:
        if not options_set:
            message = 'Record "{}" must contain a % settings line'
            raise ParseError(message.format(current_record.code),
                    line=line,
                    line_number=line_number)
        records.append(current_record)
    return records
