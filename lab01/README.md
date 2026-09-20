# Lab 01 - Directory Backup

## Description

The `backup.sh` script is a Bash script that creates a compressed backup of a specified directory.

The script creates a `.tar.gz` archive and adds the current date and time to the archive filename.

## Usage

```bash
./backup.sh <source_directory> [backup_directory]
```

### Arguments

* `source_directory` - required argument. Specifies the directory that should be backed up.
* `backup_directory` - optional argument. Specifies where the backup should be saved. If this argument is not provided, `/backup` is used as the default directory.

## Examples

Create a backup of `/home/user/Documents` using the default `/backup` directory:

```bash
./backup.sh /home/user/Documents
```

Create a backup and save it to `/home/user/backups`:

```bash
./backup.sh /home/user/Documents /home/user/backups
```

## Output

The script creates an archive with the following format:

```text
directory_name_YYYY-MM-DD_HH-MM-SS.tar.gz
```

For example:

```text
source_2026-09-20_21-23-48.tar.gz
```

## Error Handling

The script checks:

* whether the correct number of arguments was provided;
* whether the source directory exists;
* whether the backup directory exists;
* whether the backup archive was created successfully.

If an error occurs, an appropriate error message is displayed and the script terminates.

## Requirements

The script requires:

* Linux;
* Bash;
* GNU tar.
