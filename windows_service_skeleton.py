"""
At the commandline you run python_service_name.py start|stop|restart
It will require a command prompt/powershell with admin privileges

"""

import win32event
import win32service
import win32serviceutil


class AppServerSvc(win32serviceutil.ServiceFramework):
	# Required Attributes, _svc_name_ and _svc_display_name_
	# you can START/STOP the service at the commandline by the following name
	_svc_name_ = "TestService"
	# this text shows up as the service name in the Service  
        # Control Manager (SCM), type in services in the start menu in windows 7 or 10.
	_svc_display_name_ = "Test Service"

	def __init__(self, args):
		# base class to build services from
		# self is the name of the program and args is either start|stop|restart|install|debug|etc...
		win32serviceutil.ServiceFramework.__init__(self,args)
		# create an event to listen for stop requests on
		self.hWaitStop = win32event.CreateEvent(None,0,0,None)

	def SvcStop(self):
		# SvcStop is a special name, Don't change
		# tell the SCM we're shutting down  
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		# fire the stop event
		win32event.SetEvent(self.hWaitStop)

	def SvcDoRun(self):
		# SvcDoRun is a special name, Don't change
		# below here start running your normal code or you could create a main() function
		pass
    
    
if(__name__ == "__main__"):
	# win32serviceutil.HandleCommandLine allows services to process the command line
	# standard commands such as 'start', 'stop', 'debug', 'install' etc. 
	# Notice we're not using sys.argv or argparse
	win32serviceutil.HandleCommandLine(AppServerSvc)
	
