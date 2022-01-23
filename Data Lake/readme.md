# Setting up an on-premise data lake

The following setup is for a single computer running Ubuntu 20.04 LTS. First, set up a single node Hadoop cluster on the system which enables you to use Hadoop Distributed File System (HDFS) and Hadoop MapReduce operations. 

## Prerequisites
- Java or OpenJDK must be installed. 
- OpenSSH must be installed; passwordless SSH connection with the localhost needs to be established as well.
- sudo privileges for the current user

### Installing OpenJDK
To check which Java version does Hadoop support, check https://cwiki.apache.org/confluence/display/HADOOP/Hadoop+Java+Versions. **Java 8** can be installed for the current Hadoop version 3.3.1. Run the following commands in the terminal. 

```
sudo apt update
sudo apt install openjdk-8-jdk -y

# check java version
java -version; javac -version
```
### Installing OpenSSH
Run the following command for installing the OpenSSH server and client.
```
sudo apt install openssh-server openssh-client -y
```
It is recommended to create a new user (without sudo privileges) on the system for running the Hadoop daemons. 

```
# add a new user with username hdoop (can be anything you choose)
sudo adduser hdoop

# switch user to hdoop
su - hdoop
```
**Enable passwordless SSH for hdoop**
Run all these lines separately and go through the prompts as required.
```
#Generate a public/private rsa key pair or SSH key pair
ssh-keygen -t rsa -P" -f ~/.ssh/id_rsa

#Store the generated key as an authorized key
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

#Set permissions for user hdoop
chmod 0600 ~/.ssh/authorized_keys

#check if the user has access to localhost
ssh localhost
```
Now that the prerequisites have been satisfied, a single node Hadoop cluster (pseudo-distributed mode) can be created on the system. 

## Install Hadoop 

Visit https://hadoop.apache.org/releases.html to check the release version of Hadoop currently being rolled out and get the download link for the **tar** binary package. 

```
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.1/hadoop-3.3.1.tar.gz
tar xzf hadoop-3.3.1.tar.gz
mv hadoop-3.3.1 hadoop
```
Now, the hadoop-3.3.1 binary files are located in the folder hadoop.

## Single Node Cluster (Pseudo-Distributed cluster)

This mode enables each Hadoop daemon to run as a single Java process. Following configuration files have to be modified to correctly configure the Hadoop environment -

- bashrc
- hadoop-env.sh
- core-site.xml
- hdfs-site.xml
- mapred-site.xml
- yarn-site.xml

**bashrc configuration** 
Open _.bashrc_ using nano text editor in the terminal.
```
nano .bashrc
```
Once open, copy the following to the end of the file for changing the PATH variable and add others. Save the file once done. 

```
export HADOOP_HOME=/home/hdoop/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS"-Djava.library.path=$HADOOP_HOME/lib/native"
```
To apply the changes to the current running environmen, use the following command in the terminal. 
```
source ~/.bashrc
```
**hadoop-env.sh configuration**
Before configuring _hadoop-env.sh_, check the location of Java binaries using the following commands. 
```
which javac
```
Copy the resulting path and execute:
```
# let the resulting path be /usr/bin/javac
readlink -f /usr/bin/javac
```
Copy the section of the path before _/bin/javac_. For my system, it is `/usr/lib/jvm/java-8-openjdk-amd64`.

Moving on to editing _hadoop-env.sh_ which configures YARN, HDFS, MapReduce etc. Open _hadoop-env.sh_ using `nano`. 

```
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```
Add the following line to the file to fix the Java version to be used for this single node Hadoop cluster. 

```
export JAVE_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```
**core-site.xml configuration**
_core-site.xml_ enables the user to specify the URL for the NameNode and a temporary directory required for the map and reduce process. Open the file using `nano`.

```
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```
Add the following to the file
```
<configuration>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>/home/hdoop/tmpdata</value>
  </property>
  <property>
    <name>fs.default.name</name>
    <value>hdfs://127.0.0.1:9000</value>
    </property>
</configuration>
```
Also create a directory where the temporary data was to stored for the map and reduce process. 
```
mkdir ~/hdoop/tmpdata
```
This creates `/hdoop/tmpdata` in the `HOME` directory as defined in _core-site.xml_. 

**hdfs-site.xml configuration**
Configure the location for storing node metadata, fsimage file and edit log file. Define NameNode and DataNode storage directories. Set _dfs.replication_ value of 3 to 1 since a single node cluster is being setup.

```
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```
Add the following lines to _hdfs-site.xml_
```
<configuration>
  <property>
    <name>dfs.data.dir</name>
    <value>/home/hdoop/dfsdata/namenode</value>
  </property>
  <property>
    <name>dfs.data.dir</name>
    <value>/home/hdoop/dfsdata/datanode</value>
   </property>
   <property>
    <name>dfs.replication</name>
    <value>1</value>
   </property>
</configuration>
```
Create the directory specified for `dfs.data.dir` in the system
```
mkdir ~/hdoop/dfsdata/namenode
```
**mapred-site.xml configuration**
Open _mapred-site.xml_ and set the MapReduce framework to YARN. 
```
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```
Add the following lines to _mapred-site.xml_
```
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
```
**yarn-site.xml configuration**
Configure **NodeManager**, **Resource Manager**, **Containers** and **Application Master**. 

```
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```
Add the following to _yarn-site.xml_
```
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>127.0.0.1</value>
  </property>
  <property>
    <name>yarn.acl.enable</name>
    <value>0</value>
  </property>
  <property>
    <name>yarn.nodemanager.env-whitelist</name>   
    <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PERPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
  </property>
</configuration>
```
Now, all the required files have been configured properly for the pseudo-distributed mode. Before starting Hadoop services, it is necessary to format the **NameNode**. 
```
hdfs namenode -format
```
`SHUTDOWN_MSG` shows up once the formatting is finished. 

## Start the Hadoop Cluster

The shell files `start-dfs.sh` and `start-yarn.sh` can be found in the directory `/home/hadoop/sbin` but since this directory has already been added to the `PATH` variable, they can be executed directly without navigating to the said directory. 

```
#Run NameNode, DataNode and secondary namenode
start-dfs.sh

#Run resource manager and node manager
start-yarn.sh

#Check if all the daemons are running using the following command
jps
```
## Hadoop UI

The Hadoop user interface can be accessed using a browser with different addresses. 

**NameNode UI** : http://localhost:9870

**Individual DataNodes** : http://localhost:9864

**YARN Resource Manager** : http://localhost:8088

### WIP
