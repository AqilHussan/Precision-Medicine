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
# add a new user with username pma (can be anything you choose)
sudo adduser pma

# switch user to pma
su - pma
```
**Enable passwordless SSH for pma**
Run all these lines separately and go through the prompts as required.
```
#Generate a public/private rsa key pair or SSH key pair
ssh-keygen -t rsa -P ""

# Press Enter to choose to save the key in the given directory, otherwise enter new directory

#Store the generated key as an authorized key
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

#Set permissions for user pma
chmod 0600 ~/.ssh/authorized_keys

#check if the user has access to localhost
ssh localhost
```
Now that the prerequisites have been satisfied, a single node Hadoop cluster (pseudo-distributed mode) can be created on the system. 

## Install Hadoop 

Visit https://hadoop.apache.org/releases.html to check the release version of Hadoop currently being rolled out and get the download link for the **tar** binary package. 

```
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.2/hadoop-3.3.2.tar.gz
tar xzf hadoop-3.3.2.tar.gz
mv hadoop-3.3.2 hadoop
```
Now, hadoop-3.3.2 binary files are located in the folder hadoop.

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
export HADOOP_HOME=/home/pma/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
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
    <value>/home/pma/tmpdata</value>
  </property>
  <property>
    <name>fs.default.name</name>
    <value>hdfs://127.0.0.1:9000</value>
  </property>
</configuration>
```
Also create a directory where the temporary data was to stored for the map and reduce process. 
```
mkdir /home/pma/tmpdata
```
This creates `tmpdata` in the `HOME` directory as defined in _core-site.xml_. 

**hdfs-site.xml configuration**
Configure the location for storing node metadata, fsimage file and edit log file. Define NameNode and DataNode storage directories. Set _dfs.replication_ value of 3 to 1 since a single node cluster is being setup.

```
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```
Add the following lines to _hdfs-site.xml_
```
<configuration>
  <property>
    <name>dfs.namenode.data.dir</name>
    <value>/home/pma/dfsdata/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>/home/pma/dfsdata/datanode</value>
   </property>
   <property>
    <name>dfs.replication</name>
    <value>1</value>
   </property>
</configuration>
```
Create the directories specified above
```
mkdir /home/pma/dfsdata
mkdir /home/pma/dfsdata/datanode
mkdir /home/pma/dfsdata/namenode
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

To monitor HDFS cluster, use `hdfs dfsadmin -report`
To monitor YARN resources use `yarn node -list` and `yarn application -list`

## Installing Spark

Navigate to the home directory and run 
```
wget https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz
tar xzf spark-3.2.1-bin-hadoop3.2.tgz
mv spark-3.2.1-bin-hadoop3.2 spark
```
The above commands will move all **Spark** binaries to folder _spark_ in the home directory of the current user. 

Setup Spark bin and Hadoop environment variables in _.bashrc_ 

```
export PATH =/home/pma/spark/bin:$PATH
export HADOOP_CONF_DIR=/home/pma/hadoop/etc/hadoop
export SPARK_HOME=/home/pma/spark
export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native:$LD_LIBRARY_PATH
```
**Rename** Spark default template config file

```
mv $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf
```

Set `spark.master` to YARN in `$SPARK_HOME/conf/spark-defaults.conf` and add the rest of the lines as mentioned below

```
spark.master yarn

spark.eventLog.enabled true
spark.eventLog.dir hdfs://127.0.0.1:9000/spark-logs

spark.history.provider org.apache.spark.deploy.history.FsHistoryProvider
spark.history.fs.logDirectory hdfs://127.0.0.1:9000/spark-logs
spark.history.fs.update.interval 10s
spark.history.ui.port 18080
```

Add the following to `$HADOOP_HOME/etc/hadoop/yarn-site.xml` to fix java8 + YARN issue.

```
<property>
  <name>yarn.nodemanager.pmem-check-enabled</name>
  <value>false</value>
</property>

<property>
  <name>yarn.nodemanager.vmem-check-enabled</name>
  <value>false</value>
</property>
```
### Running History server, Spark-shell and PySpark

```
hdfs dfs -mkdir /spark-logs
cd $SPARK_HOME/sbin
./start-history-server.sh
```
The web interface can accessed using http://127.0.0.1:18080

Run spark-shell by simply entering `spark-shell` in the terminal. Similary, for Pyspark use `pyspark`. 
