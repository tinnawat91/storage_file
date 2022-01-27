#!/usr/bin/python

import os, subprocess, sys, getopt

def main(argv):
  
  url_pkg = 'https://artifacts.elastic.co/downloads/kibana/kibana-7.16.3-linux-x86_64.tar.gz'
  url_java = 'https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz'
  ki_pkg = url_pkg.split('/')[5]
  java_pkg = url_java.split('/')[6]
  kibana_location = "/opt/CentralizeLog/kibana_v7.16.3/" + ki_pkg.split('.tar')[0]
  kibana_user = "kibana_system"
  kibana_pwd = "7fLTJJrkN7d29JWLMTDO"
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
    os.system(" echo 'export PATH=$PATH:$JAVA_HOME/bin:$ES_JAVA_HOME/bin' >> " + home_path + "/.bashrc")
    os.system(" source " + home_path +"/.bashrc")
  file.close()


  ###
  # Install Kibana
  ###
  print(" Download package ")
  os.system(" wget " + url_pkg + " -P /opt/CentralizeLog/kibana_v7.16.3")

  print(" Extract package ")
  os.system(" tar xvfz /opt/CentralizeLog/kibana_v7.16.3/" + ki_pkg + " -C /opt/CentralizeLog/kibana_v7.16.3")


  ###
  # Config Kibana
  ###
  print(" Add configuration ")
  os.system(" cp " + kibana_location + "/config/kibana.yml ./kibana.yml.bak")
  file = open( kibana_location + '/config/kibana.yml', 'r')

  lines = file.readlines()
  added = False
  for i in range(len(lines)):
    if(lines[i] == "elasticsearch.hosts: " + elascticsearch_host + "\n"):
      added = True
    
  if (not added):  
    os.system(" echo 'elasticsearch.hosts: %s' >> " %elascticsearch_host + kibana_location + "/config/kibana.yml")
    # os.system(" echo 'elasticsearch.ssl.verificationMOde: certificate' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo '#elasticsearch.username: %s' >> " %kibana_user + kibana_location + "/config/kibana.yml")
    os.system(" echo '#elasticsearch.password: %s' >> " %kibana_pwd + kibana_location + "/config/kibana.yml")
    # os.system(" echo 'elasticsearch.ssl.certificate: %s/config/certs/server.crt' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    # os.system(" echo 'elasticsearch.ssl.key: %s/config/certs/server.key' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    # os.system(" echo 'elasticsearch.ssl.keyPassphrase: 12345' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo '#elasticsearch.ssl.certificateAuthorities: %s/config/certs/rootCA.crt' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    os.system(" echo 'path.data: %s/app/data' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    os.system(" echo 'server.name: ki1.log.thailife.com' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo 'server.port: 5601' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo 'server.host: %s' >> " %ip + kibana_location + "/config/kibana.yml")
    os.system(" echo '#server.ssl.enabled: true' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo '#server.ssl.certificate: %s/config/certs/server.crt' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    os.system(" echo '#server.ssl.key: %s/config/certs/server.key' >> " %kibana_location + kibana_location + "/config/kibana.yml")
    os.system(" echo '#server.ssl.keyPassphrase: 12345' >> " + kibana_location + "/config/kibana.yml")
    os.system(" echo '#server.ssl.certificateAuthorities: %s/config/certs/rootCA.crt' >> " %kibana_location + kibana_location + "/config/kibana.yml")

  file.close()

  ###
  # Create kibana.service
  ###
  os.system(" echo '[Unit]' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'Description=Kibana' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo '' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo '[Service]' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'Type=simple' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'User=elkusr' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'Group=elkgrp' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'ExecStart=" + kibana_location + "/bin/kibana' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'Restart=no' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'LimitNOFILE=65536' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'LimitMEMLOCK=infinity' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo '' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo '[Install]' >> " + kibana_location + "/config/kibana.service")
  os.system(" echo 'WantedBy=multi-user.target' >> " + kibana_location + "/config/kibana.service")
  os.system(" cp " + kibana_location + "/config/kibana.service /etc/systemd/system")
  os.system(" systemctl daemon-reload")
  
  ###
  # Change directory owner
  ###
  os.system("chown elkusr:elkgrp -R /opt/CentralizeLog/")

  ###
  # Open ports (firewall)
  ###
  print(" Open port: 5601 ") 
  os.system(" ufw allow from any to any port 5601 proto tcp")


if __name__ == "__main__":
  main(sys.argv[1:])