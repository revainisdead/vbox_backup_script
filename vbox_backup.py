from typing import List

import argparse
import os
import subprocess
import uuid

from datetime import datetime


def get_snapshot_uuids(mach: str) -> List[str]:
    # Get current snapshots to remove them all
    vbox_snaps_list_process =  subprocess.Popen(['VBoxManage', 'snapshot', mach, 'list'], stdout=subprocess.PIPE)
    snapshots = vbox_snaps_list_process.communicate()

    # Get just the names returned
    snapshots_bytes = snapshots[0]
    snapshots_output = snapshots_bytes.decode('utf-8')

    # Output example: '  Name: empty-test-backup (UUID: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa)\r\n'
    snap_uuids_prune = snapshots_output.split('UUID: ')
    # Get rid of first entry
    snap_uuids_prune.pop(0)

    snapshots = []
    uuid_length = 36
    for snap_uuid in snap_uuids_prune:
        snapshots.append(snap_uuid[0:uuid_length])

    # Kill Popen process when done
    vbox_snaps_list_process.kill()

    for snap in snapshots:
        # Verify we have found an actual UUID
        try:
            uuid.UUID(snap, version=4)
        except ValueError:
            print('UUIDs from VBoxManage list command were retrieved incorrectly.')
            raise

    print(snapshots)
    return snapshots


def create_snapshot(mach: str, backup_dir: str):
    snapshots = get_snapshot_uuids(mach)

    for snap in snapshots:
        subprocess.call(['VBoxManage', 'snapshot', mach, 'delete', snap], stdout=subprocess.PIPE)

    now = datetime.now()
    datetimeReadable = now.strftime('%I-%m-%S-%m_%d_%Y')

    # Take a live snapshot of the vm
    backup_name = '{0}-backup-{1}'.format(mach, datetimeReadable)
    subprocess.call(['VBoxManage', 'snapshot', mach, 'take', backup_name], stdout=subprocess.PIPE)
    #subprocess.call(['VBoxManage', 'snapshot', mach, 'take', backup_name, '--live'], stdout=subprocess.PIPE)

    # Verify snapshot was made by requerying
    snapshots = get_snapshot_uuids(mach)
    try:
        new_snapshot = snapshots[0]
    except KeyError:
        print('New snapshot \'{}\' was not created. Abort'.format(backup_name))
        raise

    # Create VM clone from snapshot
    subprocess.call(['VBoxManage', 'clonevm', mach, '--snapshot', new_snapshot, '--name', backup_name])
    # '--options', 'keepallmacs'
    # '--options', 'keephwuuids'
    # '--options', 'keepdisknames'

    # Make a designated Clones folder for each vm inside the backup folder
    mach_clones_dir = os.path.join(backup_dir, '{}-Clones'.format(mach))

    print(mach_clones_dir)
    if not os.path.exists(mach_clones_dir):
        os.makedirs(mach_clones_dir)

    # Copy clone to the backup_dir
    # (using ftp?)



# testing on linux
# VBoxManage snapshot debian-small take test_snapshot1
# VBoxManage snapshot debian-small list

# python3 vbox_backup.py debian-test1 debian-test2 -b /home/christian/vm_backups

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('machines', type=str, nargs='+', help="Virtual Box machines to back up.")
    parser.add_argument('-b', '--backup_directory', help="Directory to send backups to.")
    args = parser.parse_args()

    print(args.machines)
    print(args.backup_directory)

    # Verify that each machine is an actual folder in the default virtual box location, or ask for location of vms
    # C:\Users\{user}\'VirtualBox VMs'

    for mach in args.machines:
        create_snapshot(mach, args.backup_directory)


if __name__ == "__main__":
    main()
