Race Into Space Help Editor
===========================

Convert .cdr files into plaintext and back.


## Writing a text file
A plaintext help file consists of a series of entries that display dialog
messages. Each entry has a number of components.

* code - a unique value up to 6 single-byte characters long
* comments - any line that begins with a semicolon ';' is treated as a comment
  and will be included in the binary file but ignored by _raceintospace_.
* line count/mode - a line that begins with '%' specifies the number of lines in
  the entry as well as the mode (continue vs yes/no prompt).
* color change - an initial '.' indicates the a change in text color
* text - lines of plain text that are included in the dialog prompt

Each of the components is discussed in greater depth below.

### Code

The first line of any entry is the id code. The code provides a unique
identifier for the entry, and is used in the game code to specify which dialog
text should be used. Within the text file, the id defines the beginning of the
dialog entry and the end of the previous entry.

Beginning a line with the sequence `;=` marks that line as defining the
identifier. The rest of the line may include only the identifying sequence and
whitespace. Any code may be used that is an alphanumeric string of 1-6
characters (technically `[0-9a-zA-Z_]{1,6}`). Codes are case-insensitive, so
"k123" is equivalent to "K123".

By convention, all existing codes in use consist of an initial alphabet
character followed by a three-digit number, including leading zeros.

Example:

    ;= I110

### Comments

Lines beginning with `;` are treated as comments. They are included in the
binary file, but will be ignored by _raceintospace_ in their entirety.

Within the text file, some lines are treated differently than others. While
these do not have any effect on the game, they may modify the behavior of the
binary file converter.

If a comment contains the text "Longest Line:", then if the next line in the
file is also a comment, it will be treated as specifying the maximum line
length for subsequent lines in that entry. This was presumably done in the
original file so that the developers could easily indicate to themselves how
long lines should be. If used, these lines are typically the first lines after
the entry identifier.

Example:

    ; This is a normal comment with no effect
    ; Longest Line:
    ;XXXXXXXXXXXXXXXXXXXXXXXX
    This text will be treated
    normally but
    this line will generate an error

### Line count and mode

Each entry has a mandatory specifier indicating the number of lines of text in
the entry. Only those number of lines will actually be read by _raceintospace_,
with any subsequent lines being ignored. This specifier also defines the mode of
the dialog displayed.

The line count and mode specifier consists of a line starting with a percentage
sign character `%` followed by a two-digit line count, an intervening character,
and then a single digit mode.

Example:

    %08:1

If the line count is less than 10, a leading 0 must be used. The separator, ':'
in the example, can be any single byte character, but ':' is suggested to
maintain consistency.

Mode is specified by a single digit 0 - 9.

* if mode is 0, the dialog will have a 'Continue' button
* if mode is some other value, the dialog will have 'Yes' and 'No' options

### Color change

The color of the text may be set within the entry. A color palette value is
provided, which sets the foreground color for the dialog to use that palette
value for the remainder of the text, or until a new color is specified.

Color changes are indicated by a line starting with an initial `.` and
immediately followed by a three-digit integer value in the range 000 through
255, with leading zeros where needed. No other characters are permitted on the
line.

If two color change lines are specified without intervening text, the converter
will issue a warning.

Example:

    .053

### Text

The majority of the dialog entry will consist of the plain text intended for
display to the player. Any line in the text file that is not designated as
another type will be treated as a line of dialog text. The first line of text
will be used as the dialog title.

Any line that does not begin with one of the characters `;`, `%`, or `.` is
considered a text line. Text lines may have a maximum of 40 characters, though
further restrictions may be employed within the converter (see comments).

Within each line, any of the alphanumeric characters are permitted as well as
the characters

    . - + , ; & <space> ! @ # % ( ) / < > ' * ^ ? \u0014

Lower case characters are permitted but will be automatically translated to
their upper case counterparts, as _raceintospace_ cannot display lower case
characters properly.

## Creating a binary file

Once a properly formatted text file has been readied, a binary version may be
generated using the conversion program.

    > python3 writefile.py [textfile] --output [dest]
