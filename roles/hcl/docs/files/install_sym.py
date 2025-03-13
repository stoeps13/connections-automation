# -*- encoding: utf8 -*-
# ***************************************************************** 
#                                                                   
# IBM Confidential                                                  
#                                                                   
# IBM Docs Source Materials                                         
#                                                                   
# (c) Copyright IBM Corporation 2012. All Rights Reserved.          
#                                                                   
# U.S. Government Users Restricted Rights: Use, duplication or      
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp. 
#                                                                   
# ***************************************************************** 

import socket
import os, stat
import shutil
import tarfile
import logging
import subprocess
import time
import json

from common import command, CFG, ZipCompat, call_wsadmin
from .add_symphony_limit_config import AddSymphonyLimitConfig

MONITOR_DEST = "/sym_monitor"
MONITOR_SRC_WIN = "/config/sym_monitor_win"
MONITOR_SRC_LIN = "/config/sym_monitor_linux"
INSTANCE_FILENAME = "instances.cfg"
CRONTABME_FILENAME = "crontabme"
CRONTABBAK_FILENAME = "crontab_bak"
SCHTASK_FILENAME = "start_task.bat"
END_SCHTASK_FILENAME = "end_task.bat"
HARDCODED_PATH = "/sym_inst/sym_monitor"
HARDCODED_REPO_PATH = "/root/repo"
CONFIG_JSON_SUB_DIR="IBMDocs-config"
CONFIG_JSON_FILE = "conversion-config.json"
POWERSHELL_DIR = "windowspowershell"
POWERSHELL = "powershell.exe"
KILL_SYM_SH = "./conversion/kill_sym.sh"
class InstallSymphony(command.Command):
  
  def __init__(self):
    #self.config = config.Config()
    self.root = CFG.getSymphonyFolder()
    self.count = CFG.getSymCount()
    self.build = CFG.get_build_dir()
    self.backup_dir = CFG.get_temp_dir() + os.sep + 'symphony'
    logging.debug("Conversion build folder located: " + os.path.abspath(self.build))
    
    if not CFG.get_cell_name():
      #get cell name
      logging.info("Start to get cell name...")
      cell_name_args = CFG.get_was_cmd_line()
      cell_name_args.extend(["-f",  "./conversion/tasks/get_cell_name.py"])
      cell_name_succ, cell_name_ws_out = call_wsadmin(cell_name_args)
      if not cell_name_succ:
        raise Exception("Failed to get the cell name")
      
      cell_name_var = "cellname"
      cell_name_var = "".join([cell_name_var,": "])
    
      cell_names = self._parse_info(cell_name_var,cell_name_ws_out)
       
      if len(cell_names) == 0:
        raise Exception("Failed to get the cell name")
      self.cell_name = cell_names[0]
      logging.info("Get cell %s successfully" % self.cell_name)
    else:
      self.cell_name = CFG.get_cell_name()
    
    #Get the user install path of node on USER_INSTALL_ROOT     
    logging.info("Start to get the USER_INSTALL_ROOT...")
    hostname = socket.gethostname()
    user_inst_args = CFG.get_was_cmd_line()
    user_inst_args.extend(["-f",  "./conversion/tasks/get_user_inst_path_for_node.py"])
    #user_ins_args.extend(["USER_INSTALL_ROOT"])
    user_inst_args.extend([hostname])
    user_inst_succ, user_inst_ws_out = call_wsadmin(user_inst_args)
    if not user_inst_succ:
      raise Exception("Failed to get was profile for given host")
    
    user_inst_path_var = "UserInstPath"
    user_inst_path_var = "".join([user_inst_path_var,": "])
    user_inst_paths = self._parse_info(user_inst_path_var,user_inst_ws_out)
       
    if user_inst_paths[0] == "None":
      raise Exception("Failed to get was profile for given host")
      
    self.cell_config_root = user_inst_paths[0]
    logging.info("Get USER_INSTALL_ROOT %s successfully" % self.cell_config_root)
    
    self.config_folder = os.path.join(self.cell_config_root,"config","cells",self.cell_name,CONFIG_JSON_SUB_DIR)
    
    print("self.config_folder: ")
    print((self.config_folder))

    if os.name == 'nt':
      self.binary_w32 = os.path.dirname(self.get_libre_path("libreOfficeWin"))
      logging.debug("Libre binary for windows located: " + self.binary_w32)
    else:
        self.binary_lnx = os.path.dirname(self.get_libre_path("libreOffice"))
        logging.debug("Libre binary for linux located: " + self.binary_lnx)
    
    self.root = CFG.getSymphonyFolder()
    self.monitor_dest = self.root + MONITOR_DEST
    self.count = CFG.getSymCount()
    self.port = CFG.getSymStartPort()
    self.build = CFG.get_build_dir()
    if os.name == "nt":
      self.monitor_src = self.build + MONITOR_SRC_WIN
    else:
      self.monitor_src = self.build + MONITOR_SRC_LIN
  def precheck(self):
    return True

  def postcheck(self):
    return True

  def readCfg(self, cfg=None):
    return True

  def _lnx(self, inst_path):
    logging.info("_lnx inst_path: " + inst_path)
    # Get the name of the source directory
    source_dir_name = os.path.basename(self.binary_lnx)

    # Create a new path under the destination directory with the same name as the source directory
    new_inst_path = os.path.join(inst_path, source_dir_name)

    shutil.copytree(self.binary_lnx, new_inst_path)
  
  def _w32(self, inst_path):
    logging.info("_w32inst_path: " + inst_path)
    # Get the name of the source directory
    source_dir_name = os.path.basename(self.binary_w32)
    logging.info("source_dir_name: " + source_dir_name)
    # Create a new path under the destination directory with the same name as the source directory
    new_inst_path = os.path.join(inst_path, source_dir_name)
    logging.info("new_inst_path: " + new_inst_path)
    shutil.copytree(self.binary_w32, new_inst_path)
 
  def config_sym_warning_log(self,instance_path):
      if os.name == 'nt':
          soffice_path = os.path.join(instance_path,'LibreOffice','program')
      else:
          soffice_path = os.path.join(instance_path,'libreoffice7.6','program')
      config_path = os.path.join(self.build,'config','sym_warning_log')

      for txt in os.listdir(config_path):
          shutil.copy(config_path + os.sep + txt, soffice_path)
        
  def ins_bin(self,upgrade=False):
    if not upgrade:
      if os.path.exists(self.root):
        logging.info("Cleaning old symphony binaries")
        shutil.rmtree(self.root)
      os.makedirs(self.root)
    
    add_sym_limit_config = AddSymphonyLimitConfig()
    
    for i in range(self.count):
      inst_i = self.root + os.sep + "inst" + str(i)
      logging.info("Installing symphony binaries for instance " + str(i) + " in " + inst_i)
      os.makedirs(inst_i)
      if os.name == "nt":
        self._w32(inst_i)
      else:
        self._lnx(inst_i)
      self.config_sym_warning_log(inst_i)
      add_sym_limit_config.do(inst_i)
    
    #standby instance
    for i in range(self.count,self.count*2):
      inst_i = self.root + os.sep + "inst" + str(i)
      logging.info("Standby: Installing symphony binaries for instance " + str(i) + " in " + inst_i)
      os.makedirs(inst_i)
      if os.name == "nt":
        self._w32(inst_i)
      else:
        self._lnx(inst_i)
      self.config_sym_warning_log(inst_i)
      add_sym_limit_config.do(inst_i)

  def kill_sym(self):
    logging.info("Stopping all the soffice processes")
    if os.name == "nt":
      #logging.warning("not implemented yet")      
      killed = False
      for i in range(3):
        subprocess.call(["taskkill.exe", "/f", "/im", "soffice.bin"])
        time.sleep(10)
        return_code = subprocess.call(["taskkill.exe", "/f", "/im", "soffice.bin"])
        if return_code == 128:
          killed = True
          break
      if not killed:
        raise Exception("Can not kill soffice.bin proceess, please kill them manually then try aggain.")          
      
    else:
      os.chmod(KILL_SYM_SH, stat.S_IRWXU|stat.S_IRWXG)
      #subprocess.call(["dos2unix", KILL_SYM_SH]) # 4170, to fix potential window format shell file
      subprocess.call([KILL_SYM_SH])
    
    logging.info("Waiting 10s after killing soffice to remove DLL successfully")
    time.sleep(10)
    logging.info("All the soffice processes stopped")

  def do(self):
    # remove the old binaries
    if os.path.exists(self.backup_dir):
      shutil.rmtree(self.backup_dir, True)     
    # end and delete task scheduler
    if os.name == 'nt':
      self.end_delete_task()
    # kill all soffice.exe
    self.kill_sym()
    self.ins_bin()
    self.copy()
    if os.name == "nt":
      self.windows_do()
    else:
      self.linux_do()
    return True

  def undo(self):
    logging.info("Cleaning symphony binaries")
    # end and remove task schedule
    if os.name == "nt":
      self.windows_undo()
    else:
      self.linux_undo()
    # kill all soffice.exe
    self.kill_sym()
      
    if os.path.exists(self.root):
      shutil.rmtree(self.root)
    return True
  
  def do_upgrade(self):
    logging.info('Start to upgrade symphony and task scheduler, uninstall and reinstall it...')
    
    # remove the old binaries
    if os.path.exists(self.backup_dir):
      shutil.rmtree(self.backup_dir, True) 
    
    # end and delete task scheduler
    if os.name == 'nt':
      self.end_delete_task()
    # kill all soffice.exe
    self.kill_sym()
    # backup the old sym folder
    if os.path.exists(self.root):
      shutil.move(self.root, self.backup_dir)
    #upgrade latest soffice.exe
    self.ins_bin(upgrade=True) #upgrade mode
    # copy monitor files to current directory
    self.copy()
    # upgrade instances.cfg and start_task.bat 
    self.windows_do()
    
    logging.info('Finish to upgrade symphony and task scheduler...')
    return True
  
  def undo_upgrade(self):
    logging.info('Start to undo upgrade symphony...')  
    # stop and delete task scheduler
    if os.name == 'nt':
      self.end_delete_task()
    # kill all soffice.exe
    self.kill_sym()
    
    # remove the latest content in sym folder
    if os.path.exists(self.root):
      shutil.rmtree(self.root)
    
    # copy old content from backup folder to current folder
    shutil.copytree(self.backup_dir, self.root)
    
    if os.name == 'nt':
      self.start_run_task() 
      
    logging.info('Finish to undo upgrade symphony and task scheduler...')
    return True
  
  def disable_scheduler(self):
    logging.info('Disable task scheduler.')
    
    cmd_list = [
      'schtasks /end /TN "sym_monitor"',
      'schtasks /change /disable /TN "sym_monitor"',
      'schtasks /end /TN "kill_timeout"',
      'schtasks /change /disable /TN "kill_timeout"'      
    ]
    
    if os.name == 'nt':
      for cmd in cmd_list:
        os.system(cmd)      
  
  def enable_scheduler(self):
    logging.info('Enable task scheduler.')
    
    cmd_list = [      
      'schtasks /change /enable /TN "sym_monitor"',
      'schtasks /run /I /TN "sym_monitor"',
      'schtasks /change /enable /TN "kill_timeout"',    
      'schtasks /run /I /TN "kill_timeout"',      
    ]
    
    if os.name == 'nt':
      for cmd in cmd_list:
        os.system(cmd)
        
  def copy(self):
    if os.path.exists(self.monitor_dest):
      logging.info("Cleaning old monitoring tools")
      shutil.rmtree(self.monitor_dest)  	
    logging.info("Copying monitoring tools to: " + self.monitor_dest)
    shutil.copytree(self.monitor_src, self.monitor_dest)
    if os.path.exists(os.path.join(self.monitor_dest, "sym_monitor.sh")):
      os.chmod(self.monitor_dest + "/sym_monitor.sh",stat.S_IRWXU|stat.S_IRWXG)
      os.chmod(self.monitor_dest + "/kill_timeout.sh",stat.S_IRWXU|stat.S_IRWXG)
      os.chmod(self.monitor_dest + "/template.sh",stat.S_IRWXU|stat.S_IRWXG)

  def windows_dev_startup(self):
    #logging.info("Windows CRON for monitor tools is not implemented yet")
    content = []
    for i in range(self.count*2):
      cmd_line = []
      cmd_line.append("start \"\" ")
      cmd_line.append("\"%s\inst%s\LibreOffice\program\soffice.exe\" " % (self.root, str(i)))
      cmd_line.append("-headless -nofirststartwizard \"-accept=socket,host=0.0.0.0,port=%s;urp;StarOffice.ServiceManager\"" % (str(self.port + i)))
      cmd_line.append("\n")
      content.append("".join(cmd_line))
      
    fw_path = self.monitor_dest + os.sep + "startup.bat"
    logging.info("Creating a temporary utility to start symphony processes manually: " + fw_path)
    fw_cmd = open(fw_path, "w")
    fw_cmd.write("".join(content))
    fw_cmd.close()

  def write_instance_cfg(self):
    cfg_content = []
    if os.name == "nt":
      symphony_dir_name = "LibreOffice"
      soffice_bin_ext = ".exe" 
    else: 
      symphony_dir_name = "libreoffice7.6"
      soffice_bin_ext = ".bin"  

    for i in range(self.count*2):
      sym_bin = "%s/inst%s/%s/program/soffice%s %s" % (
	self.root,
	str(i),
	symphony_dir_name,
	soffice_bin_ext,
	str(self.port+i))
      cfg_content.append(sym_bin)
      cfg_content.append("\n")
    cfg_path = self.monitor_dest + os.sep + INSTANCE_FILENAME

    logging.info("Writing monitoring instances file: " + cfg_path)
    fo_cfg = open(cfg_path, "w")
    fo_cfg.write("".join(cfg_content))
    fo_cfg.close()

  def write_schtasks(self):
    sctask_path = os.path.join(self.monitor_dest, SCHTASK_FILENAME)
    logging.info("Reading schtasks.exe template from: " + sctask_path)
    fr = open(sctask_path, "r")
    echo_tmp = fr.readline()
    monitor_tmp = fr.readline()
    monitor_dest_for_powershell = self.monitor_dest.replace(' ', '` ').replace('(', '`(').replace(')', '`)')
    path_for_powershell = self.get_powershell_path().replace(' ', '` ').replace('(', '`(').replace(')', '`)')
    monitor_tmp = monitor_tmp.replace("$powershell", path_for_powershell)
    monitor_tmp = monitor_tmp.replace("$IBMConversions/sym_monitor", monitor_dest_for_powershell)
    logging.debug("schtask info for monitor: %s" % monitor_tmp)    
    
    kill_tmp = fr.readline()
    repo_path_for_powershell = self.get_repo_path().replace(' ', '` ').replace('(', '`(').replace(')', '`)')
    kill_tmp = kill_tmp.replace("$powershell", path_for_powershell)
    kill_tmp = kill_tmp.replace("$IBMConversions/sym_monitor", monitor_dest_for_powershell)
    kill_tmp = kill_tmp.replace("$IBMConversions/repo", repo_path_for_powershell)
    logging.debug("schtask info for kill_timeout: %s" % kill_tmp)
    other_cnt = fr.readlines()
    fr.close()

    logging.info("Writing schtask file to: " + sctask_path) 
    fw = open(sctask_path, "w")
    fw.write(echo_tmp)
    fw.write("\n")
    fw.write(monitor_tmp)
    fw.write("\n")
    fw.write(kill_tmp)
    fw.write("\n".join(other_cnt))
    fw.close()
    logging.info("Adding monitor tools to Windows 2008 Server Task Scheduler")

  def write_crontabme(self):
    cron_path = self.monitor_dest + os.sep + CRONTABME_FILENAME
    logging.info("Reading crontab template from: " + cron_path)
    fr = open(cron_path, "r")
    monitor_tmp = fr.readline()
    monitor_tmp = monitor_tmp.replace(HARDCODED_PATH, self.monitor_dest)
    logging.debug("cron job for monitor: " + monitor_tmp)
    kill_tmp = fr.readline()
    kill_tmp = kill_tmp.replace(HARDCODED_PATH, self.monitor_dest)
    kill_tmp = kill_tmp.replace(HARDCODED_REPO_PATH, self.get_repo_path())
    logging.debug("cron job for kill" + kill_tmp)
    fr.close()
    
    #get current crontab list
    crontab_list = self.get_crontab_list()
    crontab_list.append(monitor_tmp)
    crontab_list.append(kill_tmp)
    
    logging.info("Writing crontab file to: " + cron_path)
    crontabme_file = open(cron_path, "w")
    for line in crontab_list:
      crontabme_file.write(line + "\n")
    crontabme_file.close()
    
    logging.info("Adding monitor tools to cron table")
    subprocess.call(["crontab", cron_path])

  def get_crontab_list(self):
    cmd = ["crontab","-l"]
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = p.communicate()[0]
    lines = self._splitlines(out)
    return lines

  def _splitlines(self,s):
    s = s.decode()
    rv = [s]
    
    if '\r' in s:
      rv = s.split('\r\n')
    elif '\n' in s:
      rv = s.split('\n')
    if rv[-1] == '':
      rv = rv[:-1]
    return rv 

  def windows_do(self):
    self.write_instance_cfg()
    self.write_schtasks()
    self.start_run_task()
    #TODO TEMP only for local development usage
    self.windows_dev_startup()
  
  def start_run_task(self):
    start_sctask_path = os.path.join(self.monitor_dest, SCHTASK_FILENAME)
    logging.info("run start_task.bat from " + start_sctask_path)
    # start_sctask_path
    if os.path.exists(start_sctask_path):
      subprocess.call([start_sctask_path])
    
  def end_delete_task(self):
    end_sctask_path = os.path.join(self.monitor_dest, END_SCHTASK_FILENAME)
    logging.info("run end_task.bat from " + end_sctask_path)
    # end_sctask_path
    if os.path.exists(end_sctask_path):
      subprocess.call([end_sctask_path])

  def windows_undo(self):
    self.end_delete_task()
    
  def linux_do(self):
    self.write_instance_cfg()
    self.write_crontabme()
  
  def linux_undo(self):
    if os.path.exists(self.monitor_dest):
      logging.info("Removing monitor tools from cron table")
      crontab_bak_path = os.path.join(self.monitor_dest, CRONTABBAK_FILENAME)
      #get current crontab list
      crontab_list = self.get_crontab_list()
      crontab_bak_file = open(crontab_bak_path, "w+")
      for line in crontab_list:
        if self.monitor_dest not in line:
          crontab_bak_file.write(line + "\n")    
      crontab_bak_file.close()
      if os.path.exists(crontab_bak_path):
        subprocess.call(["crontab", crontab_bak_path])

  def _parse_info(self,des,des_prt):    
    des_list = []
    for line in des_prt.split('\n'):
      if line.find(des) > -1:
        #raise Exception("Didn't get the node name")
        index_start = line.find(des)
        index_end = index_start + len(des)
        des_name = line[index_end : len(line)]
        if des_name.find('\n') >= 0:
          des_name = des_name[0 : des_name.find('\n')]
          
        #logging.info("Node name is: %s" % node_name)
        des_list.append(des_name)            
      #endif line.find
    #endfor
    return des_list
    
  def get_powershell_path(self):
    powershell_dir = None
    sys_path = os.environ['PATH'].lower()
    paths = sys_path.split(os.pathsep)
    for path in paths:
      if POWERSHELL_DIR in path:
        powershell_dir = path
        break      
    return os.path.join(powershell_dir, POWERSHELL)
  
  def get_libre_path(self, attr):
      repo_path = None
      config_file_path = os.path.join(self.config_folder, CONFIG_JSON_FILE)
      if(os.path.exists(config_file_path)):
        config_file = open(config_file_path)
        config_json = json.load(config_file)
        config_file.close()
        if(attr in config_json):
          repo_path = config_json[attr]['path']
      return repo_path

  def get_repo_path(self):
    repo_path = None
    config_file_path = os.path.join(self.config_folder, CONFIG_JSON_FILE)
    if(os.path.exists(config_file_path)):
      config_file = open(config_file_path)
      config_json = json.load(config_file)
      config_file.close()
      if("repositoryPath" in config_json):
        repo_path = config_json["repositoryPath"]
    return repo_path      