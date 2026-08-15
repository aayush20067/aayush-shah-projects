# Strain Based Analysis of Multi-Hole Interaction in Acrylic using DIC

ME218 (Solid Mechanics Lab), IIT Bombay

Holes in a loaded component concentrate strain, and that concentration can start a crack well
before nominal stress reaches the material limit. When there's more than one hole they
interact: each one changes the strain in the ligament between them and modifies the
concentration around its neighbours. This project measured that interaction experimentally
using Digital Image Correlation.

I did the DIC post-processing, ROI extraction and analysis, and wrote the report. It was a
five-person group project and the full contribution breakdown is in section (g) of the PDF.

## Setup

Eight specimen configurations, all cast acrylic (PMMA), 4 mm sheet, laser cut at the IIT
Bombay Microfactory to ASTM D638 Type I dog-bone geometry:

| Config | Holes | Arrangement |
|---|---|---|
| NH | 0 | baseline, no hole |
| 1H | 1 | single hole |
| 2H2, 2H4 | 2 | collinear, $s/d$ = 2 and 4 |
| 3H2, 3H4 | 3 | collinear, $s/d$ = 2 and 4 |
| 3H2S, 3H4S | 3 | staggered, $s/d$ = 2 and 4 |

Each specimen got a white base coat and a black speckle pattern for DIC tracking, then was
loaded uniaxially in tension on a UTM under displacement control with images captured
continuously.

## Analysis

Image sequences were processed in MatchID. Full-field strain maps weren't available at the
subset level for these specimens, so instead I defined regions of interest manually and
recorded the average strain in each: annular zones around every hole, the ligaments between
adjacent holes (vertical L1, diagonal L2), and far-field zones.

Two normalised metrics, both referenced to each specimen's own far-field strain so that
differences in load level between specimens drop out:

$$K_\varepsilon = \frac{\varepsilon_{\text{ann}}}{\varepsilon_{\text{FF}}}, \qquad I = \frac{\varepsilon_{\text{lig}}}{\varepsilon_{\text{FF}}}$$

## Results

**Closer holes interact much more strongly.** For the three-hole collinear case, normalised
ligament strain nearly doubled going from $s/d = 4$ to $s/d = 2$ ($I$: 0.395 → 0.757).

**The middle hole gets shielded.** In the collinear three-hole array at $s/d = 2$, the centre
hole showed *lower* annular concentration ($K_\varepsilon = 0.711$) than the outer holes
($K_\varepsilon = 1.238$). Its neighbours take the load. This matches classical analytical
predictions.

**Staggering helps.** Offsetting the centre hole laterally cut vertical ligament interaction
by about 24% compared to the collinear case at the same spacing.

The practical read is that a small geometric change — offsetting one hole — redistributes
load paths enough to meaningfully reduce ligament strain, which is useful when designing
perforated components.

## Limitations

Four-hole specimens were fabricated and tested but the DIC analysis couldn't be completed
before submission because the analysis setup wasn't available. Only one specimen per
configuration was tested, so genuine geometric effects and experimental scatter can't be
fully separated. FE simulation would be the obvious quantitative check on these trends.

## Files

- `ME218_Report.pdf` — full report: method, all eight configurations, results table, discussion

## Tools

MatchID (DIC), universal testing machine, laser-cut PMMA specimens, speckle patterning.
