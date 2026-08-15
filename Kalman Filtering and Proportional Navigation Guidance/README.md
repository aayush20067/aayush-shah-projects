# Kalman Filtering and Proportional Navigation Guidance

AE641 (Introduction to Navigation and Guidance), IIT Bombay
Coursework exercises, not a full project.

Two guidance and estimation problems worked through by hand and then simulated in MATLAB.

## Extended Kalman filtering for state estimation

A scalar random-walk state observed through two noisy measurement channels, one of which has
a time-varying observation model and heavily time-varying noise. Since the system is linear
time-varying, the EKF reduces to the standard Kalman filter here.

I derived the five filter equations for this system — state prediction, covariance
prediction, Kalman gain, state update, covariance update — and implemented them to compare
the estimate against ground truth over 200 time steps.

The estimate tracks the true state closely for most of the run. Where it drifts, it's during
sharp state changes or when the second channel's noise variance spikes, which is what you'd
expect when the measurement carries less information.

## Proportional navigation guidance

A missile–target intercept with an initial heading error. Given a target at 10 km closing at
200 m/s on a 60° heading and a missile at 400 m/s, I solved for the launch angle that puts
the missile on a collision course (40.66°), then computed the range and time-to-go after the
heading error is introduced.

From there I applied proportional navigation with $N = 3$ to work out the lateral
acceleration demand over the engagement and simulated both trajectories to intercept.

The acceleration profile shows the expected PPN behaviour: high demand early to correct the
initial heading error, tailing off as the missile settles onto the collision course. The
simulated intercept overshoots slightly, which the write-up attributes to the small-angle
approximation used in the acceleration formula and to treating time-to-go as constant.

## Files

- `group_10_report.pdf` — handwritten derivations, plots, observations and the MATLAB source
- `Project641.mlx` — MATLAB live script for both problems
- `FInal_video_missile_target.mov` — animation of the intercept

## Tools

MATLAB.
