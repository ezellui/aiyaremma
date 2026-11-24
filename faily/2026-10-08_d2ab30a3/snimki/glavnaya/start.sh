#!/bin/bash
S=/tmp/claude-0/-home-claude/7173b229-aa2b-56f5-8c29-d70c9d405cc9/scratchpad/runner
kill $(pgrep -f "java.*Run /root") 2>/dev/null; sleep 1
mkdir -p $S/lib; rm -f $S/lib/*
J=/usr/share/java
for m in server http io util util-ajax servlet security webapp xml annotations plus jndi apache-jsp; do cp -L $J/jetty9-$m.jar $S/lib/; done
for f in servlet-api-3.1 tomcat9-jasper tomcat9-jasper-el tomcat9-el-api tomcat9-jsp-api tomcat9-juli tomcat9-util tomcat9-util-scan tomcat9-api eclipse-jdt-core asm asm-commons asm-tree saxonb saxonb-dom saxonb-xpath; do cp -L $J/$f.jar $S/lib/; done
CP=$(ls $S/lib/*.jar | tr '\n' ':')
cd /root
setsid nohup java -Xmx1024m -cp "$S:$CP:/root/eldamo/build/classes" Run /root/eldamo/src/main/webapp /root/eldamo/build/classes > $S/jetty.log 2>&1 < /dev/null &
