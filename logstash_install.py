#!/usr/bin/python

import os, subprocess, sys, getopt

def main(argv):
  
  url_pkg = 'https://artifacts.elastic.co/downloads/logstash/logstash-7.16.3-linux-x86_64.tar.gz'
  url_java = 'https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz'
  ls_pkg = url_pkg.split('/')[5]
  java_pkg = url_java.split('/')[6]
  logstash_location = "/opt/CentralizeLog/logstash_v7.16.3/" + ls_pkg.split('-linux')[0]
  logstash_user = "logstash_system"
  logstash_pwd = "HPxznbRHt3KynPOa9cww"
  elascticsearch_host = '["http://esm1.log.thailife.com:9200", "http://esm2.log.thailife.com:9200", "http://esm3.log.thailife.com:9200"]'

  
  ip = subprocess.check_output('hostname -i', shell=True).decode('utf-8')
  print('ip: ', ip)
  sudo_user = os.environ['SUDO_USER']
  home_path = '/home/elkusr'

  ###
  # Config Server
  ###
  print(" Config server ")
  added = False
  file = open('/etc/security/limits.conf', 'r')
  lines = file.readlines()
  for line in lines:
    if(line == "kibana  soft  nofile    65536\n"):
      added = True
  if (not added):
    os.system("echo 'elkusr  soft  nofile    65536' >> /etc/security/limits.conf")
    os.system("echo 'elkusr  hard  nofile    65536' >> /etc/security/limits.conf")
    os.system("echo 'elkusr  soft  memlock   unlimited' >> /etc/security/limits.conf")
    os.system("echo 'elkusr  hard  memlock   unlimited' >> /etc/security/limits.conf")
  
  os.system("swapoff -a")
  file.close()

  added = False
  file = open('/etc/sysctl.conf', 'r')
  lines = file.readlines()
  for line in lines:
    if(line == "vm.max_map_count = 262144\n"):
      added = True
  if (not added):
    os.system("echo 'vm.max_map_count = 262144' >> /etc/sysctl.conf")
    
  os.system("sysctl -p")
  file.close()

  ###
  # Install java 11
  ###
  print(" Install JDK 11 ")
  os.system("wget " + url_java + " -P /opt/CentralizeLog/java11/")
  os.system("tar xvfz /opt/CentralizeLog/java11/" + java_pkg + " -C /opt/CentralizeLog/java11/")
  
  java_path = '/opt/CentralizeLog/java11/jdk-11'
  
  added = False
  file = open(home_path + '/.bashrc', 'r')
  lines = file.readlines()
  for line in lines:
    if(line == "export JAVA_HOME=" + java_path + "\n"):
      added = True
  if(not added):
    os.system(" echo 'export JAVA_HOME=" + java_path + "' >> " + home_path + "/.bashrc")
    os.system(" echo 'export LS_JAVA_HOME=" + java_path + "' >> " + home_path + "/.bashrc")
    os.system(" echo 'export PATH=$PATH:$JAVA_HOME/bin:$LS_JAVA_HOME/bin' >> " + home_path + "/.bashrc")
    os.system(" source " + home_path +"/.bashrc")
  file.close()


  ###
  # Install logstash
  ###
  print(" Download package ")
  os.system(" wget " + url_pkg + " -P /opt/CentralizeLog/logstash_v7.16.3")

  print(" Extract package ")
  os.system(" tar xvfz /opt/CentralizeLog/logstash_v7.16.3/" + ls_pkg + " -C /opt/CentralizeLog/logstash_v7.16.3")


  ###
  # Config logstash
  ###
  print(" Add configuration ")
  os.system(" cp " + logstash_location + "/config/logstash.yml ./logstash.yml.bak")
  file = open( logstash_location + '/config/logstash.yml', 'r')

  lines = file.readlines()
  added = False
  for i in range(len(lines)):
    if(lines[i] == "elasticsearch.hosts: " + elascticsearch_host + "\n"):
      added = True
    
  if (not added):  
    os.system(" echo '#xpack.monitoring.enabled: true' >> " + logstash_location + "/config/logstash.yml")
    os.system(" echo '#xpack.monitoring.elasticsearch.hosts: %s' >> " %elascticsearch_host + logstash_location + "/config/logstash.yml")
    os.system(" echo '#xpack.monitoring.elasticsearch.username: %s' >> " %logstash_user + logstash_location + "/config/logstash.yml")
    os.system(" echo '#xpack.monitoring.elasticsearch.password: %s' >> " %logstash_pwd + logstash_location + "/config/logstash.yml")
    os.system(" echo '#xpack.monitoring.elasticsearch.ssl.certificate_authority: %s/config/certs/rootCA.crt' >> " %logstash_location + logstash_location + "/config/logstash.yml")
    os.system(" echo 'path.data: %s/app/data' >> " %logstash_location + logstash_location + "/config/logstash.yml")
    os.system(" echo 'path.logs: %s/app/logs' >> " %logstash_location + logstash_location + "/config/logstash.yml")
    os.system(" echo 'node.name: ls1.log.thailife.com' >> " + logstash_location + "/config/logstash.yml")
  
  file.close()
  
  ###
  # Change directory owner
  ###
  os.system("chown elkusr:elkgrp -R /opt/CentralizeLog/")

  ###
  # Open ports (firewall)
  ###
  # print(" Open port: 5601 ") 
  # os.system(" ufw allow from any to any port 5601 proto tcp")


if __name__ == "__main__":
  main(sys.argv[1:])