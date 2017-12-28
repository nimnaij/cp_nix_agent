
""" Sets up the initial environment and returns a dictionary of its state and an instruction string. The state is then passed on to the check method."""
def initialize():
  state = {}
  script = "sample"
  results = { "script" : script, "initial_state" : state }
  return results

""" Conducts checks based on the initial state configuration. Returns the results of the checks via a list of message and point value dicts"""
def check(state):
  return [{"msg" : "success!", "value": 3, "max" : 3 , "id" : 0}, {"msg" :"you did something wrong", "value":-2, "max": 0, "id" :1}]
