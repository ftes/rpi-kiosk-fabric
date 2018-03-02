from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import upload_template
from fabric.contrib.console import confirm
from fabric.operations import local

home_dir = "/home/pi"
code_dir = home_dir + "/node-server"
ssh_dir = home_dir + "/.ssh"

local_url = "http://localhost:3000"
git_repo = "git@github.com:..."
apt_packages = "unattended-upgrades apt-listchanges xserver-xorg x11-xserver-utils xinit openbox git nodejs npm chromium-browser xdotool"
service_name = "node"
update_interval_minutes = 4
refresh_interval_minutes = 25

def install(sonar_token):
    sys_update()
    sys_install()
    sys_configure_openbox()
    sys_configure_x_server()
    sys_add_service(sonar_token)
    add_update_script()
    sys_set_cron()
    sys_add_ssh_key()
    sys_print_ssh_key()
    prompt("Add the SSH public key printed above as a deploy key to the repo. Press [Enter] to continue.")
    git_clone()
    npm_install()
    sys_enable_service()
    sys_start_service()

def update():
    git_pull()
    npm_install()
    sys_restart_service()

def prompt(output):
    local("echo '%s'" % output)
    local("read")

def sys_update():
    sudo("apt -y update && sudo apt -y upgrade")

def sys_install():
    sudo("apt -y install --no-install-recommends %s" % apt_packages)

def sys_add_service(sonar_token):
    context = { "code_dir": code_dir, "sonar_token": sonar_token }
    upload_template("systemd.service", "/etc/systemd/system/%s.service" % service_name, use_sudo=True, context=context)

def sys_configure_openbox():
    context = { "local_url": local_url }
    upload_template("openbox.conf", "/etc/xdg/openbox/autostart", use_sudo=True, context=context)

def sys_add_ssh_key():
    run("mkdir -p " + ssh_dir)
    run("ssh-keygen -N \"\" -f %s/id_rsa" % ssh_dir)
    upload_template("known_hosts", "%s/known_hosts" % ssh_dir, mirror_local_mode=True)

def sys_print_ssh_key():
    run("cat %s/id_rsa.pub" % ssh_dir)

def sys_enable_service():
    sudo("systemctl enable %s" % service_name)

def sys_start_service():
    sudo("systemctl start %s" % service_name)

def sys_restart_service():
    sudo("systemctl restart %s" % service_name)

def sys_status_service():
    sudo("systemctl status %s" % service_name)

def sys_add_cron(line):
    run("(crontab -l 2>/dev/null; echo '%s') | crontab -" % line)

def sys_set_cron():
    run("crontab -r", warn_only=True) # remove old config
    context = { "home_dir": home_dir, "update_interval_minutes": update_interval_minutes, "refresh_interval_minutes": refresh_interval_minutes }
    upload_template("crontab", "%s/crontab" % home_dir, context=context)
    run("crontab crontab")

def sys_configure_x_server():
    upload_template(".bash_profile", "%s/.bash_profile" % home_dir)

def git_clone():
    with cd(home_dir):
        run("git clone %s" % git_repo)

def git_pull():
    with cd(code_dir):
        run("git pull")

def npm_install():
    with cd(code_dir):
        run("npm install")

def add_update_script():
    context = { "service_name": service_name, "code_dir": code_dir }
    upload_template("update.sh", "%s/update.sh" % home_dir, mirror_local_mode=True, context=context)
