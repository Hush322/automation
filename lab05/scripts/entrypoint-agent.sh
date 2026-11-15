#!/bin/bash
set -e
# Scrie cheia publica primita prin variabila de mediu in authorized_keys
if [ -n "$JENKINS_AGENT_SSH_PUBKEY" ]; then
    echo "$JENKINS_AGENT_SSH_PUBKEY" > /home/jenkins/.ssh/authorized_keys
    chown jenkins:jenkins /home/jenkins/.ssh/authorized_keys
    chmod 600 /home/jenkins/.ssh/authorized_keys
fi
exec /usr/sbin/sshd -D -e
