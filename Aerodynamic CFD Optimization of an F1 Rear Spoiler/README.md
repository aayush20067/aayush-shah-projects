# CFD Analysis of the Aerodynamic Performance of an F1 Car

Rear spoiler angle optimisation
ME219 (Fluid Mechanics), IIT Bombay

A CFD study of four Formula 1 car configurations, looking at how geometry and rear spoiler
angle trade off drag against downforce.

## Objectives

- Analyse the aerodynamic performance of four F1 car models using CFD.
- Evaluate and compare drag force, downforce and their coefficients for each model.
- Study how velocity and geometry affect aerodynamic behaviour.
- Understand where 2D CFD models fall short compared to commercial 3D aerodynamic analysis.

That last one matters. A 2D simulation can't capture the three-dimensional flow structures
that dominate real F1 aerodynamics — tip vortices, spanwise flow, wake interaction between
front and rear elements. Knowing what your model is throwing away is part of using it
properly.

## Setup

Turbulence was handled with k–ε and k–ω SST models, and second-order upwind discretisation
was used to resolve gradients more accurately.

Boundary conditions matter a lot for realism here: velocity inlet, pressure outlet, and a
moving ground so the car is travelling over a road rather than sitting in a wind tunnel with
a stationary floor. Aerodynamic forces come from integrating pressure and shear stress over
the car surface.

## Files

- `CFD Analysis of Aerodynamic Performance of an F1 Car with Rear Spoiler Angle Optimization.pdf`
  — full presentation: setup, results across all four configurations
- `v.mp4`, `v (1).mp4`, `v_car_a.mp4`, `velo.mp4` — flow visualisations from the simulations

## Tools

CFD solver, k–ε / k–ω SST turbulence modelling, second-order upwind discretisation.
