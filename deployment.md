The software is deployed on a Raspberry Pi. To decrease the risk of disk 
corruption, the file system is mounted read-only. To switch between the read-only and read-write modes, use the commands "rw" and "ro". Thes command are aliases:
alias ro='sudo mount -o remount,ro / ; fs_mode=$(mount | sed -n -e "s/^\/dev\/root on \/ .*(\(r[w|o]\).*/\1/p")'
alias rw='sudo mount -o remount,rw / ; fs_mode=$(mount | sed -n -e "s/^\/dev\/root on \/ .*(\(r[w|o]\).*/\1/p")'

