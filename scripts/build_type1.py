"""Build the Type 1 fonts and the pdfLaTeX support files from the OpenType fonts.

    python scripts/build_type1.py

Run `python source/build.py` first. Needs FontForge (`fontforge` on PATH),
LCDF Typetools (`otftotfm`, `t1lint`) and a TeX installation that provides
`ec.enc` (found with `kpsewhich`). Writes:

  fonts/type1/   GaussianModern-*.pfb / .afm / .pfm   (standalone Type 1)
  texmf/         a TDS tree for pdfLaTeX, dvips and plain TeX
"""
import os, re, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OTF = ROOT / 'fonts' / 'otf'
T1 = ROOT / 'fonts' / 'type1'
TEXMF = ROOT / 'texmf'
VERSION = '0.107'
EPOCH = '1792281600'   # 2026-10-18 00:00 UTC, so rebuilt files carry a fixed date
STYLES = [('Regular', 'regular', 'm', 'n'), ('Italic', 'italic', 'm', 'it'),
          ('Semibold', 'semibold', 'sb', 'n'), ('SemiboldItalic', 'semibolditalic', 'sb', 'it')]

FF_SCRIPT = r'''
import fontforge, sys
f = fontforge.open(sys.argv[1])
f.version = sys.argv[3]
f.encoding = 'AdobeStandard'
f.selection.all(); f.autoHint()
f.generate(sys.argv[2] + '.pfb', flags=('afm', 'pfm', 'round'))
'''

TDS = {
    'tfm': TEXMF / 'fonts/tfm/public/gaussianmodern',
    'vf': TEXMF / 'fonts/vf/public/gaussianmodern',
    'enc': TEXMF / 'fonts/enc/dvips/gaussianmodern',
    'map': TEXMF / 'fonts/map/dvips/gaussianmodern',
    'type1': TEXMF / 'fonts/type1/public/gaussianmodern',
    'afm': TEXMF / 'fonts/afm/public/gaussianmodern',
    'latex': TEXMF / 'tex/latex/gaussianmodern',
}


def run(cmd, **kw):
    env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH)
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, **kw)
    if r.returncode:
        raise SystemExit(f'{cmd[0]} failed:\n{r.stdout}\n{r.stderr}')
    return r


def clean_afm(path):
    """Drop FontForge's placeholder .notdef entries and fix the metrics count."""
    lines = path.read_text().splitlines()
    out, inside, chars = [], False, []
    for line in lines:
        if line.startswith('StartCharMetrics'):
            inside = True; out.append(None); continue
        if line.startswith('EndCharMetrics'):
            inside = False
            out[out.index(None)] = f'StartCharMetrics {len(chars)}'
            out.extend(chars); out.append(line); continue
        if inside:
            if '; N .notdef ;' not in line: chars.append(line)
            continue
        if line.startswith('Comment Creation Date'): continue
        out.append(line)
    path.write_text('\n'.join(out) + '\n')


def type1(ps, script):
    run(['fontforge', '-quiet', '-lang=py', '-script', script,
         str(OTF / f'{ps}.otf'), str(T1 / ps), VERSION])
    run(['t1lint', str(T1 / f'{ps}.pfb')])
    clean_afm(T1 / f'{ps}.afm')


def tex_metrics(ps, tfm, ec, tmp):
    mapfile = tmp / f'{tfm}.map'
    run(['otftotfm', '-e', ec, '-f', 'kern', '-f', 'liga', '--no-type1', '--no-updmap',
         f'--tfm-directory={TDS["tfm"]}', f'--vf-directory={TDS["vf"]}',
         f'--encoding-directory={TDS["enc"]}', f'--map-file={mapfile}',
         str(OTF / f'{ps}.otf'), tfm])
    line = next(l for l in mapfile.read_text().splitlines() if l.startswith(tfm))
    # point the map at the hinted Type 1 font instead of the OpenType file
    return re.sub(r'<[^<\s]+\.otf$', f'<{ps}.pfb', line)


FD = r'''\ProvidesFile{t1gmd.fd}[2026/10/18 v%(v)s Gaussian Modern, T1 encoding]
\DeclareFontFamily{T1}{gmd}{}
\DeclareFontShape{T1}{gmd}{m}{n}{<-> gmd-regular-t1}{}
\DeclareFontShape{T1}{gmd}{m}{it}{<-> gmd-italic-t1}{}
\DeclareFontShape{T1}{gmd}{sb}{n}{<-> gmd-semibold-t1}{}
\DeclareFontShape{T1}{gmd}{sb}{it}{<-> gmd-semibolditalic-t1}{}
\DeclareFontShape{T1}{gmd}{m}{sl}{<-> ssub * gmd/m/it}{}
\DeclareFontShape{T1}{gmd}{sb}{sl}{<-> ssub * gmd/sb/it}{}
\DeclareFontShape{T1}{gmd}{b}{n}{<-> ssub * gmd/sb/n}{}
\DeclareFontShape{T1}{gmd}{b}{it}{<-> ssub * gmd/sb/it}{}
\DeclareFontShape{T1}{gmd}{b}{sl}{<-> ssub * gmd/sb/it}{}
\DeclareFontShape{T1}{gmd}{bx}{n}{<-> ssub * gmd/sb/n}{}
\DeclareFontShape{T1}{gmd}{bx}{it}{<-> ssub * gmd/sb/it}{}
\DeclareFontShape{T1}{gmd}{bx}{sl}{<-> ssub * gmd/sb/it}{}
\endinput
'''

STY = r'''\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{gaussianmodern}[2026/10/18 v%(v)s Gaussian Modern Type 1 text fonts]
% Text fonts only. Mathematics keeps the document's math fonts.
\RequirePackage{iftex}
\ifPDFTeX
  % In PDF mode, load the map file directly so the fonts work without updmap.
  % In DVI mode, dvips needs the map installed (or dvips -u +gaussianmodern.map).
  \ifnum\pdfoutput>0 \pdfmapfile{=gaussianmodern.map}\fi
\else
  \PackageWarningNoLine{gaussianmodern}{%
    This package loads the Type 1 fonts for pdfLaTeX.\MessageBreak
    With XeLaTeX or LuaLaTeX, use fontspec and the OpenType\MessageBreak
    fonts instead (see USAGE.md)}
\fi
\RequirePackage[T1]{fontenc}
\renewcommand*{\rmdefault}{gmd}
\endinput
'''


def main():
    ec = run(['kpsewhich', 'ec.enc']).stdout.strip()
    if not ec: raise SystemExit('ec.enc not found; install TeX Live')
    for d in [T1, TEXMF]:
        if d.exists(): shutil.rmtree(d)
    T1.mkdir(parents=True)
    for d in TDS.values(): d.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t); script = tmp / 'ff.py'; script.write_text(FF_SCRIPT)
        maplines = []
        for st, low, _, _ in STYLES:
            ps = f'GaussianModern-{st}'
            type1(ps, script)
            maplines.append(tex_metrics(ps, f'gmd-{low}-t1', ec, tmp))
            for ext, d in [('pfb', 'type1'), ('afm', 'afm')]:
                shutil.copy2(T1 / f'{ps}.{ext}', TDS[d] / f'{ps}.{ext}')
            print(ps, 'done')
    (TDS['map'] / 'gaussianmodern.map').write_text(
        '% Gaussian Modern Type 1 fonts, T1 (Cork) encoding\n' + '\n'.join(sorted(set(maplines))) + '\n')
    for enc in TDS['enc'].glob('*.enc'):
        # drop otftotfm's creation date and the recorded command line (local paths)
        text = enc.read_text().split('\n% Command line:')[0].rstrip() + '\n'
        enc.write_text(''.join(l for l in text.splitlines(True)
                               if not l.startswith('% Encoding created by otftotfm')))
    (TDS['latex'] / 't1gmd.fd').write_text(FD.replace('%(v)s', VERSION))
    (TDS['latex'] / 'gaussianmodern.sty').write_text(STY.replace('%(v)s', VERSION))


if __name__ == '__main__':
    main()
