# vmobey - Execute actions in guest over VM channel (guest component) 
#### Version 0.1 / "Baba's Baklava"

## Introduction
This little script allows you to execute actions inside a virtual machine that have been requested from the host/hypervisor.  
These actions are really just standard executables dropped into a directory, that will be spawned as a process.  

By joining forces with it's hypervisor companion app ["vmdo"](https://github.com/doctor-love/vmdo), many great tasks can be achieved - such instructing the guest to perform system updates, reconfigure network settings and similar.  

It is like a bad/less complex version of Peter Odding's ["negotiator"](https://github.com/xolox/python-negotiator).  


## Usage
```
# cp -p vmobey.py /usr/bin/vmobey
# mkdir /usr/lib/vmobey
# cp -p ~/scripts/start_vpn /usr/lib/vmobey
# vmobey --channel-dev /dev/vport3p1
INFO: Executing requested action "/usr/lib/vmobey/start_vpn work" with 90 second(s) timeout
INFO: Result - RC: "0", OUTPUT: "VPN connection "work" was successfully started"
ERROR: Requested action "/usr/lib/vmobey/root_my_box" is not allowed

```

## Dependencies
- Linux (should probably work fine for Windows and GNU HURD as well, but I haven't tested it)
- Driver support for the VirtIO serial port (who hasn't?!)
- Python 3.5 or later with the standard library
