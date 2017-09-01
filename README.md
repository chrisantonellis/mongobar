## mongobar
mongobar is a python shell script used to create and manage MongoDB backups.  
Internally it is a wrapper for the **mongodump** and **mongorestore** commands.  

## Installation
```
pip install git+git://github.com/chrisantonellis/mongobar.git
```
## Usage
* Run `mongobar` in a terminal

## Configuration Setup
* Copy `.mongobar_config.json` to `~/.mongobar_config.json`
* Edit the configuration to meet your needs

## HELP!!
* (Almost) everything is explained in the `-h --help` commands
* Access help via `mongobar -h`
* Access help for an action by typing `mongobar <action> -h`

## Examples

#### Backups
List all backups. Backups are assigned a unique name when created.
![backups](https://i.imgur.com/O3AxGMF.png)  

#### Backup metadata
View metadata for a backup. Metadata is created when a backup is created.
![meta](https://i.imgur.com/TarD8xB.png)

#### Server metadata
View metadata for a server.
![server](https://i.imgur.com/45JOCbF.png)

#### Host Directories
View backup host directories. Backups are automatically separated by host.
![meta](https://i.imgur.com/bgKE62C.png)

#### Configuration
View configuration data.
![meta](https://i.imgur.com/h9c0ytR.png)
