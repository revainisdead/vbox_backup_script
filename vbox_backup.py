import argparse
import os
import subprocess

from datetime import datetime


def create_snapshot(mach, backup_dir):
    # Make a designated Snapshot folder for each vm
    mach_snapshots_dir = backup_dir + '/{}-Snapshots'.format(mach)

    print(mach_snapshots_dir)
    if not os.path.exists(mach_snapshots_dir):
        os.makedirs(mach_snapshots_dir)

        # Designate the snapshot folder for each vm
        # If this is called when there are already snapshots, an error is thrown,
        # so only call this when the directory is first created.
        subprocess.call(['VBoxManage', 'modifyvm', mach, '--snapshotfolder', mach_snapshots_dir], stdout=subprocess.PIPE)

    now = datetime.now()
    datetimeReadable = now.strftime('%I-%m-%S-%m_%d_%Y')

    # Take a live snapshot of the vm
    subprocess.call(['VBoxManage', 'snapshot', mach, 'take', '{0}-backup-{1}'.format(mach, datetimeReadable), '--live'], stdout=subprocess.PIPE)

    # Verify snapshot was made
    # list_process =  subprocess.Popen(['VBoxManage', 'snapshot', mach, 'list'], stdout=subprocess.PIPE)
    # snapshots = list_process.communicate()

    # Delete old snapshots so they don't accumulate on vm
    # - get output from list command
    # - Use Popen, stdout to PIPE, then p.communicate() to read
    # - either check timestamp and delete old snapshots or just delete them all
    # - supply snapshot name or UUID to delete call
    # subprocess.call(['VBoxManage', 'snapshot', mach, 'delete', {snapshot_name}], stdout=subprocess.PIPE)



# testing on linux
# VBoxManage snapshot debian-small take test_snapshot1
# VBoxManage snapshot debian-small list

# python3 vbox_backup.py debian-test1 debian-test2 -b /home/christian/vm_backups

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('machines', type=str, nargs='+', help="Virtual Box machines to back up, list out all VM directories")
    parser.add_argument('-b', '--backup_directory', help="Directory to send backups to. Don't include trailing slash.")
    args = parser.parse_args()

    print(args.machines)
    print(args.backup_directory)

    # Verify that each machine is an actual folder in the default virtual box location, or ask for location of vms
    # C:\Users\{user}\'VirtualBox VMs'

    for mach in args.machines:
        create_snapshot(mach, args.backup_directory)


if __name__ == "__main__":
    main()
