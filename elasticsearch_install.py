#!/usr/bin/python

import os, subprocess, sys, getopt

def main(argv):
  ### ------------------------------------------------------------------------------
  # BEGIN cluster's common config 
  ###

  seed_hosts = '["10.102.48.73", "10.102.48.74", "10.102.48.75"]'
  initial_master_nodes = '["esm1.log.thailife.com", "esm2.log.thailife.com", "esm3.log.thailife.com"]'
  url_pkg = 'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.16.3-linux-x86_64.tar.gz'
  url_java = 'https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz'
  es_pkg = url_pkg.split('/')[5]
  java_pkg = url_java.split('/')[6]
  elasticsearch_location = '/opt/CentralizeLog/elk_v7.16.3/' + es_pkg.split('-linux')[0]
  
  ### 
  # END cluster's common config 
  ### ------------------------------------------------------------------------------

  cluster_name = ''
  node_name = ''
  node_type = ''

  try: 
    opts, args = getopt.getopt(argv,"c:n:t:",["cluster-name=", "node-name=", "type="])
  except getopt.GetoptError:
    print('1: test.py -c <cluster name> -n <node name> -t <node type>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
        print('test.py -c <cluster name> -n <node name> -t <node type>')
        sys.exit()
    elif opt in ("-c", "--cluster-name"):
        cluster_name = arg
        print('cluster_name: ', cluster_name)
    elif opt in ("-n", "--node-name"):
        node_name = arg
        print('node_name: ', node_name)
    elif opt in ("-t", "--type"):
        node_type = arg
        print('node_type: ', node_type)

  if(cluster_name == '' or node_name == '' or node_type == ''):
    print('2: test.py -c <cluster name> -n <node name> -t <node type>')
    sys.exit(2)


  ip = subprocess.check_output('hostname -i', shell=True).decode('utf-8')
  print('ip: ', ip)
  mem = int(subprocess.check_output("awk '/MemTotal/ {print $2}' /proc/meminfo", shell=True).decode('utf-8'))
  mem = round(mem/(1024*1024), 2)
  print('memory: ~' + str(mem) + 'GB')
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
    if(line == "elasticsearch  soft  nofile    65536\n"):
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
  os.system("mkdir /opt/CentralizeLog/java11")
  os.system("wget " + url_java + " -P /opt/CentralizeLog/java11/")
  os.system("tar xvfz /opt/CentralizeLog/java11/" + java_pkg + " -C /opt/CentralizeLog/java11")
  
  java_path = '/opt/CentralizeLog/java11/jdk-11'
  
  added = False
  file = open(home_path + '/.bashrc', 'r')
  lines = file.readlines()
  for line in lines:
    if(line == "export JAVA_HOME=" + java_path + "\n"):
      added = True
  if(not added):
    os.system(" echo 'export JAVA_HOME=" + java_path + "' >> " + home_path + "/.bashrc")
    os.system(" echo 'export ES_JAVA_HOME=" + java_path + "' >> " + home_path + "/.bashrc")
    os.system(" echo 'export PATH=$PATH:$JAVA_HOME/bin:$ES_JAVA_HOME/bin' >> " + home_path + "/.bashrc")
    os.system("source " + home_path +"/.bashrc")
  file.close()

  
  
  ###
  # Install elasticsearch
  ###
  print(" Download package ")
  os.system(" wget " + url_pkg + " -P /opt/CentralizeLog/elk_v7.16.3")

  print(" Extract package ")
  os.system(" tar xvfz /opt/CentralizeLog/elk_v7.16.3/" + es_pkg + " -C /opt/CentralizeLog/elk_v7.16.3")
  
  ###
  # Config JVM heap size
  ###
  half_mem = str(round((mem-2)/2))
  print(" Set Java Memory to half of system MEMORY ~ " + half_mem + " GB")

  os.system(" cp " + elasticsearch_location + "/config/jvm.options " + elasticsearch_location + "/config/jvm.options.bak")
  file = open( elasticsearch_location + '/config/jvm.options', 'r')
  lines = file.readlines()
  added = False
  for line in lines:
    if(line == "-Xms"):
      added = True
  if (not added):
    os.system(" echo '-Xms%sg' >> " %half_mem + elasticsearch_location + "/config/jvm.options")
    os.system(" echo '-Xmx%sg' >> " %half_mem + elasticsearch_location + "/config/jvm.options")
  file.close()

  ###
  # Config Elasticsearch
  ###
  print(" Add configuration ")
  os.system(" cp " + elasticsearch_location + "/config/elasticsearch.yml " + elasticsearch_location + "/config/elasticsearch.yml.bak")
  file = open( elasticsearch_location + '/config/elasticsearch.yml', 'r')
  lines = file.readlines()

  added = False
  for line in lines:
    if(line == "cluster.name: " + cluster_name + "\n"):
      added = True
  if (not added):
    os.system(" echo 'cluster.name: %s' >> " %cluster_name + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'node.name: %s' >> " %node_name + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'path.data: /opt/CentralizeLog/elk_v7.16.3/app/data' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'path.logs: /opt/CentralizeLog/elk_v7.16.3/app/logs' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'network.bind_host: 0.0.0.0' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'network.host: %s' >> " %ip + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'node.max_local_storage_nodes: 3' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'bootstrap.memory_lock: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    
    if(node_type == 'master'):
      os.system(" echo 'node.master: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
      os.system(" echo 'node.data: false' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    else:
      os.system(" echo 'node.master: false' >> " + elasticsearch_location + "/config/elasticsearch.yml")
      os.system(" echo 'node.data: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
      
    os.system(" echo 'http.port: 9200' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'transport.tcp.port: 9300' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'discovery.seed_hosts: %s' >> " %seed_hosts + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'cluster.initial_master_nodes: %s' >> " %initial_master_nodes + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo '' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.enabled: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.enabled: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.key: " + elasticsearch_location + "/config/certs/server.key' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.key_passphrase: 12345' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.certificate: " + elasticsearch_location + "/config/certs/server.crt' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.certificate_authorities: " + elasticsearch_location + "/config/certs/rootCA.crt' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.transport.ssl.verification_mode: certificate' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo '' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.http.ssl.enabled: true' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.http.ssl.key: " + elasticsearch_location + "/config/certs/server.key' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.http.ssl.key_passphrase: 12345' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.http.ssl.certificate: " + elasticsearch_location + "/config/certs/server.crt' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    os.system(" echo 'xpack.security.http.ssl.certificate_authorities: " + elasticsearch_location + "/config/certs/rootCA.crt' >> " + elasticsearch_location + "/config/elasticsearch.yml")
    
  file.close()

  ###
  # Create elasticsearch.service
  ###
  os.system(" echo '[Unit]' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'Description=ElasticSearch' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo '' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo '[Service]' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'Type=simple' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'User=elkusr' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'Group=elkgrp' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'ExecStart=" + elasticsearch_location + "/bin/elasticsearch' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'Restart=no' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'LimitNOFILE=65536' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'LimitMEMLOCK=infinity' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo '' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo '[Install]' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" echo 'WantedBy=multi-user.target' >> " + elasticsearch_location + "/config/elasticsearch.service")
  os.system(" cp " + elasticsearch_location + "/config/elasticsearch.service /etc/systemd/system")
  os.system(" systemctl daemon-reload")
  
  ###
  # Change directory owner
  ###
  os.system("chown elkusr:elkgrp -R /opt/CentralizeLog/")

  ###
  # Open ports (firewall)
  ###
  print(" Open port: 9200, 9300 ") 
  if(node_type == 'master'):
    os.system(" ufw allow from any to any port 9200 proto tcp")
  os.system(" ufw allow from any to any port 9300 proto tcp")
  
if __name__ == "__main__":
  main(sys.argv[1:])
