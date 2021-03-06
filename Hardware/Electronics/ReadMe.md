# Electronics 

This system is designed to be controlled with RAMPS/MEGA electronics modified to run at 18-20Vdc. 
The reason for this is that 
* The intent is to eventually power the system with standard power tool (rechargeable) lithium batteries, which are typically either 18V or 20V.
* Higher voltage provides more power to the motors. 

Note that by driving the electronics at higher voltage, it is imperative that heat sinks and fans are used to cool the motor drivers and (possibly) the motors themselves.

You will need the following components:
* 1ea Power supply capable of at least 18-20Vdc and 7A
* 1ea MEGA2560
* 1ea RAMPS cape with motor drivers
* 1ea NEMA17 stepper motor with 5:1 planetary gear drive for the moineau pump

In the near term, this extruder system is intended to be used with existing 3D printer designs.  However, it may be advisable to replace NEMA17 motors with NEMA23 steppers.

