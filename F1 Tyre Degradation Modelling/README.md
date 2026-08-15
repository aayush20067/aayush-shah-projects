# Modelling Tyre Degradation in Formula 1

A two-stage machine learning pipeline on real F1 timing and telemetry data
ME228 (Applied Data Science and Machine Learning), IIT Bombay

Tyre degradation drives most of the strategy calls in F1 — when to pit, which compound, how
long to run a stint. It's also hard to measure. The thing you can observe is lap time, and
lap time is noisy for reasons that have nothing to do with the tyres: traffic, yellow flags,
DRS gaps, driver mistakes. A slow lap might be genuine wear or it might be a driver stuck
behind someone.

Pulling the degradation signal out of that noise is the problem this project is about.

## Approach

What I'm actually modelling is ΔT: how much slower a lap is than the best lap that driver
managed on the same set of tyres in that stint. If ΔT is positive and climbing over lap
number, that's tyre wear.

**Stage 1, clean lap classification.** An MLP gives each lap a probability of being a clean
lap, meaning the driver was in free air and not affected by traffic, flags or anything odd. I
built two versions of the labels: a simple gap-based one, and a second set derived from
240 Hz car telemetry.

**Stage 2, degradation learning.** Those probabilities become sample weights for the second
stage, where Ridge regression, Gradient Boosting, Random Forest and an MLP regressor learn
ΔT from tyre age, compound, track and lap position.

## Data

All of it came through [FastF1](https://github.com/theOehrly/Fast-F1), which reads the
official F1 timing feed.

- Stage 1 (V1) and all the regression models used the full 2024 season, all 22 races.
- Stage 1 (V2), the telemetry-based version, used six races (Bahrain, Saudi Arabia,
  Australia, Japan, China, Miami). Loading full 240 Hz telemetry is heavy enough that all 22
  wasn't practical.
- Out-of-sample testing was on Bahrain 2023, an unseen race from a different season.

## What I found

The simple gap-based clean lap classifier does improve the regression, but not by much and
it has obvious limits. Telemetry-derived features gave noticeably better lap labels.

The bigger finding was about generalisation. My first model used only stint position and
compound, and on an unseen race it was terrible — strongly negative R². Degradation is very
track-dependent and the model had no idea what track it was looking at. Adding Race as a
categorical feature and retraining across 20–25 races improved it a lot.

But testing across seasons (2024 → 2023) it still fell over. Race encoding is only a proxy.
It memorises which tracks are harsh instead of learning why they're harsh, and once you
change season the cars, setups and conditions have all shifted underneath it. To actually
generalise you'd need physically meaningful track features — surface roughness, corner
loading, energy input — rather than a categorical label.

That last one is a negative result and it's the most useful thing in the project.

## Files

- `ME228_Report.pdf` — full report, pipeline, all four model architectures under both label
  sets, evaluation
- `f1_tire_degradation.ipynb` — the implementation: data loading, cleaning, feature
  engineering, both MLP stages, regression, plots
- `ME228_Presentation.pdf` — final presentation
- `ME228_Progress_Report.pdf` — mid-project progress report
- `PIPELINE_NOTES.md` — my working notes, in the order I built things

## Tools

Python, FastF1, scikit-learn, pandas, NumPy, Matplotlib.
