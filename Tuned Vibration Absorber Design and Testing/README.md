# Tuned Vibration Absorber — Design, Fabrication and Testing

A 2-DOF dynamic vibration absorber, built and measured against theory
ME444 (Analysis and Design of Mechanical Systems), IIT Bombay

The usual way to deal with vibration near resonance is to add damping: stiffen the
structure, add rubber mounts, apply some damping treatment. It works but it costs weight and
complexity, and at true resonance even a well-damped system can hit amplitudes you can't
live with.

A tuned absorber does something different. You couple a second spring-mass system to the
structure and tune it to the excitation frequency. It then oscillates in anti-phase and
cancels the load on the primary structure, so the primary mass barely moves. Tuned properly,
the single resonance peak splits into two with a deep anti-resonance valley between them.

I built one and measured how closely it follows the textbook.

## The rig

The primary mass was a 285 g assembly: a 12 V DC motor, an Arduino Uno and an MPU6050 IMU.
The motor provided eccentric excitation, and I swept the frequency by varying supply voltage
from 5 V to 11.5 V. The absorber mass was sized to the tuning condition and attached through
a second spring. The IMU logged acceleration and I processed it with FFT in Python.

## Results

Resonance splitting showed up clearly. The single peak became two with a distinct
anti-resonance dip between them, which is what 2-DOF theory says should happen. Amplitude
near the anti-resonance dropped as expected.

Alongside the physical rig I ran Python simulations to look at the effect of damping ratio,
mass ratio and Den Hartog optimal design, and built an MSC ADAMS model as an idealised
reference.

The prototype doesn't match the ideal exactly, and the report says why: friction,
misalignment and imperfect eccentric excitation all blunt the response. That gap between the
clean theory and a real bench setup is most of what I took away from it.

## Files

```
ME444_Report_Group13.pdf     full report — theory, fabrication, results
arduino-daq/                 firmware for MPU6050 acquisition (.ino)
data-analysis/               Python analysis — FFT, damping and mass ratio studies,
                             Den Hartog comparison, time and frequency domain plots
absorber-tests/              raw sweep data with and without the absorber fitted,
                             RMS and peak-to-peak amplitude vs drive voltage
```

## Tools

Arduino Uno, MPU6050 IMU, Python (NumPy, SciPy, Matplotlib), FFT, MSC ADAMS.
