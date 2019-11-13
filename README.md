## Back up running VirtualBox machines without turning them off

Steps
- `[Warning]` Removes all current snapshots
- Creates a live snapshot
- Creates a clone of the snapshot
- Copies the clone to the folder you specify

### Examples
Nix
`python3 vbox_backup.py debian-test1 debian-test2 -b /home/christian/vm_backups -v /home/christian/"VirtualBox VMs"`

Win
`python vbox_backup.py empty-test -b C:/Users/chall/Documents/vm_backups -v C:/Users/chall/"VirtualBox VMs"`

### Arguments
`positional`: Specify which machines you would like to back up
`-b`: Back up directory to copy newly created clone to, will create a unique folder for each machine
`-v`: The directory the virtual box machines currently reside

