import subprocess, random, hashlib, string, os, json, re

PASSWD = "/etc/passwd"
SHADOW = "/etc/shadow"

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
  script = "Only authorized users should be able to log in."
  nobody_passwd = run_and_capture(["grep" , "nobody", PASSWD])
  nobody_shadow = run_and_capture(["grep" , "nobody", SHADOW])
  #print(nobody_passwd+"," + nobody_shadow)
  new_nobody_passwd = nobody_passwd.split(":")
  new_nobody_passwd[5] = "/tmp"
  new_nobody_passwd[6] = "/bin/sh"
  new_nobody_passwd = ":".join(new_nobody_passwd)
  new_nobody_shadow = nobody_shadow.split(":")
  new_nobody_shadow[1] = "U6aMy0wojraho"
  new_nobody_shadow = ":".join(new_nobody_shadow)

  state = {
    "original_passwd_line" : nobody_passwd,
    "original_shadow_line" : nobody_shadow,
    "dirty_passwd_line"    : new_nobody_passwd,
    "dirty_shadow_line"    : new_nobody_shadow,
  }
  update_file(SHADOW, nobody_shadow, new_nobody_shadow)
  update_file(PASSWD, nobody_passwd, new_nobody_passwd)
  results = { "script" : script, "initial_state" : state }
  return results


""" Conducts checks based on the initial state configuration. Returns the results of the checks via a list of message and point value dicts. A sample of the three types of results is provided."""
def check(state):
  results = []
  passwd_result = {"value" : 0, "max" : 2, "id" : 0, "msg" : ""}
  shadow_result = {"value" : 0, "max" : 1, "id" : 1, "msg" : ""}
  if state["dirty_passwd_line"] not in get_file_contents(PASSWD):
    passwd_result["value"] = 2
    passwd_result["msg"] = "backdoor in nobody account removed from /etc/passwd; flag: nobody_backdoor_passwd_removed-ab0c472f50627dcca3403048e53ba8b5"

  if state["dirty_shadow_line"] not in get_file_contents(SHADOW):
    shadow_result["value"] = 1
    shadow_result["msg"] = "password in nobody account removed from /etc/shadow ; flag: nobody_backdoor_shadow_removed-6722591e28e5fe091fd265ff61fab351"

  return [passwd_result, shadow_result]

""" Restores the host to pre-initialize state. """
def cleanup(state):
  update_file(PASSWD, r'nobody:[^\n]*', state["original_passwd_line"],regex=True)
  update_file(SHADOW, r'nobody:[^\n]*', state["original_shadow_line"],regex=True)

