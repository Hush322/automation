#!/bin/bash

# Check the number of arguments
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <source_directory> [backup_directory]"
    exit 1
fi

SOURCE_DIR="$1"
BACKUP_DIR="${2:-/backup}"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

# Check if the backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: Backup directory '$BACKUP_DIR' does not exist."
    exit 1
fi

# Get current date and time
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Get the name of the source directory
DIR_NAME=$(basename "$SOURCE_DIR")

# Define the archive name
ARCHIVE="$BACKUP_DIR/${DIR_NAME}_${DATE}.tar.gz"

# Create the backup
tar -czf "$ARCHIVE" -C "$(dirname "$SOURCE_DIR")" "$DIR_NAME"

# Check if the backup was created successfully
if [ $? -eq 0 ]; then
    echo "Backup successfully created:"
    echo "$ARCHIVE"
else
    echo "Error: Failed to create backup."
    exit 1
fi
