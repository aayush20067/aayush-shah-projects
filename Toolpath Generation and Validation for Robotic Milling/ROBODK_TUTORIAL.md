1. Create a new cad on fusion..of the final design required
2. Go to the maufacturing tab on fusion
3. create a new setup
4. define the stock that you have and which you want to machine to get the final design
5. Select the operation you want to perform.
    1. Slotting
        or 
    2. Multi axis operations.
6. Select tool
7. Select the area that you want to machine 
8. Set all parameters (understand all the parameters and explain all of them)
9. click on generate
10. Download RoboDk plugin
11. Export model and toolpath to RoboDK
12. Import Robot
14. grab the position of the robot by connecting to the robt over ethernet (TCP-IP): IP of the robot is 192.168.0.20 set host ip to anything with the same 192.168.0.xx and subnet mask is 255.255.255.0 port is set to 10001 as given by the CR800D controller on the mistubishi robot
13. Define TCP based on physical measurements can be found manually if we know the position of any point in space wrt to the base.
14. Use frames to do that
15. Define a new frame with the block and toolpath
16. move that frame such that the tcp is somewhere..near the start of the toolpath..
17. click on the imported program from Fusion and set the frame and tool and robot..and set desired start position and generate the tool path
18. Simulate the toolpath
19. check for any erratic/out of the blue movements.
20. Export the generated program as a .prg file
21. download the .prg file onto RT tool box - offline.
22. Edit the .prg file so as to remove all the extra information on top ("open com" etc etc ) set tool etc..
24. verify that the syntax is right.
23. Open online on rt toolbox 3
24. in the online mode..go to the programs folder in the offline section and right click the program to send it to the controller
25. once sent to the controller...
26. open operation panel and begin the cutting process at the desired override.