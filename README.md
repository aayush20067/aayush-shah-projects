# Aayush Shah — Engineering Projects

B.Tech Mechanical Engineering, IIT Bombay (Roll 24B2300).
I work mostly on robotics, control and autonomy, with a fair amount of hands-on
experimental work alongside it.

This repo collects the engineering projects from my undergrad. Each folder is one project,
named for what it is rather than the course code it came from.

## Projects

**[Toolpath Generation and Validation for Robotic Milling](./Toolpath%20Generation%20and%20Validation%20for%20Robotic%20Milling)**
Took a part from CAD through to actual cutting on a Mitsubishi RV-8CRL six-axis arm. TCP
calibration, slot milling, and a compensation strategy for arm deflection that brought depth
variation down from about 200 µm to 85 µm.
*Fusion 360, RoboDK, RT ToolBox3, CR800D controller*

**[Tuned Vibration Absorber Design and Testing](./Tuned%20Vibration%20Absorber%20Design%20and%20Testing)**
Built a 2-DOF dynamic vibration absorber and tested it. Got clean resonance splitting and an
anti-resonance dip, then checked how far the real rig drifts from Den Hartog theory.
*Arduino, MPU6050, Python, FFT, MSC ADAMS*

**[F1 Tyre Degradation Modelling](./F1%20Tyre%20Degradation%20Modelling)**
Two-stage ML pipeline for pulling a tyre degradation signal out of noisy lap times. An MLP
scores how "clean" each lap is, and those scores weight the regression stage. Also documents
where it stops working, which turned out to be the interesting part.
*Python, FastF1, scikit-learn*

**[Quaternion-Based Adaptive Control for Quadrotor Trajectory Tracking](./Quaternion-Based%20Adaptive%20Control%20for%20Quadrotor%20Trajectory%20Tracking)**
Adaptive controller for a quadrotor with unknown mass and inertia. Uses unit quaternions to
avoid singularities and one Lyapunov function covering translational and rotational dynamics
together.
*MATLAB, Simulink*

**[Nonlinear Backstepping Control of a Quadrotor](./Nonlinear%20Backstepping%20Control%20of%20a%20Quadrotor)**
A separate controller for the same platform, designed by recursive backstepping.
*MATLAB, Simulink*

**[Strain Analysis of Multi-Hole Interaction via Digital Image Correlation](./Strain%20Analysis%20of%20Multi-Hole%20Interaction%20via%20Digital%20Image%20Correlation)**
Experimental study of how nearby holes change the strain field in acrylic under tension,
across eight specimen configurations.
*DIC (MatchID), UTM, speckle patterning*

**[Aerodynamic CFD Optimization of an F1 Rear Spoiler](./Aerodynamic%20CFD%20Optimization%20of%20an%20F1%20Rear%20Spoiler)**
CFD comparison of four F1 body configurations, looking at drag, downforce and rear spoiler
angle.
*CFD, k–ε / k–ω SST*

## Other work

Two other things I work on live in their own repos so they stay current instead of sitting
here as frozen copies:

- [2026-rpl-wifi-slam](https://github.com/rpl-iitb/2026-rpl-wifi-slam) — WiFi-based SLAM at
  the Robot Perception Lab, IIT Bombay. Ongoing.
- AUV-IITB — Autonomous Underwater Vehicle team, IIT Bombay. RoboSub 2026.

## A note on what's here

I've included the reports, presentations and raw data next to the code so you can check the
work rather than take my word for it. Where a project gave a partial or negative result I've
left that in. The tyre degradation write-up in particular spends a section on why the model
fails to generalise across seasons.

Several of these were done in course groups at IIT Bombay. Author lines are on the reports.
