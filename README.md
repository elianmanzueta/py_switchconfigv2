# py_switchconfigv2
A re-write of my old py_switchconfig script. 

I wrote the py_switchconfig script about a year ago so I thought I'd give it a re-write with my more updated knowledge of python scripting and networking.
This script uses netmiko like its predecessor, but instead of working off of a GUI, it works off of command line options.

So for example, if you wanted to configure a port as an access port, you would do:

```
python SimpleSwitchConfig.py -ip _ip address_ -user _user_ -interface _interface_ -m access -v 10
```

This will configure an access port on the given interface and set it to VLAN 10.

This script is not meant to be used in an actual working environment.
