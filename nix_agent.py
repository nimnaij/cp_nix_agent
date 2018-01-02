#!/usr/bin/python3
import subprocess, random, importlib.util, os, json, time, sys, threading

MODULES_DIR = "modules"
MODULES_NAMESPACE = "cp_mod_{0}"
def load_module(path,name):
  try:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
  except:
    print("Unexpected error: ")
    print( sys.exc_info()[0])
    return False
  return module

def load_modules():
  modules = {}
  for name in next(os.walk(MODULES_DIR))[2]:
    if name[-3:] == ".py":
      path = os.path.join(MODULES_DIR,name)
      module = load_module(path,MODULES_NAMESPACE.format(name[:-3]))
      if module:
        modules[name[:-3]] = module
  return modules

class script_builder:

  default_os = "Linux"
  default_orgs = ["Bob's Morgue: you kill 'em we chill 'em", "Flying Squirrel Taxidermy","Airforce Supply Depot: chairs for people who sit","Army Supply Depot: supplies for the warfighter", "Smalltown Computer Repair","Skydiving Are Us: first time success or your money back", "Blue Falcons Unite: support group for USAFA grads", "iPhone Repair Shop: we'll overcharge you twice", "Android Repair Shop: hardware repairs for the unpatched smart phone","Neckbeards Apparel: for all your larping needs", "Faux News: false reporting with a bible in our hand and a twinkle in our eye", "Jefferson Post: your source for petty dramatic reporting", "Old York Times: we promise the rest of the paper is better than what you see on Facepage", "Wall Avenue Journal: you can't use private browsing to bypass our paywall", "Tommy's Closet", "Rent-A-Swag", "Pawnee Parks and Recreation", "Fringe Division", "Aperture Science", "Apogee Hardware", "Dharma Initiative", "Commander Keen's Pogo Sticks", "Cosmo's Cosmic Spacecraft", "Micro Man's Tiny Circuits"]

  script = """You are part of an incident response team for your organization and have been selected to help triage a {os} workstation at "{org}."

Conduct an investigation to identify and fix security and policy violations.
"""

  def pick_random(self,choices):
    return random.choice(choices)

  def initialize_modules(self):
    modules = load_modules()
    messages = []
    module_data = {}
    for key in modules.keys():
      m = modules[key]
      try:
        data = m.initialize()
        module_data[key] = data
        messages.append(data["script"])
      except:
        print("Unexpected error: ")
        print( sys.exc_info()[0])
        pass
    self.module_data = module_data
    return messages

  def __init__(self, values={}):
    if "os" not in values.keys():
      try:
        values["os"] = subprocess.run(["lsb_release","-sd"], stdout=subprocess.PIPE).stdout.decode('utf8').replace("\n","")
      except:
        try:
          values["os"] = subprocess.run(["uname","-s","-r","-i","-o"],stdout=subprocess.PIPE).stdout.decode('utf8').replace("\n","")
        except:
          values["os"] = self.default_os
    if "org" not in values.keys():
      values["org"] = self.pick_random(self.default_orgs) 
    script = self.script.format(**values)
    self.values = values 
    for line in self.initialize_modules():
      script += "\n" + line +"\n"

    self.final_script = script

  def get_state(self):
    return { "module_data" : self.module_data, "values" : self.values }

  def get_script(self):
    return self.final_script

class nix_agent:
  init_file = ".init"
  check_interval = 30
  def load_state(self):
    f = open(self.init_file,"r")
    data = f.read()
    f.close()
    config = json.loads(data)
    self.script = config["script"]
    self.module_data = config["module_data"]
    self.initial_values = config["values"]
    self.cur_scores = config["scores"]
  def save_state(self):
    config = {"script" : self.script, "module_data" : self.module_data, "values" : self.initial_values, "scores" : self.cur_scores }
    f = open(self.init_file,"w")
    f.write(json.dumps(config))
    f.close()
  def __init__(self):
    try:
      self.load_state()
    except:
      self.script_builder = script_builder()
      self.script = self.script_builder.get_script()
      initial_data = self.script_builder.get_state()
      self.module_data = initial_data["module_data"]
      self.initial_values = initial_data["values"]
      self.cur_scores = {}
      self.save_state()
    self.render_script()

  def begin_game(self):
    self.active = True
    while self.active == True:
      self.execute_checks()
      self.save_state()
      time.sleep(self.check_interval)
  def execute_checks(self):
    outputs = []
    modules = load_modules()
    for key in modules.keys():
      module = modules[key]
      cur_outputs = module.check(self.module_data[key]["initial_state"])
      for output in cur_outputs:
        output["id"] = key + str(output["id"])
      outputs += cur_outputs
    for line in outputs:
      if line["id"] in self.cur_scores.keys():
        if self.cur_scores[line["id"]]["value"] != line["value"]:
          self.handle_new_score(self.cur_scores[line["id"]], line)
      self.cur_scores[line["id"]] = line
#      if line["value"] < 0:
#        continue
      print(line)

  def handle_checcks(self):
    pass

  def cleanup_game(self):
    modules = load_modules()
    for key in modules.keys():
      module = modules[key]
      try:
        module.cleanup(self.module_data[key]["initial_state"])
      except:
        print("Unexpected error: ")
        print( sys.exc_info()[0])
        continue

  def handle_new_score(self,old,new):
    pass
  def render_script(self):
    print(self.script)
  def start(self):
    self.begin_game()

if __name__ == "__main__":
  agent = nix_agent()
  t = threading.Thread(target=agent.start)
  t.start()
  while True:
    cmd = input("quit to quit; clean to cleanup;reset to cleanup and remove conf file;\n")
    if "quit" in cmd:
      agent.active = False
      print("Waiting for watcher thread to finish...")
      t.join()
      break
    elif "clean" in cmd:
      agent.cleanup_game()
    elif "reset" in cmd:
      agent.active = False
      agent.cleanup_game()
      t.join()
      os.remove(agent.init_file)
      break
      
  
