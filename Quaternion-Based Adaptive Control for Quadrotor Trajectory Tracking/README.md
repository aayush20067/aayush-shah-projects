# Quaternion-Based Adaptive Control for Quadrotor Trajectory Tracking

SC617 (Adaptive Control Theory), IIT Bombay — sole author

An adaptive controller that makes a quadrotor track a trajectory without knowing its own
mass or inertia matrix. Based on the method in Pliego-Jiménez (2021).

## The problem

A quadrotor controller normally needs the vehicle's mass $m$ and inertia matrix $J$. In
practice you often don't have good values for either — payload changes, the CAD estimate is
wrong, components shift. An adaptive controller estimates those parameters online while it
flies, and you prove that the tracking error still converges.

Two things make this version worth doing:

**Quaternions instead of Euler angles.** Euler-angle attitude representations have
singularities. Using unit quaternions $q = [\eta, \epsilon^T]^T \in S^3$ avoids them
entirely, so the controller stays well-defined through any orientation.

**One Lyapunov function for everything.** Rather than proving stability separately for the
translational and rotational loops and hoping the cascade holds, this uses a single Lyapunov
function covering the full coupled dynamics.

## System model

With $\mathcal{I}$ the inertial frame and $\mathcal{B}$ the body frame:

$$\dot p = v, \qquad m\dot v = TRe_3 - mge_3$$
$$\dot q = \tfrac12 \Omega(\omega)q, \qquad J\dot\omega = \tau - \omega \times J\omega$$

The attitude dynamics are linear in the inertia parameters, which is what makes adaptation
possible:

$$J\dot\omega + S(\omega)J\omega = \Psi_o(\omega, \dot\omega)\theta = \tau$$

where $\theta \in \mathbb{R}^p$ is the constant inertia parameter vector and $\Psi_o$ is the
regressor.

## What I did

Designed the controller in two loops — an outer position controller producing a desired
thrust and attitude, and an inner attitude controller — with adaptive laws for the unknown
mass and inertia, and a stability proof for the whole thing.

The second part of the report extends this to the case where the **control allocation matrix
is also unknown**, which is the more realistic situation when you don't have a good model of
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
