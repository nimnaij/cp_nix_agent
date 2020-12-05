# cp_nix_agent
Linux CyberPatriot Scenario Simulation Tool

This project allows for automatic, modularized scenarios that simulate CyberPatriot competitions.

Note: I wrote this in 2017 in a very rushed weekend; consequently the python is buggy and terrible. It needs a rewrite, but it does mostly work in its current fragile, undocumented state.

I likewise have very little time to rewrite this so I'm mostly patching it to make it work when I can. 

Usage:

```
sudo python3 nix_agent.py
```

You can run it manually or as a service.

This is currently designed to run on Kubuntu 20.04 LTS


## TODO:

* convert HTML templates to external, editable mako templates
* use DRY principles for goodness' sake
* better error handling
