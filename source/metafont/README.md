# METAFONT sources

These programs draw a roman fitted to the type of C. F. Gauss, *Werke*, Band III
(Göttingen, 2nd printing 1876). They are the origin of Gaussian Modern's
Gauss-modelled upright shapes. The fonts themselves are built from the JSON and
UFO masters, not from these files.

| File | Contents |
| --- | --- |
| `gwr10.mf` | Parameter file, 10 pt. Every value is commented; lengths are in 1/36 pt with the x-height at 155 units. |
| `gwroman.mf` | Driver, derived from Knuth's `roman.mf`, with separate width units for capitals and figures. |
| `gwromanu.mf` | Knuth's `romanu.mf` (capitals) with Q removed, renamed as his notice requires. |
| `gwq.mf` | The Q, with a short parametrised tail. |

Build with TeX Live, which supplies `cmbase.mf` and the other unchanged Computer
Modern files:

    mf '\mode=ljfour; input gwr10'
    gftopk gwr10.600gf gwr10.600pk

The glyph programs are © Donald E. Knuth (Computer Modern), used under his terms.
See `../../THIRD-PARTY-NOTICES.md`.
