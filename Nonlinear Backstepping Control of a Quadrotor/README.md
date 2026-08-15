# Nonlinear Control of a Quadrotor using Backstepping and Lyapunov Stability

SC617 (Adaptive Control Theory), IIT Bombay — sole author

A second controller for the same quadrotor platform, designed a different way. Where the
[adaptive controller](../Quaternion-Based%20Adaptive%20Control%20for%20Quadrotor%20Trajectory%20Tracking)
handles unknown parameters, this one assumes the model is known and goes after the
nonlinearity directly using recursive backstepping.

## Structure

The controller splits into three cascaded subsystems:

- attitude controller
- altitude controller
- position controller

Backstepping builds these up recursively. You start from the innermost dynamics, pick a
virtual control that stabilises it with a Lyapunov function, then step outward treating the
previous stage's virtual control as a reference to be tracked, carrying the Lyapunov function
along. By the time you reach the outer loop you have a stability proof for the whole cascade
rather than for each loop in isolation.

## Model parameters

```
m  = 1.336 kg
g  = 9.80665 m/s²
Ix = 0.0259 kg·m²
Iy = 0.0260 kg·m²
Iz = 0.0397 kg·m²
```

Controller gains: $k_1 = k_2 = k_3 = k_4 = 2.5$, $k_5 = k_6 = 2$, $k_7 = 2.2$, $k_8 = 0.5$,
$k_9 = k_{11} = 0.4$.

## Simulations

Two cases:

1. **Set-point stabilisation** — driving the quadrotor to a fixed position and holding it.
2. **Circular trajectory tracking** — following a continuously varying reference, which is
   the harder test since the error dynamics never settle.

## Files

- `SC617_Backstepping_Report.pdf` — full derivation, Lyapunov analysis, both simulation cases

## Tools

MATLAB, Simulink, Lyapunov stability theory.
