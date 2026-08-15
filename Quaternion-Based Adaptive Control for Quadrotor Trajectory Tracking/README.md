# Quaternion-Based Adaptive Control for Quadrotor Trajectory Tracking

SC617 (Adaptive Control Theory), IIT Bombay — sole author

An adaptive controller that makes a quadrotor track a trajectory without knowing its own
mass or inertia matrix. Based on the method in Pliego-Jiménez (2021).

## The problem

A quadrotor controller normally needs the vehicle's mass and inertia matrix. In practice you
often don't have good values for either — payload changes, the CAD estimate is wrong,
components shift. An adaptive controller estimates those parameters online while it flies,
and you prove the tracking error still converges.

Two things make this version worth doing. It uses unit quaternions rather than Euler angles,
which removes the attitude singularities and keeps the controller well-defined through any
orientation. And it proves stability with a single Lyapunov function covering the full
coupled translational and rotational dynamics, instead of treating the two loops separately
and hoping the cascade holds.

## What I did

Designed the controller in two loops: an outer position controller producing a desired
thrust and attitude, and an inner attitude controller, with adaptive laws for the unknown
mass and inertia and a stability proof for the whole thing.

The second part of the report extends this to the case where the control allocation matrix
is also unknown, which is the more realistic situation when you don't have a good model of
how motor commands map to thrust and torque. That needed its own adaptive law and its own
stability argument.

Simulations are in the Simulink models.

## Files

- `SC617_Final_Report.pdf` — derivation, adaptive laws, stability proofs, simulation results
- `SC617_Final.slx`, `untitled5.slx` — Simulink models
- `Papers/` — the reference literature I worked from, including the Pliego-Jiménez paper the
  method comes from

## Tools

MATLAB, Simulink, Lyapunov stability theory.
