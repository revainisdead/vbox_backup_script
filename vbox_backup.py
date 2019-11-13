from typing import List

import argparse
import os
import shutil
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

    return snapshots


def create_snapshot(mach: str, backup_dir: str):
    snapshots = get_snapshot_uuids(mach)

    print('Deleting all old snapshots')
    for snap in snapshots:
        subprocess.call(['VBoxManage', 'snapshot', mach, 'delete', snap], stdout=subprocess.PIPE)

    now = datetime.now()
    datetimeReadable = now.strftime('%I-%M-%S-%m_%d_%Y')

    backup_name = '{0}-backup-{1}'.format(mach, datetimeReadable)
    print('Creating live snapshot of VM')
    subprocess.call(['VBoxManage', 'snapshot', mach, 'take', backup_name, '--live'], stdout=subprocess.PIPE)

    # Verify snapshot was made by requerying
    snapshots = get_snapshot_uuids(mach)
    try:
        new_snapshot = snapshots[0]
    except KeyError:
        print('New snapshot \'{}\' was not created. Abort'.format(backup_name))
        raise
    print('Newly created snapshot UUID for {} is {}'.format(mach, new_snapshot))

    return backup_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('machines', type=str, nargs='+', help="Virtual Box machines to back up.")
    parser.add_argument('-b', '--backup_directory', help="Directory to send backups to.")
    parser.add_argument('-v', '--virtualbox_directory', help="Virtual Box directory, to grab created clones.")
    args = parser.parse_args()

    machines = args.machines
    backup_directory = args.backup_directory
    virtualbox_directory = args.virtualbox_directory

    for mach in machines:
        # Before running VBoxManage commands, ensure the VM exists.
        if not os.path.exists(os.path.join(virtualbox_directory, mach)):
            print('Machine name {} does not exist. Trying next name given.'.format(mach))
            continue

        snapshot_name = create_snapshot(mach, backup_directory)

        print('Creating VM clone from snapshot')
        subprocess.call(['VBoxManage', 'clonevm', mach, '--snapshot', snapshot_name, '--name', snapshot_name])
        # '--options',
        #   'keepallmacs'
        #   'keephwuuids'
        #   'keepdisknames'

        # Make a designated Clones folder for each vm inside the backup folder
        mach_backup_dir = os.path.join(backup_directory, '{}-Clones'.format(mach))

        print('{} clones saved to {}'.format(mach, mach_backup_dir))
        if not os.path.exists(mach_backup_dir):
            os.makedirs(mach_backup_dir)

        clone_dir = os.path.join(virtualbox_directory, snapshot_name)

        snapshot_with_ext = '{}{}'.format(snapshot_name, '.vdi')

        clone = os.path.join(clone_dir, snapshot_with_ext)
        cp_dest = os.path.join(mach_backup_dir, snapshot_with_ext)

        print('Copying clone to that directory . . .')
        shutil.copy(clone, cp_dest)

        print('Done.\n')


if __name__ == "__main__":
    main()
