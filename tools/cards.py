#!/usr/bin/env python3
"""Render a punched deck as IBM 5081-style card images (PostScript).

Input is a raw deck as written by the Hercules 3525 punch in binary mode.

Usage: tools/cards.py deck.ebc [--first N] [--count N] [--no-interpret] | ps2pdf - out.pdf

Parameters:
    --first Sets what card to start on
    --count Number of cards to render
    --no-interpret Don't print interpreted characters on top edge of cards.
"""

import argparse
import sys

# 12-bit column images: 0x800 = row 12, 0x400 = row 11, 0x200 = row 0,
# 0x100 = row 1, ... 0x001 = row 9.
EBCDIC_TO_HOL = [
    0xB03, 0x901, 0x881, 0x841, 0x821, 0x811, 0x809, 0x805,
    0x803, 0x903, 0x883, 0x843, 0x823, 0x813, 0x80B, 0x807,
    0xD03, 0x501, 0x481, 0x441, 0x421, 0x411, 0x409, 0x405,
    0x403, 0x503, 0x483, 0x443, 0x423, 0x413, 0x40B, 0x407,
    0x703, 0x301, 0x281, 0x241, 0x221, 0x211, 0x209, 0x205,
    0x203, 0x303, 0x283, 0x243, 0x223, 0x213, 0x20B, 0x207,
    0xF03, 0x101, 0x081, 0x041, 0x021, 0x011, 0x009, 0x005,
    0x003, 0x103, 0x083, 0x043, 0x023, 0x013, 0x00B, 0x007,
    0x000, 0xB01, 0xA81, 0xA41, 0xA21, 0xA11, 0xA09, 0xA05,
    0xA03, 0x902, 0x882, 0x842, 0x822, 0x812, 0x80A, 0x806,
    0x800, 0xD01, 0xC81, 0xC41, 0xC21, 0xC11, 0xC09, 0xC05,
    0xC03, 0x502, 0x482, 0x442, 0x422, 0x412, 0x40A, 0x406,
    0x400, 0x300, 0x681, 0x641, 0x621, 0x611, 0x609, 0x605,
    0x603, 0x302, 0xC00, 0x242, 0x222, 0x212, 0x20A, 0x206,
    0xE00, 0xF01, 0xE81, 0xE41, 0xE21, 0xE11, 0xE09, 0xE05,
    0xE03, 0x102, 0x082, 0x042, 0x022, 0x012, 0x00A, 0x006,
    0xB02, 0xB00, 0xA80, 0xA40, 0xA20, 0xA10, 0xA08, 0xA04,
    0xA02, 0xA01, 0xA82, 0xA42, 0xA22, 0xA12, 0xA0A, 0xA06,
    0xD02, 0xD00, 0xC80, 0xC40, 0xC20, 0xC10, 0xC08, 0xC04,
    0xC02, 0xC01, 0xC82, 0xC42, 0xC22, 0xC12, 0xC0A, 0xC06,
    0x702, 0x700, 0x680, 0x640, 0x620, 0x610, 0x608, 0x604,
    0x602, 0x601, 0x682, 0x642, 0x622, 0x612, 0x60A, 0x606,
    0xF02, 0xF00, 0xE80, 0xE40, 0xE20, 0xE10, 0xE08, 0xE04,
    0xE02, 0xE01, 0xE82, 0xE42, 0xE22, 0xE12, 0xE0A, 0xE06,
    0xA00, 0x900, 0x880, 0x840, 0x820, 0x810, 0x808, 0x804,
    0x802, 0x801, 0xA83, 0xA43, 0xA23, 0xA13, 0xA0B, 0xA07,
    0x600, 0x500, 0x480, 0x440, 0x420, 0x410, 0x408, 0x404,
    0x402, 0x401, 0xC83, 0xC43, 0xC23, 0xC13, 0xC0B, 0xC07,
    0x282, 0x701, 0x280, 0x240, 0x220, 0x210, 0x208, 0x204,
    0x202, 0x201, 0x683, 0x643, 0x623, 0x613, 0x60B, 0x607,
    0x200, 0x100, 0x080, 0x040, 0x020, 0x010, 0x008, 0x004,
    0x002, 0x001, 0xE83, 0xE43, 0xE23, 0xE13, 0xE0B, 0xE07,
]

# Hercules translates ASCII to EBCDIC with code page 1047, which differs from
# Python's cp037 in where it puts the brackets, caret and not sign.
CP1047_FROM_CP037 = str.maketrans('Ý¨¬^[]', '[]^¬Ý¨')

# IBM 5081 card geometry, in inches
CARD_W, CARD_H = 7.375, 3.25
COL_X0, COL_PITCH = 0.251, 0.087     # center of column 1, column spacing
ROW_Y0, ROW_PITCH = 0.25, 0.25       # center of row 12 from top, row spacing
HOLE_W, HOLE_H = 0.055, 0.125
CORNER = 0.25                        # top-left corner cut

PT = 72.0
CARDS_PER_PAGE = 3
PAGE_W, PAGE_H = 8.5, 11.0
GAP = 0.3


def ps_string(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch in '()\\':
            out.append('\\' + ch)
        elif 32 <= o < 127:
            out.append(ch)
        elif o < 256:
            out.append('\\%03o' % o)    # Latin-1, e.g. cent and not signs
        else:
            out.append('?')
    return '(' + ''.join(out) + ')'


PROLOG = """%!PS-Adobe-3.0
%%Title: Punched card deck
%%Pages: {pages}
%%EndComments
/Courier findfont dup length dict begin
  {{1 index /FID ne {{def}} {{pop pop}} ifelse}} forall
  /Encoding ISOLatin1Encoding def
  currentdict end /Courier-L1 exch definefont pop
/inch {{72 mul}} def
% x y w h hole
/hole {{4 2 roll moveto dup 0 exch rlineto exch 0 rlineto neg 0 exch rlineto
  closepath fill}} def
% card outline with top-left corner cut, origin at bottom-left
/outline {{newpath 0 0 moveto {w} 0 lineto {w} {h} lineto {c} {h} lineto
  0 {hc} lineto closepath}} def
% blank card face: stock, printed digit rows and column numbers
/face {{
  gsave outline 0.953 0.914 0.776 setrgbcolor fill grestore
  gsave outline 0.4 setgray 0.5 setlinewidth stroke grestore
  0.45 0.35 0.3 setrgbcolor
  /Courier-L1 findfont 5.2 scalefont setfont
  0 1 9 {{ /r exch def
    0 1 79 {{ /c exch def
      {x0} c {px} mul add 1.56 sub
      {h} {y0} sub r 2 add {py} mul sub 1.8 sub moveto
      r 1 string cvs show
    }} for
  }} for
  /Courier-L1 findfont 2.6 scalefont setfont
  0 1 79 {{ /c exch def
    c 1 add 2 string cvs dup length 0.78 mul /hw exch def
    {x0} c {px} mul add hw sub {h} {y0} sub 2.5 {py} mul sub 0.6 sub
    2 copy moveto 2 index show
    pop {y0} 0.48 {py} mul sub moveto show
  }} for
}} def
"""


def card_ps(record, interpret):
    x0, px = COL_X0 * PT, COL_PITCH * PT
    y0, py = ROW_Y0 * PT, ROW_PITCH * PT
    hw, hh = HOLE_W * PT, HOLE_H * PT
    h = CARD_H * PT
    lines = ['face']
    if interpret:
        lines.append('0 setgray /Courier-L1 findfont 7 scalefont setfont')
        text = record.decode('cp037').translate(CP1047_FROM_CP037)
        for c, ch in enumerate(text):
            if ch.strip():
                x = x0 + c * px - 2.1
                lines.append('%.2f %.2f moveto %s show' % (x, h - 7.2, ps_string(ch)))
    lines.append('0.12 setgray')
    for c, b in enumerate(record):
        hol = EBCDIC_TO_HOL[b]
        for r in range(12):
            if hol & (0x800 >> r):
                x = x0 + c * px - hw / 2
                y = h - (y0 + r * py) - hh / 2
                lines.append('%.2f %.2f %.2f %.2f hole' % (x, y, hw, hh))
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('deck', help='raw EBCDIC deck, 80 bytes per card')
    ap.add_argument('--first', type=int, default=1, help='first card (1-based)')
    ap.add_argument('--count', type=int, help='number of cards (default: rest)')
    ap.add_argument('--no-interpret', action='store_true',
                    help='do not print characters along the top edge')
    args = ap.parse_args()

    data = open(args.deck, 'rb').read()
    if len(data) % 80:
        sys.exit('%s: length %d is not a multiple of 80' % (args.deck, len(data)))
    cards = [data[i:i + 80] for i in range(0, len(data), 80)]
    end = len(cards) if args.count is None else args.first - 1 + args.count
    cards = cards[args.first - 1:end]
    if not cards:
        sys.exit('no cards selected')

    pages = (len(cards) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
    w, h = CARD_W * PT, CARD_H * PT
    out = sys.stdout
    out.write(PROLOG.format(
        pages=pages, w=w, h=h, c=CORNER * PT, hc=h - CORNER * PT,
        x0=COL_X0 * PT, px=COL_PITCH * PT, y0=ROW_Y0 * PT, py=ROW_PITCH * PT))
    out.write('%%EndProlog\n')

    left = (PAGE_W - CARD_W) / 2 * PT
    stack = CARDS_PER_PAGE * CARD_H + (CARDS_PER_PAGE - 1) * GAP
    top = PAGE_H * PT - (PAGE_H - stack) / 2 * PT
    for p in range(pages):
        out.write('%%%%Page: %d %d\n' % (p + 1, p + 1))
        for i, rec in enumerate(cards[p * CARDS_PER_PAGE:(p + 1) * CARDS_PER_PAGE]):
            n = args.first + p * CARDS_PER_PAGE + i
            y = top - h - i * (CARD_H + GAP) * PT
            out.write('gsave %.2f %.2f translate\n' % (left, y))
            out.write(card_ps(rec, not args.no_interpret) + '\n')
            out.write('grestore\n')
            out.write('0.5 setgray /Courier-L1 findfont 6 scalefont setfont '
                      '%.2f %.2f moveto (card %d) show\n' % (left, y - 8, n))
        out.write('showpage\n')
    out.write('%%EOF\n')


if __name__ == '__main__':
    main()
