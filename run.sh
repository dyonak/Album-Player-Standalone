#!/bin/bash
#exec service rpcbind start &
#exec service nfs-kernel-server start & 
exec python3 ./Webapp.py &
exec python3 ./AlbumPlayer.py