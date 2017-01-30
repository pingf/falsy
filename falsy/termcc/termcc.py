# coding=utf-8
# author = Jesse MENG
# email: pingf@gmail.com
# Some ANSI escape sequences (not a complete list)
# Code	Name	Effect
#
# CSI n A	CUU – Cursor Up	Moves the cursor n (default 1) cells in the given direction. If the cursor is already at the edge of the screen, this has no effect.
#
# CSI n B	CUD – Cursor Down
#
# CSI n C	CUF – Cursor Forward
#
# CSI n D	CUB – Cursor Back
# CSI n E	CNL – Cursor Next Line	Moves cursor to beginning of the line n (default 1) lines down. (not ANSI.SYS)
# CSI n F	CPL – Cursor Previous Line	Moves cursor to beginning of the line n (default 1) lines up. (not ANSI.SYS)
# CSI n G	CHA – Cursor Horizontal Absolute	Moves the cursor to column n. (not ANSI.SYS)
#
# CSI n ; m H	CUP – Cursor Position	Moves the cursor to row n, column m. The values are 1-based, and default to 1 (top left corner) if omitted. A sequence such as CSI ;5H is a synonym for CSI 1;5H as well as CSI 17;H is the same as CSI 17H and CSI 17;1H
#
# CSI n J	ED – Erase Display	Clears part of the screen. If n is 0 (or missing), clear from cursor to end of screen. If n is 1, clear from cursor to beginning of the screen. If n is 2, clear entire screen (and moves cursor to upper left on DOS ANSI.SYS).
#
# CSI n K	EL – Erase in Line	Erases part of the line. If n is zero (or missing), clear from cursor to the end of the line. If n is one, clear from cursor to beginning of the line. If n is two, clear entire line. Cursor position does not change.
#
# CSI n S	SU – Scroll Up	Scroll whole page up by n (default 1) lines. New lines are added at the bottom. (not ANSI.SYS)
#
# CSI n T	SD – Scroll Down	Scroll whole page down by n (default 1) lines. New lines are added at the top. (not ANSI.SYS)
#
# CSI n ; m f	HVP – Horizontal and Vertical Position	Moves the cursor to row n, column m. Both default to 1 if omitted. Same as CUP
#
# CSI n m	SGR – Select Graphic Rendition	Sets SGR parameters, including text color. After CSI can be zero or more parameters separated with ;. With no parameters, CSI m is treated as CSI 0 m (reset / normal), which is typical of most of the ANSI escape sequences.
#
# CSI 5i	AUX Port On	Enable aux serial port usually for local serial printer
#
# CSI 4i	AUX Port Off	Disable aux serial port usually for local serial printer
#
# CSI 6 n	DSR – Device Status Report	Reports the cursor position (CPR) to the application as (as though typed at the keyboard) ESC[n;mR, where n is the row and m is the column.)
#
# CSI s	SCP – Save Cursor Position	Saves the cursor position.
#
# CSI u	RCP – Restore Cursor Position	Restores the cursor position.
# CSI ?25l	DECTCEM	Hides the cursor. (Note: the trailing character is lowercase L.)
# CSI ?25h	DECTCEM	Shows the cursor.
# SGR (Select Graphic Rendition) parameters
# Code	Effect	Note
# 0	Reset / Normal	all attributes off
# 1	Bold or increased intensity
# 2	Faint (decreased intensity)	Not widely supported.
# 3	Italic: on	Not widely supported. Sometimes treated as inverse.
# 4	Underline: Single
# 5	Blink: Slow	less than 150 per minute
# 6	Blink: Rapid	MS-DOS ANSI.SYS; 150+ per minute; not widely supported
# 7	Image: Negative	inverse or reverse; swap foreground and background (reverse video)
# 8	Conceal	Not widely supported.
# 9	Crossed-out	Characters legible, but marked for deletion. Not widely supported.
# 10	Primary(default) font
# 11–19	n-th alternate font	Select the n-th alternate font (14 being the fourth alternate font, up to 19 being the 9th alternate font).
# 20	Fraktur	hardly ever supported
# 21	Bold: off or Underline: Double	Bold off not widely supported; double underline hardly ever supported.
# 22	Normal color or intensity	Neither bold nor faint
# 23	Not italic, not Fraktur
# 24	Underline: None	Not singly or doubly underlined
# 25	Blink: off
# 26	Reserved
# 27	Image: Positive
# 28	Reveal	conceal off
# 29	Not crossed out
# 30–37	Set text color (foreground)	30 + n, where n is from the color table below
# 38	Reserved for extended set foreground color	typical supported next arguments are 5;n where n is color index (0..255) or 2;r;g;b where r,g,b are red, green and blue color channels (out of 255)
# 39	Default text color (foreground)	implementation defined (according to standard)
# 40–47	Set background color	40 + n, where n is from the color table below
# 48	Reserved for extended set background color	typical supported next arguments are 5;n where n is color index (0..255) or 2;r;g;b where r,g,b are red, green and blue color channels (out of 255)
# 49	Default background color	implementation defined (according to standard)
# 50	Reserved
# 51	Framed
# 52	Encircled
# 53	Overlined
# 54	Not framed or encircled
# 55	Not overlined
# 56–59	Reserved
# 60	ideogram underline or right side line	hardly ever supported
# 61	ideogram double underline or double line on the right side	hardly ever supported
# 62	ideogram overline or left side line	hardly ever supported
# 63	ideogram double overline or double line on the left side	hardly ever supported
# 64	ideogram stress marking	hardly ever supported
# 65	ideogram attributes off	hardly ever supported, reset the effects of all of 60–64
# 90–97	Set foreground text color, high intensity	aixterm (not in standard)
# 100–107	Set background color, high intensity	aixterm (not in standard)


# Color table
# Intensity	0	1	2	3	4	5	6	7
# Normal	Black	Red	Green	Yellow[12]	Blue	Magenta	Cyan	White
# Bright	Black	Red	Green	Yellow	Blue	Magenta	Cyan	White


TERMCC_PREFIX = '\033['
TERMCC_SUFFIX = 'm'
TERMCC_RESET = 0

TERMCC_COLOR_TABLE = {
    'Black': 0,
    'Red': 1,
    'Green': 2,
    'Yellow': 3,
    'Blue': 4,
    'Magenta': 5,
    'Cyan': 6,
    'White': 7
}
TERMCC_TEXT_COLOR_BASE = 30
TERMCC_BACK_COLOR_BASE = 40

TERMCC_NORMAL = 1
TERMCC_BOLD = 1
TERMCC_FAINT = 2
TERMCC_ITALIC = 3
TERMCC_UNDERLINE = 4


def _wrap(code):
    return TERMCC_PREFIX + str(code) + TERMCC_SUFFIX


def _reset():
    return _wrap(TERMCC_RESET)


def _text_color(color):
    return _wrap(TERMCC_TEXT_COLOR_BASE + TERMCC_COLOR_TABLE[color])


def _back_color(color):
    return _wrap(TERMCC_BACK_COLOR_BASE + TERMCC_COLOR_TABLE[color])

def normal(text):
    return _wrap(TERMCC_NORMAL) + text + _reset()

def bold(text):
    return _wrap(TERMCC_BOLD) + text + _reset()


def faint(text):
    return _wrap(TERMCC_FAINT) + text + _reset()


def italic(text):
    return _wrap(TERMCC_ITALIC) + text + _reset()


def underline(text):
    return _wrap(TERMCC_UNDERLINE) + text + _reset()


def black(text):
    return _text_color('Black') + text + _reset()


def red(text):
    return _text_color('Red') + text + _reset()


def green(text):
    return _text_color('Green') + text + _reset()


def yellow(text):
    return _text_color('Yellow') + text + _reset()


def blue(text):
    return _text_color('Blue') + text + _reset()


def magenta(text):
    return _text_color('Magenta') + text + _reset()


def cyan(text):
    return _text_color('Cyan') + text + _reset()


def white(text):
    return _text_color('White') + text + _reset()


def black_(text):
    return _back_color('Black') + text + _reset()


def red_(text):
    return _back_color('Red') + text + _reset()


def green_(text):
    return _back_color('Green') + text + _reset()


def yellow_(text):
    return _back_color('Yellow') + text + _reset()


def blue_(text):
    return _back_color('Blue') + text + _reset()


def magenta_(text):
    return _back_color('Magenta') + text + _reset()


def cyan_(text):
    return _back_color('Cyan') + text + _reset()


def white_(text):
    return _back_color('White') + text + _reset()

if __name__ == '__main__':
    print(yellow_(blue('hello world')))
    print(red_(blue('hello world')))
    print(bold(red('hello world')))
    print(faint(red('hello world')))
    print(red('hello world'))
    print(italic(red('hello world')))
    print(underline(red('hello world'))+' ... '+magenta_(cyan('hello world')))