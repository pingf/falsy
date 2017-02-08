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
# \e[0m resets all colors and attributes.
# \e[20m resets only attributes (underline, etc.), leaving colors unchanged.
# \e[39m resets only foreground color, leaving attributes unchanged.
# \e[49m resets only background color, leaving attributes unchanged.


TERMCC_PREFIX = '\033['
TERMCC_SUFFIX = 'm'

TERMCC_FORE = '38;5;'
TERMCC_RESET_FORE = '39;5;'
TERMCC_BACK = '48;5;'
TERMCC_RESET_BACK = '49;5;'
TERMCC_STYLE = ''
TERMCC_RESET_STYLE = ''

TERMCC_RESET_ALL = '0'
TERMCC_RESET_ALL_STYLE = '20'
TERMCC_RESET_ALL_FORE = '39'
TERMCC_RESET_ALL_BACK = '49'

TERMCC_FORE_TABLE = TERMCC_BACK_TABLE = {
    'black': 0,
    'red': 1,
    'green': 2,
    'yellow': 3,
    'blue': 4,
    'magenta': 5,
    'cyan': 6,
    'lightgray': 7,
    'darkgray': 8,
    'lightred': 9,
    'lightgreen': 10,
    'lightyellow': 11,
    'lightblue': 12,
    'lightmagenta': 13,
    'lightcyan': 14,
    'white': 15,
}
TERMCC_STYLE_TABLE = {
    'bold': 1,
    'dim': 2,
    'italic': 3,
    'underlined': 4,
    'blink': 5,
    'reverse': 7,
    'hidden': 8,
}


def cc(text, **kwargs):
    c = kwargs.get('fore')
    b = kwargs.get('back')
    ss = kwargs.get('styles')
    p = ''
    if c:
        p += fore(c)
        print(p)
    if b:
        p += back(b)
    if ss:
        for s in ss:
            p += style(s)
    return p + text + reset()


def wrap(text):
    return TERMCC_PREFIX + str(text) + TERMCC_SUFFIX


def reset():
    return wrap(TERMCC_RESET_ALL)


def rastyle():
    return wrap(TERMCC_RESET_ALL_STYLE)


def rafore():
    return wrap(TERMCC_RESET_ALL_FORE)


def raback():
    return wrap(TERMCC_RESET_ALL_BACK)


def fore(fore):
    if type(fore) == str:
        return wrap(TERMCC_FORE + str(TERMCC_FORE_TABLE[fore]))
    if 0 < fore <= 256:
        return wrap(TERMCC_FORE + str(fore))
    return wrap(TERMCC_FORE + str(TERMCC_FORE_TABLE['white']))


def rfore(fore):
    return wrap(TERMCC_RESET_FORE + str(TERMCC_FORE_TABLE[fore]))


def back(color):
    return wrap(TERMCC_BACK + str(TERMCC_FORE_TABLE[color]))


def rback(color):
    return wrap(TERMCC_RESET_BACK + str(TERMCC_BACK_TABLE[color]))


def style(style):
    return wrap(TERMCC_STYLE + str(TERMCC_STYLE_TABLE[style]))


def rstyle(style):
    return wrap(TERMCC_RESET_STYLE + str(TERMCC_STYLE_TABLE[style] + 20))


def bold():
    return style('bold')  #


def rbold():
    return rstyle('bold')


def dim():
    return style('dim')  #


def rdim():
    return rstyle('dim')


def italic():
    return style('italic')  #


def ritalic():
    return rstyle('italic')


def underlined():
    return style('italic')


def runderlined():
    return rstyle('italic')


def blink():
    return style('blink')


def rblink():
    return rstyle('blink')


def reverse():
    return style('reverse')


def rreverse():
    return rstyle('reverse')


def hidden():
    return style('hidden')  #


def rhidden():
    return rstyle('hidden')


def black():
    return fore('black')


def rblack():
    return rfore('black')


def red():
    return fore('red')


def rred():
    return rfore('red')


def green():
    return fore('green')


def rgreen():
    return rfore('green')


def yellow():
    return fore('yellow')


def ryellow():
    return rfore('yellow')


def blue():
    return fore('blue')


def rblue():
    return rfore('blue')


def magenta():
    return fore('magenta')


def rmagenta():
    return rfore('magenta')


def cyan():
    return fore('cyan')


def rcyan():
    return rfore('cyan')


def lgray():
    return fore('lightgray')


def rlgray():
    return rfore('lightgray')


def gray():
    return fore('darkgray')


def rgray():
    return rfore('darkgray')


def lred():
    return fore('lightred')


def rlred():
    return rfore('lightred')


def lgreen():
    return fore('lightgreen')


def rlgreen():
    return rfore('lightgreen')


def lyellow():
    return fore('lightyellow')


def rlyellow():
    return rfore('lightyellow')


def lblue():
    return fore('lightblue')


def rlblue():
    return rfore('lightblue')


def lmagenta():
    return fore('lightmagenta')


def rlmagenta():
    return rfore('lightmagenta')


def rlcyan():
    return rfore('lightcyan')


def white():
    return fore('white')


def rwhite():
    return rfore('white')


def black_():
    return back('black')


def rblack_():
    return rback('black')


def red_():
    return back('red')


def rred_():
    return rback('red')


def green_():
    return back('green')


def rgreen_():
    return rback('green')


def yellow_():
    return back('yellow')


def ryellow_():
    return rback('yellow')


def blue_():
    return back('blue')


def rblue_():
    return rback('blue')


def magenta_():
    return back('magenta')


def rmagenta_():
    return rback('magenta')


def cyan_():
    return back('cyan')


def rcyan_():
    return rback('cyan')


def lgray_():
    return back('lightgray')


def rlgray_():
    return rback('lightgray')


def gray_():
    return back('darkgray')


def rgray_():
    return rback('darkgray')


def lred_():
    return back('lightred')


def rlred_():
    return rback('lightred')


def lgreen_():
    return back('lightgreen')


def rlgreen_():
    return rback('lightgreen')


def lyellow_():
    return back('lightyellow')


def rlyellow_():
    return rback('lightyellow')


def lblue_():
    return back('lightblue')


def rlblue_():
    return rback('lightblue')


def lmagenta_():
    return back('lightmagenta')


def rlmagenta_():
    return rback('lightmagenta')


def lcyan_():
    return back('lightcyan')


def rlcyan_():
    return rback('lightcyan')


def white_():
    return back('white')


def rwhite_():
    return rback('white')


if __name__ == '__main__':
    print(yellow_(blue('hello world')))
    print(red_(blue('hello world')))
