#!/bin/bash

# start mongo without auth
mongod --fork --logpath /var/log/mongodb.log

# create backup and restore user
mongo admin --eval '
db.createUser({
  user: "backup_restore_user",
  pwd: "password",
  roles: [{
    role: "backup",
    db: "admin"
  },{
    role: "restore",
    db: "admin"
  }]
})'

# stop mongo
mongo admin --eval "db.shutdownServer()"

# start mongo with auth
mongod --fork --logpath /var/log/mongodb.log --auth

tail -f /dev/null