#!/usr/bin/env python3
"""pdf2pptx.py -- PowerPoint versions of the NTU deck, made locally from build/main.pdf.

Two files are written (default: build/):
  IWO_NTU_presentation_editable.pptx  every text line is an editable PowerPoint text box, placed and spaced as in the
                                      PDF (Arial, metric-compatible with the TeX Gyre Heros of the PDF); figures,
                                      display equations and a few special math glyphs are pictures; rules, lines and
                                      the NTU emblem are a background picture.
  IWO_NTU_presentation_exact.pptx     every slide is the PDF page as one high-resolution picture (pixel-identical).
Both carry the frame title in a title placeholder, so the outline, navigation and accessibility checker see it.

Text classes come from build_pptx/main_marked.pdf (tools/pptx/build_marked.sh): display math and small capitals are
tagged there with reserved colours. Its characters are matched to main.pdf in content-stream order; the script
stops if the two PDFs do not have the same characters in the same order.

Usage: python3 tools/pptx/pdf2pptx.py [--pages 1-5,9] [--out build] [--zoom 8.4668]
"""
import argparse
import io
import os
import re
import sys

import pymupdf
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))           # presentation_ntu/
REAL_PDF = os.path.join(ROOT, "build", "main.pdf")
MARKED_PDF = os.path.join(ROOT, "build_pptx", "main_marked.pdf")

SLIDE_W, SLIDE_H = 12192000, 6858000                    # EMU, 13.333 in x 7.5 in (16:9)
MARK_DMATH = (1, 0, 1)
MARK_SC = (0, 1, 2)

# Arial metrics (Liberation fonts are metric-compatible with Arial and Courier New)
LIB = "/usr/share/fonts/truetype/liberation/"
METRIC_FILES = {
    ("Arial", False, False): "LiberationSans-Regular.ttf", ("Arial", True, False): "LiberationSans-Bold.ttf",
    ("Arial", False, True): "LiberationSans-Italic.ttf", ("Arial", True, True): "LiberationSans-BoldItalic.ttf",
    ("Courier New", False, False): "LiberationMono-Regular.ttf", ("Courier New", True, False): "LiberationMono-Bold.ttf",
    ("Courier New", False, True): "LiberationMono-Italic.ttf", ("Courier New", True, True): "LiberationMono-BoldItalic.ttf",
}
# first baseline of a text box with single (100 %) line spacing, below the box top, in em: 1.0 for Arial
# (measured in LibreOffice, whose PPTX layout follows PowerPoint: line height 1.2 em, cap top at 0.31 em)
ASCENT = 1.0
DESCENT = 0.2
SMALLCAPS_SCALE = 0.80  # size of small-capital letters relative to capitals

# glyphs that Arial lacks or that TeX draws in a way a font cannot reproduce: kept as pictures
PICTURE_GLYPHS = set("∥∝≲≪≫⇒∓⟨⟩√�")
ACCENTS = set("¯˜ˆˇ˙¨´`˘˚") | {chr(c) for c in range(0x300, 0x370)}
MATH_ITALIC_FONTS = ("zsfmi-reg", "rtxmi")              # slanted letters; zsfmia (digits, upright Greek) is upright
FIGURE_TEXT_FONTS = ("LiberationSans", "STIXGeneral", "DejaVu")   # matplotlib text: must lie inside a figure
TYPEWRITER_FONTS = ("F264", "F267", "F314")              # \texttt (subset fonts without a base name)
EMBLEM_FILES = ("ntu_logo_header",)                      # kept in the background picture


# ----------------------------------------------------------------------------------------------------------------------
# metrics
class Metrics:
    """Advance widths with pair kerning (HarfBuzz), as PowerPoint and LibreOffice set kerned text."""
    FEATURES = {"kern": True, "liga": False, "clig": False}

    def __init__(self):
        self.fonts = {}

    def _font(self, key):
        if key not in self.fonts:
            path = LIB + METRIC_FILES[key]
            face = hb.Face(hb.Blob.from_file_path(path))
            self.fonts[key] = (TTFont(path).getBestCmap(), hb.Font(face), face.upem)
        return self.fonts[key]

    def has(self, ch, face="Arial"):
        return ord(ch) in self._font((face, False, False))[0]

    def width(self, text, face, bold, italic, size):
        cmap, font, upm = self._font((face, bold, italic))
        if any(ord(ch) not in cmap for ch in text):
            return None
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, self.FEATURES)
        return sum(p.x_advance for p in buf.glyph_positions) / upm * size


METRICS = Metrics()


# ----------------------------------------------------------------------------------------------------------------------
# PDF content stream: positions of the XObjects drawn by the page (figures, emblem)
TOKEN = re.compile(rb"""
    (?P<ws>\s+|%[^\r\n]*)
  | (?P<str>\()
  | (?P<hex><[0-9A-Fa-f\s]*>)
  | (?P<dict><<|>>)
  | (?P<arr>[\[\]{}])
  | (?P<name>/[^\s/\[\]()<>{}%]*)
  | (?P<num>[+-]?(?:\d+\.?\d*|\.\d+))
  | (?P<op>[A-Za-z'"*][A-Za-z0-9'"*]*)
""", re.X)


def _skip_string(data, i):
    depth, n = 1, len(data)
    while i < n and depth:
        c = data[i]
        if c == 0x5C:           # backslash escape
            i += 2
            continue
        if c == 0x28:
            depth += 1
        elif c == 0x29:
            depth -= 1
        i += 1
    return i


def mat_mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, e * A + f * C + E, e * B + f * D + F)


def xobject_placements(doc, page):
    """[(name, xref, bbox top-left coordinates)] for every XObject the page content draws directly."""
    names = {name: xref for xref, name, invoker, _ in page.get_xobjects() if invoker == 0}
    data = page.read_contents()
    ctm, stack, operands, out = (1, 0, 0, 1, 0, 0), [], [], []
    i, n = 0, len(data)
    while i < n:
        m = TOKEN.match(data, i)
        if not m:
            i += 1
            continue
        kind = m.lastgroup
        i = m.end()
        if kind == "ws":
            continue
        if kind == "str":
            i = _skip_string(data, i)
            operands.append(None)
            continue
        if kind in ("hex", "dict", "arr"):
            operands.append(None)
            continue
        tok = m.group(kind)
        if kind == "num":
            operands.append(float(tok))
            continue
        if kind == "name":
            operands.append(tok.decode("latin-1"))
            continue
        op = tok.decode("latin-1")
        if op == "q":
            stack.append(ctm)
        elif op == "Q":
            ctm = stack.pop() if stack else (1, 0, 0, 1, 0, 0)
        elif op == "cm" and len(operands) >= 6 and all(isinstance(v, float) for v in operands[-6:]):
            ctm = mat_mul(tuple(operands[-6:]), ctm)
        elif op == "Do" and operands and isinstance(operands[-1], str):
            name = operands[-1][1:]
            xref = names.get(name)
            if xref:
                out.append((name, xref, _xobject_rect(doc, xref, ctm, page.rect.height)))
        operands = []
    return out


def _xobject_rect(doc, xref, ctm, page_h):
    sub = doc.xref_get_key(xref, "Subtype")[1]
    if sub == "/Image":
        x0, y0, x1, y1 = 0, 0, 1, 1
        mat = (1, 0, 0, 1, 0, 0)
    else:
        bb = [float(v) for v in doc.xref_get_key(xref, "BBox")[1].strip("[]").split()]
        x0, y0, x1, y1 = bb
        mt = doc.xref_get_key(xref, "Matrix")
        mat = tuple(float(v) for v in mt[1].strip("[]").split()) if mt[0] == "array" else (1, 0, 0, 1, 0, 0)
    full = mat_mul(mat, ctm)
    pts = []
    for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        a, b, c, d, e, f = full
        pts.append((a * x + c * y + e, b * x + d * y + f))
    xs = [p[0] for p in pts]
    ys = [page_h - p[1] for p in pts]
    return pymupdf.Rect(min(xs), min(ys), max(xs), max(ys))


def xobject_file(doc, xref):
    v = doc.xref_get_key(xref, "PTEX.FileName")
    return v[1] if v[0] != "null" else ""


# ----------------------------------------------------------------------------------------------------------------------
# characters
class Ch:
    __slots__ = ("u", "font", "size", "color", "x0", "x1", "y", "bbox", "dir", "cls", "seq", "lig")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def cx(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    @property
    def cy(self):
        return (self.bbox[1] + self.bbox[3]) / 2


def page_chars(real_page, marked_page):
    rs, ms = real_page.get_texttrace(), marked_page.get_texttrace()
    mchars = []
    for s in ms:
        tag = tuple(round(v * 255) for v in s["color"]) if s["color"] else None
        for c in s["chars"]:
            mchars.append((c[0], tag))
    out, k = [], 0
    for s in rs:
        if s["type"] == 3:      # invisible text
            k += len(s["chars"])
            continue
        col = s["color"] or (0, 0, 0)
        for c in s["chars"]:
            mu, tag = mchars[k]
            if mu != c[0]:
                raise SystemExit(f"page {real_page.number + 1}: marked PDF differs at char {k} "
                                 f"({chr(c[0])!r} vs {chr(mu)!r}); rebuild both PDFs")
            k += 1
            cls = "dmath" if tag == MARK_DMATH else ("sc" if tag == MARK_SC else "text")
            bb = c[3]
            out.append(Ch(u=chr(c[0]), font=s["font"], size=s["size"], color=col, x0=c[2][0], y=c[2][1],
                          x1=bb[2], bbox=bb, dir=tuple(round(v, 3) for v in s["dir"]), cls=cls, seq=s["seqno"],
                          lig=c[1] == -1))     # second letter of a ligature: no glyph of its own
    if k != len(mchars):
        raise SystemExit(f"page {real_page.number + 1}: marked PDF has {len(mchars)} chars, main.pdf {k}")
    return out


def font_style(ch):
    """(face, bold, italic) for a character."""
    f = ch.font
    if any(f.startswith(t) for t in TYPEWRITER_FONTS):
        return "Courier New", False, False
    if f.startswith("TeXGyreHeros"):
        return "Arial", "Bold" in f, "Italic" in f
    if f in MATH_ITALIC_FONTS:
        return "Arial", False, ch.u.isalpha()
    return "Arial", False, False


def display_char(ch):
    return "*" if ch.u == "∗" else ch.u


# ----------------------------------------------------------------------------------------------------------------------
# picture regions
def merge_rects(rects, pad=0.0):
    rects = [pymupdf.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        out = []
        while rects:
            r = rects.pop()
            grown = pymupdf.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)
            for o in rects[:]:
                if grown.intersects(o):
                    r |= o
                    rects.remove(o)
                    changed = True
                    grown = pymupdf.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)
            out.append(r)
        rects = out
    return rects


def picture_regions(doc, page, chars):
    """Regions drawn as pictures: figures, display math, special glyphs, rotated text. Returns (regions, emblem)."""
    figs, emblem = [], []
    for name, xref, rect in xobject_placements(doc, page):
        if any(e in xobject_file(doc, xref) for e in EMBLEM_FILES):
            emblem.append(rect)
        else:
            figs.append(rect)
    special = []
    dm = [pymupdf.Rect(c.bbox) for c in chars if c.cls == "dmath"]
    for c in chars:
        if c.cls == "dmath" or any(r.contains(pymupdf.Point(c.cx, c.cy)) for r in figs):
            continue
        rotated = c.dir != (1.0, 0.0)
        odd = c.font.startswith("txex") or c.font == "txsyc" or c.u in PICTURE_GLYPHS or \
            (not METRICS.has(display_char(c)) and font_style(c)[0] == "Arial")
        if c.u in ACCENTS:
            # the accent and the letter under it
            r = pymupdf.Rect(c.bbox)
            for o in chars:
                if o is not c and o.x0 < c.bbox[2] and o.x1 > c.bbox[0] and 0 <= o.y - c.y < 1.2 * c.size:
                    r |= pymupdf.Rect(o.bbox)
            special.append(r)
        elif rotated or odd:
            special.append(pymupdf.Rect(c.bbox))
    regions = [pymupdf.Rect(r.x0 - 0.6, r.y0 - 0.6, r.x1 + 0.6, r.y1 + 0.6) for r in merge_rects(dm, pad=2.5)]
    regions += [pymupdf.Rect(r.x0 - 0.3, r.y0 - 0.3, r.x1 + 0.3, r.y1 + 0.3) for r in merge_rects(special, pad=0.4)]
    regions += figs
    regions = merge_rects(regions)
    # a region that cuts a character in two takes the whole character
    for _ in range(3):
        grew = False
        for r in regions:
            for c in chars:
                cb = pymupdf.Rect(c.bbox)
                inner = pymupdf.Rect(cb.x0 + 0.25 * cb.width, cb.y0 + 0.3 * cb.height,
                                     cb.x1 - 0.25 * cb.width, cb.y1 - 0.3 * cb.height)
                if r.intersects(inner) and not r.contains(pymupdf.Point(c.cx, c.cy)):
                    r |= cb
                    grew = True
        regions = merge_rects(regions)
        if not grew:
            break
    return regions, emblem


# ----------------------------------------------------------------------------------------------------------------------
# text segments
class Segment:
    def __init__(self, first):
        self.chars = [first]
        self.host = first           # character that sets the baseline and size
        self.end = first.x1         # right edge of the text so far

    @property
    def x0(self):
        return self.chars[0].x0

    @property
    def x1(self):
        return self.end


def space_width(c):
    face, bold, italic = font_style(c)
    return METRICS.width(" ", face, bold, italic, c.size) or 0.278 * c.size


def gap_kind(gap, before):
    """Space between two characters of one line: none, normal (a plain space), wide (a space widened by letter
    spacing) or break (start a new text box: a thin space, which no renderer narrows reliably, or a column gap)."""
    em = before.size
    if gap < 0.1 * em:
        return "none"
    sw = space_width(before)
    if abs(gap - sw) <= 0.04 * em:
        return "normal"
    if sw < gap < 0.8 * em:
        return "wide"
    return "break"


def build_segments(chars):
    """Text boxes: runs of characters on one baseline, in one face, joined by plain or wide spaces."""
    segs, cur = [], None
    for c in chars:                                     # content-stream order = TeX's reading order
        if cur is not None and c.lig:
            cur.chars.append(c)
            continue
        if cur is not None:
            h = cur.host
            gap = c.x0 - cur.end
            # one baseline per text box: sub- and superscripts get boxes of their own, placed exactly (inline
            # baseline shifts are drawn at renderer-dependent sizes, which would move the rest of the line)
            ok = (c.dir == h.dir and abs(c.y - h.y) <= 0.3 and gap >= -0.15 * h.size
                  and 0.92 * h.size <= c.size <= 1.08 * h.size and font_style(c)[0] == font_style(h)[0]
                  and gap_kind(gap, cur.chars[-1]) != "break")
            if ok:
                cur.chars.append(c)
                cur.end = max(cur.end, c.x1)
                continue
        cur = Segment(c)
        segs.append(cur)
    return segs


def run_key(c):
    face, bold, italic = font_style(c)
    return (face, bold, italic, tuple(round(v, 3) for v in c.color), c.cls == "sc", round(c.size, 2))


def emu(pt_pdf, scale):
    return int(round(pt_pdf * scale))


def segment_runs(seg):
    """[{key, text, start, space}] -- consecutive runs; each run's text ends where the next run starts."""
    runs, end, prev = [], None, None
    for c in seg.chars:
        if c.lig:
            runs[-1]["text"] += display_char(c)
            continue
        key = run_key(c)
        kind = "none" if end is None else gap_kind(c.x0 - end, prev)
        if kind == "normal":
            runs[-1]["text"] += " "
        elif kind == "wide":
            runs.append({"key": runs[-1]["key"], "text": " ", "start": end, "space": True})
        if runs and runs[-1]["key"] == key and not runs[-1]["space"]:
            runs[-1]["text"] += display_char(c)
        else:
            runs.append({"key": key, "text": display_char(c), "start": c.x0, "space": False})
        end = c.x1 if end is None else max(end, c.x1)
        prev = c
    for i, r in enumerate(runs):
        r["target"] = (runs[i + 1]["start"] if i + 1 < len(runs) else seg.end) - r["start"]
    return runs


def add_segment(slide, seg, scale, name=None, shape=None):
    """Text box for one segment; scale = EMU per PDF point."""
    pt_scale = scale / 12700.0                       # PowerPoint points per PDF point
    h = seg.host
    left = seg.x0
    top = h.y - ASCENT * h.size
    if all(c.u == "∗" for c in seg.chars):
        top += 0.30 * h.size                         # Arial '*' sits near the cap height, TeX's on the math axis
    width = max(seg.x1 - seg.x0, 1.0) + 0.15 * h.size
    height = (ASCENT + DESCENT) * h.size
    if shape is None:
        shape = slide.shapes.add_textbox(Emu(emu(left, scale)), Emu(emu(top, scale)),
                                         Emu(emu(width, scale)), Emu(emu(height, scale)))
    else:
        shape.left, shape.top = Emu(emu(left, scale)), Emu(emu(top, scale))
        shape.width, shape.height = Emu(emu(width, scale)), Emu(emu(height, scale))
    if name:
        shape.name = name
    tf = shape.text_frame
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = 1.0
    p.space_before = p.space_after = Pt(0)
    for r in list(p.runs):
        r._r.getparent().remove(r._r)

    for r in segment_runs(seg):
        face, bold, italic, color, sc, size = r["key"]
        run = p.add_run()
        rpr = run._r.get_or_add_rPr()
        run.text = r["text"]
        _style(run, rpr, face, bold, italic, color, sc and not r["space"], 0, size, pt_scale)
        # letter spacing: the run ends exactly where the next one starts in the PDF
        if sc and not r["space"]:
            rendered = _smallcaps_width(r["text"], face, bold, italic, size)
        else:
            rendered = METRICS.width(r["text"], face, bold, italic, size)
        if rendered is not None:
            _spacing(rpr, (r["target"] - rendered) / len(r["text"]) * pt_scale)
    return shape


def _smallcaps_width(text, face, bold, italic, size):
    w = 0.0
    for ch in text:
        if ch.islower():
            cw = METRICS.width(ch.upper(), face, bold, italic, size * SMALLCAPS_SCALE)
        else:
            cw = METRICS.width(ch, face, bold, italic, size)
        if cw is None:
            return None
        w += cw
    return w


def _style(run, rpr, face, bold, italic, color, smallcaps, shift, size, pt_scale):
    f = run.font
    f.name = face
    rpr.set("sz", str(int(round(size * pt_scale * 100))))      # exact size, in hundredths of a point
    f.bold = bold
    f.italic = italic
    f.color.rgb = RGBColor(*[max(0, min(255, round(v * 255))) for v in color])
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", face)
    if smallcaps:
        rpr.set("cap", "small")
    if shift:
        rpr.set("baseline", str(int(shift * 1000)))
    rpr.set("lang", "en-US")
    rpr.set("kern", "0")            # pair kerning at every size (as TeX); letter spacing does the rest of the fitting


def _spacing(rpr, pts):
    v = int(round(pts * 100))
    if v:
        rpr.set("spc", str(max(-400000, min(400000, v))))


# ----------------------------------------------------------------------------------------------------------------------
# title
def title_segment(segs, page_h):
    cand = [s for s in segs if font_style(s.host)[1] and s.host.dir == (1.0, 0.0)]
    if not cand:
        return None
    top = [s for s in cand if s.host.y < 0.14 * page_h]
    pool = top or [s for s in cand if s.host.y < 0.6 * page_h]
    if not pool:
        return None
    biggest = max(round(s.host.size, 1) for s in pool)
    if biggest < 11:
        return None
    best = [s for s in pool if round(s.host.size, 1) == biggest]
    return min(best, key=lambda s: (s.host.y, s.x0))


def segment_text(seg):
    out, end = [], None
    for c in seg.chars:
        if end is not None and not c.lig and c.x0 - end > 0.1 * seg.host.size:
            out.append(" ")
        out.append(display_char(c))
        end = c.x1 if end is None else max(end, c.x1)
    return "".join(out)


def title_layout(prs):
    for layout in prs.slide_layouts:
        if layout.name == "Title Only":
            return layout
    return prs.slide_layouts[5]


def set_title(slide, text, rect_emu, invisible=False):
    """Fill the title placeholder; invisible=True keeps it over the picture with fully transparent text."""
    ph = slide.shapes.title
    if ph is None:
        return None
    ph.left, ph.top, ph.width, ph.height = (Emu(v) for v in rect_emu)
    tf = ph.text_frame
    tf.text = text
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if invisible:
        for p in tf.paragraphs:
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.size = Pt(20)
                r.font.color.rgb = RGBColor(255, 255, 255)
                sf = r.font._rPr.find(qn("a:solidFill"))
                clr = sf.find(qn("a:srgbClr"))
                etree.SubElement(clr, qn("a:alpha")).set("val", "0")
    return ph


# ----------------------------------------------------------------------------------------------------------------------
def _send_to_back(slide, shape):
    tree = slide.shapes._spTree
    tree.remove(shape._element)
    tree.insert(2, shape._element)          # after nvGrpSpPr and grpSpPr


def render(page, zoom, clip=None):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def png_bytes(img, palette=False):
    buf = io.BytesIO()
    if palette:
        img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    img.save(buf, "PNG", optimize=True)
    buf.seek(0)
    return buf


def textless_page(real, pno):
    """A copy of the page without any text (rules, drawings and pictures stay)."""
    tmp = pymupdf.open()
    tmp.insert_pdf(real, from_page=pno, to_page=pno)
    pg = tmp[0]
    pg.add_redact_annot(pg.rect, fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                        text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    return tmp, pg


def parse_pages(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a) - 1, int(b or a)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="")
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    ap.add_argument("--zoom", type=float, default=3840 / 453.543)   # 3840 px across the slide
    ap.add_argument("--exact-zoom", type=float, default=2560 / 453.543)
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    real, marked = pymupdf.open(REAL_PDF), pymupdf.open(MARKED_PDF)
    if real.page_count != marked.page_count:
        raise SystemExit("main.pdf and main_marked.pdf differ in page count; rebuild both")
    pw, ph = real[0].rect.width, real[0].rect.height
    scale = SLIDE_W / pw                                  # EMU per PDF point
    pages = parse_pages(args.pages, real.page_count)

    ed, ex = Presentation(), Presentation()
    for prs in (ed, ex):
        prs.slide_width, prs.slide_height = Emu(SLIDE_W), Emu(SLIDE_H)
    report = []

    for pno in pages:
        page = real[pno]
        chars = page_chars(page, marked[pno])
        regions, emblem = picture_regions(real, page, chars)
        stray = [c for c in chars if any(c.font.startswith(f) for f in FIGURE_TEXT_FONTS)
                 and not any(r.contains(pymupdf.Point(c.cx, c.cy)) for r in regions)]
        text_chars = [c for c in chars if not any(r.contains(pymupdf.Point(c.cx, c.cy)) for r in regions)]
        segs = build_segments(text_chars)
        tseg = title_segment(segs, ph)

        full = render(page, args.zoom)
        tmp, bare = textless_page(real, pno)
        bg = render(bare, args.zoom)
        tmp.close()
        z = args.zoom
        for r in regions:                               # pictures sit in their own shapes, not in the background
            box = (int(r.x0 * z), int(r.y0 * z), int(round(r.x1 * z)), int(round(r.y1 * z)))
            bg.paste((255, 255, 255), box)

        # editable slide
        s = ed.slides.add_slide(title_layout(ed))
        pic = s.shapes.add_picture(png_bytes(bg, palette=True), 0, 0, Emu(SLIDE_W), Emu(SLIDE_H))
        pic.name = "Background (rules, lines, emblem)"
        _send_to_back(s, pic)
        for k, r in enumerate(regions):
            crop = full.crop((int(r.x0 * z), int(r.y0 * z), int(round(r.x1 * z)), int(round(r.y1 * z))))
            sh = s.shapes.add_picture(png_bytes(crop), Emu(emu(r.x0, scale)), Emu(emu(r.y0, scale)),
                                      Emu(emu(r.width, scale)), Emu(emu(r.height, scale)))
            sh.name = f"Picture {k + 1}"
        title_shape = s.shapes.title
        for k, seg in enumerate(segs):
            if seg is tseg and title_shape is not None:
                add_segment(s, seg, scale, shape=title_shape)
                # room to the emblem: a title never wraps, whatever the renderer's glyph widths
                title_shape.width = Emu(max(title_shape.width, emu(pw - 28.35 - 30 - seg.x0, scale)))
            else:
                add_segment(s, seg, scale, name=f"Text {k + 1}")
        if tseg is None and title_shape is not None:
            title_shape._element.getparent().remove(title_shape._element)

        # exact slide
        x = ex.slides.add_slide(title_layout(ex))
        img = render(page, args.exact_zoom)
        xp = x.shapes.add_picture(png_bytes(img, palette=True), 0, 0, Emu(SLIDE_W), Emu(SLIDE_H))
        xp.name = f"Slide {pno + 1}"
        _send_to_back(x, xp)
        if tseg is not None:
            t = tseg
            rect = (emu(t.x0, scale), emu(t.host.y - ASCENT * t.host.size, scale),
                    emu(t.x1 - t.x0, scale), emu((ASCENT + DESCENT) * t.host.size, scale))
            set_title(x, segment_text(tseg), rect, invisible=True)
        elif x.shapes.title is not None:
            x.shapes.title._element.getparent().remove(x.shapes.title._element)

        report.append(f"p{pno + 1}: {len(segs)} text boxes, {len(regions)} pictures, title="
                      f"{segment_text(tseg)[:60] if tseg else '-'!r}" + (f", STRAY figure text {len(stray)}" if stray else ""))
        print(report[-1], flush=True)

    os.makedirs(args.out, exist_ok=True)
    ed.save(os.path.join(args.out, "IWO_NTU_presentation_editable.pptx"))
    ex.save(os.path.join(args.out, "IWO_NTU_presentation_exact.pptx"))
    if args.report:
        open(args.report, "w").write("\n".join(report) + "\n")


if __name__ == "__main__":
    sys.exit(main())
