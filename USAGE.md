# Using Gaussian Modern

Gaussian Modern comes in three formats. Pick the one that suits your software.

| You are using | Use these files |
| --- | --- |
| Word, LibreOffice, Pages, InDesign, design tools, the operating system | `fonts/otf/` (or `fonts/ttf/`) |
| Web pages | `fonts/ttf/`, converted to WOFF2 (see below) |
| XeLaTeX or LuaLaTeX | `fonts/otf/`, including **Gaussian Modern Math** |
| pdfLaTeX, `latex` + dvips, plain TeX | the TeX tree in `texmf/` (Type 1) |
| PostScript, Ghostscript, older applications | `fonts/type1/` (PFB + AFM + PFM) |

The text family has four styles: **Regular**, *Italic*, **Semibold** and ***Semibold Italic***.
There is no separate bold; Semibold is the bold. **Gaussian Modern Math** is the companion for
mathematics and exists only as OpenType.

## 1. Installing on a computer

Install **either** the OTF **or** the TTF files, not both. Two copies of the same family
produce duplicate menu entries and can confuse applications.

- **Windows:** select the five `.otf` files, right-click, *Install* (or *Install for all users*).
- **macOS:** double-click each `.otf` file and choose *Install Font* in Font Book.
- **Linux:** copy the files to `~/.local/share/fonts/` and run `fc-cache -f`.

OTF and TTF hold the same designs. OTF keeps the original cubic curves; TTF converts them
to quadratic curves and suits some older Windows software. Neither format is hinted yet, so
text below about 12 px on Windows can look uneven; at print sizes and on high-resolution
screens this does not matter.

### In word processors

- **Kerning** is on by default in LibreOffice, Pages and most design applications. In Word, turn
  it on under *Font › Advanced › Kerning for fonts*.
- **Ligatures** (ff, fi, fl, ffi, ffl) appear automatically in LibreOffice and Pages. In Word,
  choose *Font › Advanced › Ligatures › Standard Only*.
- **Figures** are lining and all the same width, so columns of numbers line up.
- **Equations:** Gaussian Modern Math is built and tested for XeLaTeX and LuaLaTeX. Word's and
  LibreOffice's equation editors have not been tested with it.

## 2. On the web

Convert the TTF files to WOFF2 with FontTools (`pip install fonttools brotli`):

```sh
fonttools ttLib.woff2 compress -o GaussianModern-Regular.woff2 fonts/ttf/GaussianModern-Regular.ttf
```

Repeat for the other styles, then:

```css
@font-face {
  font-family: "Gaussian Modern";
  src: url("GaussianModern-Regular.woff2") format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Gaussian Modern";
  src: url("GaussianModern-Italic.woff2") format("woff2");
  font-weight: 400; font-style: italic; font-display: swap;
}
@font-face {
  font-family: "Gaussian Modern";
  src: url("GaussianModern-Semibold.woff2") format("woff2");
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Gaussian Modern";
  src: url("GaussianModern-SemiboldItalic.woff2") format("woff2");
  font-weight: 600; font-style: italic; font-display: swap;
}
body { font-family: "Gaussian Modern", Georgia, serif; }
strong, b { font-weight: 600; }
```

Setting `strong, b { font-weight: 600; }` makes bold text use Semibold instead of a
browser-synthesised bold. Kerning and ligatures are on by default in browsers.

## 3. XeLaTeX and LuaLaTeX (OpenType, with mathematics)

This is the most complete way to use the family: text and mathematics match, and every
character is available.

```latex
\documentclass{article}
\usepackage{unicode-math}            % loads fontspec
\setmainfont{GaussianModern-Regular.otf}[
  Path           = fonts/otf/,       % omit Path if the fonts are installed
  ItalicFont     = GaussianModern-Italic.otf,
  BoldFont       = GaussianModern-Semibold.otf,
  BoldItalicFont = GaussianModern-SemiboldItalic.otf]
\setmathfont{GaussianModernMath-Regular.otf}[Path = fonts/otf/]
\begin{document}
For a smooth $f\colon\mathbb{R}\to\mathbb{R}$,
\[ \int_0^1 x^2\,dx = \frac13 . \]
\end{document}
```

Compile with `xelatex` or `lualatex`. With installed fonts, write
`\setmainfont{Gaussian Modern}` and `\setmathfont{Gaussian Modern Math}`.

Gaussian Modern Math has no fraktur, sans-serif or typewriter maths alphabets. If you need
them, take just those alphabets from another maths font:

```latex
\setmathfont{latinmodern-math.otf}[range={\mathfrak/{latin,Latin},
                                           \mathsfup/{latin,Latin},
                                           \mathtt/{latin,Latin}}]
```

Put this line after the main `\setmathfont`.

## 4. pdfLaTeX, dvips and plain TeX (Type 1)

The `texmf/` folder is a standard TeX directory tree with the metrics (TFM, VF), encoding,
map file and Type 1 fonts, plus a LaTeX package. It covers the four text styles in the T1
(Cork) encoding, with kerning and ligatures.

### Install

Copy the **contents** of `texmf/` into your personal TeX tree. Find where that is with:

```sh
kpsewhich -var-value TEXMFHOME
```

(usually `~/texmf` on Linux, `~/Library/texmf` on macOS, `%USERPROFILE%\texmf` on Windows).
Then enable the map file, so that dvips and DVI previewers find the fonts:

```sh
updmap-user --enable Map=gaussianmodern.map        # TeX Live
```

On MiKTeX, register `texmf/` as a root directory in the MiKTeX Console (*Settings ›
Directories*), then run `initexmf --edit-config-file updmap`, add the line
`Map gaussianmodern.map`, save, and run `initexmf --mkmaps`.

pdfLaTeX also works without the map step: the package loads the map itself. To try the
fonts without installing anything, point TeX at the folder for one run:

```sh
TEXMFHOME=/path/to/gaussian-modern/texmf pdflatex mydocument.tex
```

### Use in LaTeX

```latex
\documentclass{article}
\usepackage{gaussianmodern}   % also selects T1 font encoding
\begin{document}
Straße, façade, Ångström: kerning and ligatures work as usual.
\textit{Italic}, \textbf{Semibold}, \textbf{\textit{Semibold Italic}}.
\end{document}
```

- `\textbf` uses Semibold; `\textsl` uses the italic, since there is no slanted style.
- There are no small capitals; `\textsc` falls back to the regular style with a warning.
- **Mathematics** keeps the document's maths fonts (Computer Modern by default, which suits
  the design's Computer Modern ancestry). For maths in Gaussian Modern, use XeLaTeX or LuaLaTeX.
- With `latex` + `dvips`, run `updmap-user` once as above, or use
  `dvips -u +gaussianmodern.map mydocument.dvi`.

### Plain TeX

```tex
\pdfmapfile{=gaussianmodern.map}
\font\gm=gmd-regular-t1 at 11pt  \font\gmi=gmd-italic-t1 at 11pt
\gm Text in Gaussian Modern, {\gmi italic}.
\bye
```

The TFM names are `gmd-regular-t1`, `gmd-italic-t1`, `gmd-semibold-t1` and
`gmd-semibolditalic-t1`. Plain TeX's accent macros assume the older OT1 layout, so for
accented text in the T1 encoding use LaTeX.

## 5. Type 1 fonts on their own (PostScript and older software)

`fonts/type1/` holds each style as:

- `.pfb`: the outlines (Type 1, with FontForge autohinting), Adobe Standard Encoding;
- `.afm`: metrics with kerning pairs and ligatures, for applications and TeX tools;
- `.pfm`: metrics for Windows.

**Ghostscript** finds the fonts by name when given the folder:

```sh
gs -sFONTPATH=fonts/type1 -sDEVICE=pdfwrite -o out.pdf myfile.ps
```

**PostScript** programs call them by their PostScript names (`GaussianModern-Regular`,
`GaussianModern-Italic`, `GaussianModern-Semibold`, `GaussianModern-SemiboldItalic`). The fonts
use Adobe Standard Encoding, which has no accented letters. Reencode to ISO Latin-1 for them:

```postscript
/reencode { exch findfont dup length dict begin
    { 1 index /FID ne { def } { pop pop } ifelse } forall
    /Encoding exch def currentdict end definefont pop } def
/GaussianModern-Regular-L1 /GaussianModern-Regular ISOLatin1Encoding reencode
/GaussianModern-Regular-L1 findfont 12 scalefont setfont
72 700 moveto (Stra\337e, na\357ve, fa\347ade) show
```

**Applications.** Type 1 is a legacy format:

- Adobe ended Type 1 support in its applications in January 2023 (Photoshop 23.0,
  Illustrator 27.3, InDesign 18.2 and later). Older versions still use Type 1, and PDFs with
  embedded Type 1 fonts keep displaying and printing.
- Windows still installs Type 1 fonts (right-click the `.pfm` file with the `.pfb` beside it,
  then *Install*). Microsoft has deprecated the format and plans to remove support in a
  future release.
- For current software, use the OTF files instead.

## 6. Character set

**Languages.** Each text style fully covers English, German, French, Spanish, Portuguese,
Italian, Dutch, the Scandinavian languages, Icelandic, Estonian, Polish, Czech, Slovak,
Hungarian, Slovene and Turkish. Romanian works with the older cedilla forms (ş ţ) but not the
comma-below forms (ș ț). Not yet covered: Croatian/Bosnian/Serbian Latin capital Đ, Latvian,
Lithuanian, Maltese, Welsh (ŵ ŷ) and Esperanto.

**Symbols.** Common punctuation, quotes, dashes, guillemets, €, £, ¥, ™, ©, ®, ‰, and 13
combining accents. Missing from the text fonts are the single-character ellipsis (…, which
only the maths font has), the soft hyphen, small capitals and old-style figures. Type three
full stops for an ellipsis, or use `\dots` in TeX.

**Mathematics.** Gaussian Modern Math covers the usual operators, relations, arrows, set and
calculus symbols, upright and italic Greek, italic, bold and bold italic Latin alphabets,
blackboard-bold and script **capitals**, large delimiters and extensible accents, the dots
… ⋯ ⋮ ⋱, divides ∣, the long double arrows ⟸ ⟹, and extensible over- and underbraces
⏞ ⏟. Other long arrows (⟵ ⟶ ⟷ ⟺) are not yet included. It has no
lowercase blackboard-bold or script letters, no bold Greek, and no fraktur, sans-serif or
typewriter alphabets (see the `range` example in section 3).

## 7. Troubleshooting

| Problem | Fix |
| --- | --- |
| The family appears twice in font menus | Both OTF and TTF are installed; remove one set. |
| New fonts don't appear on Linux | Run `fc-cache -f`, then restart the application. |
| `File 'gaussianmodern.sty' not found`, or a `not loadable` font error | The `texmf/` contents aren't in your TeX tree; check with `kpsewhich gaussianmodern.sty` and `kpsewhich gmd-regular-t1.tfm`. |
| dvips or a DVI previewer shows bitmaps or wrong fonts | Run `updmap-user --enable Map=gaussianmodern.map`. |
| `gaussianmodern` warns under XeLaTeX or LuaLaTeX | Use `fontspec` with the OTF files there (section 3). |
| Small text looks uneven on Windows | The OpenType files are not hinted yet; use 12 px or larger on screen. |
