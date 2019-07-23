import subprocess, random, hashlib, string, os, json, re

USER = "blackhat"

def run_and_capture(l):
  data = subprocess.run(l, stdout=subprocess.PIPE).stdout.decode('utf8')
  if data[-1:] == "\n":
    data = data[:-1]
  return data

def write_to_file(f,c):
  fh = open(f,"w")
  fh.write(c)
  fh.close()

def get_file_contents(f):
  f = open(f, "r")
  t = f.read()
  f.close()
  return t
def update_file(f,old,new,regex=False):
  original = get_file_contents(f)
  #print("original==>"+original)
  #print(old + "-->" + new)
  if not regex:
    updated = original.replace(old,new)
  else:
    updated = re.sub(old,new,original)
  #print("updated==>" +updated)
  write_to_file(f,updated)

def rand_str(x):
  return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(x)])


def hash_file(p):
  f = open(p,"rb")
  d = f.read()
  f.close()
  return hashlib.sha256(d).hexdigest()

def install_package_from_repo(package):
  run_and_capture(["apt-get","install","-y",package])


""" Sets up the initial environment and returns a dictionary of its state and an instruction script. The state is then passed on to the check and cleanup methods"""
def initialize():
  script = "Users should not have MP3 files in their home directory"
  file_output = "/home/{0}/bell.mp3".format(USER)
  run_and_capture(["wget", "http://soundbible.com/grab.php?id=2206&type=mp3", "-O", file_output])

  state = {
    "file_output"    : file_output,
  }
  results = { "script" : script, "initial_state" : state }
  return results


""" Conducts checks based on the initial state configuration. Returns the results of the checks via a list of message and point value dicts. A sample of the three types of results is provided."""
def check(state):
  results = []
  mp3_result = {"value" : 0, "max" : 2, "id" : 0, "msg" : ""}
  if not os.path.exists(state["file_output"]):
    mp3_result["value"] = 2
    mp3_result["msg"] = "Banned MP3 file has been removed. Your flag is: no_MP3s_allowed_:("

  return [mp3_result]

""" Restores the host to pre-initialize state. """
def cleanup(state):
  if os.path.exists(state["file_output"]):
    run_and_capture(["rm", state["file_output"]])
    
