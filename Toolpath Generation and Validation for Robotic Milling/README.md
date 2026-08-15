# Toolpath Generation and Validation for Robotic Milling

Mitsubishi RV-8CRL industrial arm, Fusion 360 → RoboDK → CR800D
ME230 (Mechanical Processing of Materials), IIT Bombay

I ran a part all the way from CAD geometry to actual metal removal on a six-axis industrial
arm, and then figured out why the finished slot didn't match what the CAM software said it
would be.

## Why do this on a robot arm

Robot arms are worth considering as an alternative to a dedicated CNC machining centre.
They reach orientations and workpiece geometries a 3-axis machine can't, and they don't need
specialised fixturing. The downside is stiffness. An arm is much more compliant than a
machine tool, so it deflects and chatters under cutting load, which means the tool wanders
off the commanded path exactly when it's cutting hardest.

## What I did

I designed the target geometry in Fusion 360, defined the stock, and generated slotting
toolpaths in the Manufacturing workspace using a 3 mm flat-end mill, setting up feeds,
stepdowns and lead-in/lead-out.

Calibrating the tool centre point was the step that mattered most. I did it frame-based:
measured the tool geometry physically, then defined reference frames from a known point
relative to the robot base. Get this wrong and the program cuts somewhere other than where
you think it does.

For validation I exported the model and toolpath to RoboDK, imported the robot, and
connected to the CR800D controller over Ethernet (TCP/IP, port 10001) to grab the live robot
pose. Then I simulated the whole program, checking reachability across the workspace and
watching for erratic joint motions before anything touched material.

To run it, I post-processed to a `.prg` file, stripped the generated preamble, checked the
syntax in RT ToolBox3, sent it to the controller and ran the cut at a controlled override.

## What came out

Measuring the finished slot showed an upward ramp along the length of the cut. That's the
arm deflecting progressively under load, not a programming error.

I worked out a compensation for it: put a deliberate downward plunge into the toolpath to
counteract the deflection. That brought depth variation down from roughly 200 µm to 85 µm.

The wider point is that once this pipeline is set up, it works for pretty much any geometry.
Fusion handles geometry and toolpath, RoboDK handles the robot-specific kinematics, the
controller executes. That includes curved-surface machining, which a conventional 3-axis CNC
can't reach.

## Files

- `ME230_Report.pdf` — full report, method, results, compensation analysis
- `ROBODK_TUTORIAL.md` — the actual working procedure, start to finish, from Fusion setup
  through to sending the program to the controller
- `Simulation Based Toolpath Generation & Validation for Robotic Milling.pptx` — final
  presentation
- `RoboDK Training Certificate ... .pdf` — RoboDK training, 6 hours

There's a video walkthrough of the simulation and the cut that goes with the report. It's
1.4 GB so it's hosted outside the repo. *(link to follow)*

## Hardware and software

Mitsubishi RV-8CRL six-axis arm, CR800D controller, Autodesk Fusion 360 (CAD and CAM),
RoboDK, RT ToolBox3, 3 mm flat-end mill, Ethernet TCP/IP.
