# Purged Files

This folder contains files that have been moved out of the main codebase because they are obsolete, outdated, or no longer relevant to the current project state.

## Date: 2025-11-12

## Files Moved

### Documentation (purge/docs/)

1. **SYNCTHING-SETUP.md**
   - Development-specific workflow documentation for syncthing
   - Reason: Syncthing was a temporary development workflow tool, not needed for production deployment

2. **DEVELOPMENT-WORKFLOW.md**
   - Development server-specific workflow (orche-dev.goxtt.net)
   - Reason: Specific to a particular development server setup, not relevant for general users or production

3. **COMPLETED-FEATURES.md**
   - Historical implementation summary documenting WireGuard and Web CLI features
   - Reason: Superseded by CLAUDE.md which contains current project overview and architecture

4. **INSTALL-COMMANDS.md**
   - Command-by-command installation reference
   - Reason: Redundant with DEPLOYMENT.md which provides comprehensive deployment guide

5. **QUICKSTART.md**
   - Quick start guide with outdated manual setup information
   - Reason: Contains conflicting information with DEPLOYMENT.md; manual setup approach superseded by automated deployment

6. **CONFIG-ftnt.md** (FortiGate Configuration)
   - Detailed FortiGate configuration YAML examples
   - Reason: Old configuration approach; current architecture uses vendor translators with YAML abstraction layer as described in CLAUDE.md

7. **CONFIG-tik.md** (MikroTik Configuration)
   - Detailed MikroTik configuration YAML examples
   - Reason: Old configuration approach; current architecture uses vendor translators with YAML abstraction layer

8. **CONFIG-ubnt.md** (Ubiquiti Configuration)
   - Detailed Ubiquiti configuration YAML examples
   - Reason: Old configuration approach; current architecture uses vendor translators with YAML abstraction layer

9. **CONFIG-wg.md** (WatchGuard Configuration)
   - Detailed WatchGuard configuration YAML examples
   - Reason: Old configuration approach; current architecture uses vendor translators with YAML abstraction layer

### Scripts (purge/scripts/)

1. **setup-syncthing-server.sh**
   - Syncthing server setup automation
   - Reason: Syncthing was a development workflow tool, not part of production deployment

2. **sync-to-dev.sh**
   - Rsync-based sync to development server (orche-dev.goxtt.net)
   - Reason: Specific to a particular development server, not generally useful

3. **deploy-to-dev.sh**
   - Git-based deployment to development server
   - Reason: Specific to a particular development server setup

4. **watch-and-deploy.sh**
   - File watcher for automatic deployment
   - Reason: Development-specific tool tied to particular server setup

### Syncthing Files (purge/syncthing/)

1. **.stignore**
   - Syncthing ignore patterns file
   - Reason: Syncthing-specific configuration, not needed without syncthing

2. **.stfolder/** (deleted - was empty)
   - Syncthing folder marker
   - Reason: Syncthing-specific metadata, not needed

## Current Documentation Structure

After this cleanup, the main documentation consists of:

- **README.md** - Project overview and getting started
- **CLAUDE.md** - Comprehensive project documentation for AI assistants
- **DEPLOYMENT.md** - Production deployment guide for Debian 13
- **CONFIG.md** - General configuration guide for YAML abstraction layer
- **TESTING.md** - Testing procedures
- **TROUBLESHOOTING.md** - Common issues and solutions
- **COMMANDS.md** - Command reference
- **IMPLEMENTATION-SUMMARY.md** - Implementation details and architecture

## Current Scripts Structure

Production and development scripts:

- **setup.sh** / **setup.bat** - Initial project setup
- **start.sh** / **start.bat** - Start all services
- **start-backend.sh** / **start-backend.bat** - Start backend only
- **start-frontend.sh** / **start-frontend.bat** - Start frontend only
- **stop.sh** - Stop all services
- **deploy/install.sh** - Production deployment script

## Recovery

If any of these files are needed in the future, they can be recovered from:
1. This purge folder
2. Git history (commit before the purge)

## Notes

The project has evolved significantly since initial development. The current architecture uses:
- WireGuard VPN for secure device management
- Phone-home architecture (devices initiate connections)
- Vendor abstraction layer with translators
- Automated provisioning scripts
- Production deployment via deploy/install.sh

The purged files represent earlier approaches and development-specific workflows that are no longer part of the production system.
