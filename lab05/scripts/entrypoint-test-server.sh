#!/bin/bash
set -e
# Scrie cheia publica a utilizatorului "ansible" in authorized_keys
if [ -n "$ANSIBLE_SSH_PUBKEY" ]; then
    echo "$ANSIBLE_SSH_PUBKEY" > /home/ansible/.ssh/authorized_keys
    chown ansible:ansible /home/ansible/.ssh/authorized_keys
    chmod 600 /home/ansible/.ssh/authorized_keys
fi
exec /usr/sbin/sshd -D -e
