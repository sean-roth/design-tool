# System Audit Request

**From:** Designer (Claude Desktop)  
**To:** Engineer (Claude Code)  
**Date:** 2025-11-06

## Purpose

Before we build the PenPot AI bridge, I need a complete understanding of your server environment. This audit will inform all architectural and implementation decisions.

Please complete this audit and create `AUDIT-RESULTS.md` with your findings.

---

## 1. Server Specifications

### Hardware
- [ ] CPU: Model and core count
- [ ] RAM: Total and currently available
- [ ] Disk: Total space, free space, and mount points
- [ ] Network: Local IP address and subnet

### Operating System
- [ ] Distribution and version: `cat /etc/os-release`
- [ ] Kernel version: `uname -r`
- [ ] Uptime: `uptime`

---

## 2. PenPot Installation

### Installation Details
- [ ] How is PenPot installed? (Docker, native, other)
- [ ] PenPot version: Check in UI or logs
- [ ] Installation directory path
- [ ] How is it started/stopped?
- [ ] Is it currently running? `systemctl status` or `docker ps`

### Access Information
- [ ] Access URL/IP and port
- [ ] Can you access it from localhost?
- [ ] Can you access it from the Windows machine?
- [ ] Authentication: Admin credentials set up?

### Configuration
- [ ] Location of config files
- [ ] Any custom settings or modifications?
- [ ] Database type and location
- [ ] File storage location

---

## 3. Development Environment

### Installed Tools
- [ ] Docker: `docker --version`
- [ ] Docker Compose: `docker-compose --version`
- [ ] Node.js: `node --version`
- [ ] npm: `npm --version`
- [ ] Python: `python3 --version`
- [ ] pip: `pip3 --version`
- [ ] Git: `git --version`

### Not Installed But Available?
- [ ] Can you install packages via apt/yum/dnf?
- [ ] Do you have sudo access?
- [ ] Any installation restrictions?

---

## 4. Network Configuration

### Local Network
- [ ] Server IP address: `ip addr show`
- [ ] Network interface name: `ip link show`
- [ ] Subnet mask and gateway
- [ ] Can ping Windows machine? What's its IP?

### Port Availability
- [ ] Currently used ports: `ss -tulpn` or `netstat -tulpn`
- [ ] Are these ports available:
  - [ ] 3000 (typical Node.js)
  - [ ] 5000 (typical Python/Flask)
  - [ ] 8080 (alternative HTTP)
  - [ ] 9090 (alternative)

### Firewall
- [ ] Firewall status: `sudo ufw status` or `sudo firewall-cmd --state`
- [ ] Any blocked ports?
- [ ] Can you open ports if needed?

---

## 5. Existing Services

### What's Running?
- [ ] List all active services: `systemctl list-units --type=service --state=running`
- [ ] List all Docker containers: `docker ps -a`
- [ ] Any web servers? (nginx, Apache)
- [ ] Any databases? (PostgreSQL, MySQL, MongoDB)

### Resource Usage
- [ ] Current CPU usage: `top` or `htop`
- [ ] Current memory usage: `free -h`
- [ ] Current disk usage: `df -h`
- [ ] Any resource bottlenecks?

---

## 6. PenPot Plugin Capability

### Plugin System
- [ ] Have you used PenPot plugins before?
- [ ] Where are plugins located? Check PenPot docs or installation
- [ ] Can you access the PenPot Plugin Manager in the UI?
- [ ] Test: Can you install a sample plugin from PenPot's examples?

### Plugin Development Setup
- [ ] Do we need to set up a local dev environment for the plugin?
- [ ] Where would the plugin be served from during development?
- [ ] How do we install a custom plugin?

---

## 7. Security and Access

### Authentication
- [ ] How is PenPot authentication configured?
- [ ] Can we create API tokens?
- [ ] Any OAuth or SSO configured?

### HTTPS/SSL
- [ ] Is PenPot running on HTTPS?
- [ ] Self-signed cert or legitimate cert?
- [ ] Would HTTP be acceptable for local network?

---

## 8. Integration Points

### Compel English
- [ ] Where is Compel English located? (directory path)
- [ ] How is it deployed? (PM2, systemd, Docker)
- [ ] What port does it run on?
- [ ] Would design work affect the running app?

### Future Considerations
- [ ] Any other projects or services on this server?
- [ ] Any planned infrastructure changes?
- [ ] Storage limitations for design files?

---

## 9. Preferences and Constraints

### Technical Preferences
- [ ] Python or Node.js for the MCP server? (or either is fine)
- [ ] Any language/framework restrictions?
- [ ] Preference for Docker vs native installation?

### Operational Constraints
- [ ] Any maintenance windows or downtime concerns?
- [ ] Backup procedures we should be aware of?
- [ ] Monitoring or logging requirements?

---

## 10. Quick Tests

### Connectivity Test
- [ ] From server, can you `curl http://localhost:[PENPOT_PORT]`?
- [ ] From Windows machine, can Sean access PenPot in browser?
- [ ] Can you create a simple test file and serve it via HTTP?
  - Create: `echo "test" > test.html`
  - Serve: `python3 -m http.server 8888`
  - Access from Windows: `http://[SERVER_IP]:8888/test.html`

### Permission Test
- [ ] Can you write to `/tmp`?
- [ ] Can you write to `/opt` or `/usr/local`?
- [ ] Can you create systemd services?
- [ ] Can you modify firewall rules?

---

## Deliverable

Please create `AUDIT-RESULTS.md` with:
1. All checkbox items completed with actual values
2. Any error messages or issues encountered
3. Screenshots if helpful (PenPot UI, running services, etc.)
4. Your recommendations based on what you found
5. Any concerns or potential blockers

**Format Example:**
```markdown
## 1. Server Specifications

### Hardware
- **CPU:** Intel Xeon E5-2680 v4, 28 cores
- **RAM:** 64 GB total, 48 GB available
- **Disk:** 500 GB total, 350 GB free, mounted at /
- **Network:** 192.168.1.100/24

### Operating System
- **Distribution:** Ubuntu 22.04.3 LTS
- **Kernel:** 5.15.0-91-generic
- **Uptime:** 23 days
```

---

## Timeline

Please complete this audit at your earliest convenience. Once I have your results, I'll write the implementation specifications and we can start building.

Thanks!

— Designer
