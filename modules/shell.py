
""" Sets up the initial environment and returns a dictionary of its state and an instruction script. The state is then passed on to the check and cleanup methods"""
def initialize():
  state = {}
  script = "Good Luck!"
  results = { "script" : script, "initial_state" : state }
  return results

""" Conducts checks based on the initial state configuration. Returns the results of the checks via a list of message and point value dicts. A sample of the three types of results is provided."""
def check(state):
  return [{"msg" : "Sample Incomplete Item", "value": 0, "max" : 3 , "id" : 0}, {"msg" :"Sample Bad Item", "value":-2, "max": 0, "id" :1}, {"msg" : "Sample Completed Item", "value": 1, "max" : 1, "id" : 2}]

""" Restores the host to pre-initialize state. """
def cleanup(state):
  pass
