# -*- coding: utf-8 -*-
'''
Get configuration information from configuration files and from the command
line.

The following configuration file locations are supported and are searched in
the order given below. The first definition found for a particular entry wins:
    - The application working directory. This is where the application
      bootstrap script is loaded from
      File name: <path>/.agiconfig
    - The User's home directory
      File name: ~/.agiconfig
    - The system configuration directory.
      On Linux or OS/X this is /etc
      On Windows it is %ALLUSERSPROFILE%
      File name: <path>/agiconfig
Created on 2010-09-16

@author: jonathan
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ConfigParser
import petaapan.utilities.argparse

import sys
from string import capitalize #IGNORE:W0402
import logging.config
from os import X_OK
from os.path import join, exists, expanduser, expandvars, realpath, split,\
                    splitdrive
import petaapan.utilities.envpath
from petaapan.utilities.config_validation import ValidateExistingDirectory,\
                                                 ValidateExistingFile


# The Python logger that will be used by all parts of the application
Log = None
# The asynchronous event handler that will be used by all parts of
# the application
_AsyncSingleton = None

# Ugly trick to work around the fact that argparse does not let you
# create Action subclasses instances directly and thereby allow instance
# initialisation. This is the holder for the singleton instance
# of AgiConfig
_ConfigSingleton = None


def Config():
    return _ConfigSingleton

def AsyncHandler():
    return _AsyncSingleton
# Configuration file name
_CFG_FILE = '.agiconfig'
_CFG_SYS_FILE = 'agiconfig'

# Configuration file keywords
_REPOSITORY = 'Repository'
_LIBRARIES = 'Libraries'
_COLLABORATION = 'Collaboration'
_LOG = 'LogConfiguration'
_DEVELOPMENT = 'Development'
_TEST_SERVER = 'TestingServer'
_TESTING = 'Testing'
_FULLSCREEN = 'fullscreen'
_AWAY = 'Away'
_STARTDIR = 'Startdir'
_REPO_URL = 'RepoUrl'
_SERVER_URL = 'ServerUrl'
_RESPONSE_URL = 'ResponseUrl'
_GIT_SUBSCRIPTION = 'GitSubscription'
_TYPE = 'Type'
_LOCAL_REPO = 'LocalRepo'
_PYMT = 'PyMT'
_SERVER_PORT = 'ServerPort'
_LOCAL_PORT = 'LocalPort'
_SERVER_URL = 'ServerUrl'
_RESPONSE_URL = 'ResponseUrl'
_LOGPATH = 'ConfigurationPath'
_CONSOLELOG = 'ConsoleLog'
_LOGLEVEL = 'LogLevel'
_CRITICAL = 'critical'
_ERROR = 'error'
_WARNING = 'warning'
_INFO = 'info'
_DEBUG = 'debug'
_STORYCARD = 'Storycard'
_GIT = 'git'
_HG = 'hg'
_USERID = 'UserId'
logLevelMap = {_CRITICAL: logging.CRITICAL,
               _ERROR: logging.ERROR,
               _WARNING: logging.WARNING,
               _INFO: logging.INFO,
               _DEBUG: logging.DEBUG}
 
            
            
class RepopathChecker(petaapan.utilities.argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        result, errmsg = ValidateExistingDirectory(value)
        Config()._datastoreChecked = True
        if result != logging.NOTSET:
            Log.log(result,
                       '%s option error: %s' % (option_string, errmsg))
            Config()._no_data_store = True
        else:
            setattr(namespace, self.dest, value)
            Config()._no_data_store = False
            
class LogcfgChecker(petaapan.utilities.argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        result, errmsg = ValidateExistingFile(value)
        Config()._logcfgChecked = True
        if result != logging.NOTSET:
            Log.log(result,
                       '%s option error: %s' % (option_string, errmsg))
        else:
            setattr(namespace, self.dest, value)
            Config()._logging_enabled = True
            
            
class PymtChecker(petaapan.utilities.argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        result, errmsg = ValidateExistingDirectory(value)
        Config()._pymtChecked = True
        if result != logging.NOTSET:
            Log.log(result,
                       '%s option error: %s' % (option_string, errmsg))
            Config()._pymt_unavailable = True
        else:
            setattr(namespace, self.dest, value)
            Config()._pymt_unavailable = False
            
class LogLevelChecker(petaapan.utilities.argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        global logLevelMap        

        setattr(namespace, self.dest, logLevelMap[value])
        Config().log.level = logLevelMap[value]
        Log.info('Log level explicitly set to %s' % value)
        
class DisableLogChecker(petaapan.utilities.argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        Config().log.disable()
        setattr(namespace, self.dest, True)
    
               
class AgiConfig(object):

    def __init__(self, log):
        global _ConfigSingleton #IGNORE:W0603
        global Log #IGNORE:W0603
        global _AsyncSingleton #IGNORE:W0603
        self.__version__ = '0.3.0'
        self._log = log
        Log = log.logger
       

        if not _ConfigSingleton: _ConfigSingleton = self
        self._args = None
        self._collaboration_supported = False
        self._repo_supported = False
        self._shared_repo_not_available = True
        self._local_repo_not_available = True
        self._collaboration_not_available = True
        self._loggingEnabled = False
        self._no_data_store = True
        self._pymt_unavailable = True
        self._datastoreChecked = False
        self._repoUrlChecked = False
        self._collaborationServerUrl = None
        self._collaborationResponseUrl = None
        self._gitSubscription = None
        self._logcfgChecked = False
        self._pymtChecked = False
        self._no_git = False
        self._local_port = None
        self._collaboration_port = None
        self._collaboration_user = None
        self._testing_server = False
        self._datastore_path = None
        self._logging_enabled = False
        
        # Load the configuration
        self._base_directory, base_app = split(realpath(sys.argv[0]))
        defaults = {_TYPE:_GIT, _SERVER_PORT:'8080', _LOCAL_PORT:'16160',
                    _RESPONSE_URL:'localhost', _CONSOLELOG:'True',
                    _LOGLEVEL:_ERROR, _TEST_SERVER: 'False', _FULLSCREEN:'False'}
        config = ConfigParser.SafeConfigParser(defaults)
        # Get everything possible from the configuration files if present
        config.read([join(self._base_directory, _CFG_FILE),
                     join(expanduser('~'), _CFG_FILE),
                     expandvars(join('%ALLUSERSPROFILE%(%PROGRAMDATA%)',
                                     _CFG_FILE)
                                if sys.platform == 'win32'
                                else join('/etc', _CFG_SYS_FILE))])
        
        # Load the command line arguments
        parser = petaapan.utilities.argparse.ArgumentParser(prog='[python] '\
                                                            + base_app,
                                                            description=\
                    '''CMAP version %s:
                    A flexible multi-touch based agile process manager
                    that supports all agile disciplines''' % self.__version__)
        parser.set_defaults(repotype=config.get(_REPOSITORY, _TYPE)\
                                    if config.has_option(_REPOSITORY, _TYPE)\
                                    else None,
                            repourl=config.get(_REPOSITORY, _REPO_URL)\
                                        if config.has_option(_REPOSITORY,
                                                             _REPO_URL)\
                                        else None,
                            repopath=config.get(_REPOSITORY, _LOCAL_REPO)\
                                if config.has_option(_REPOSITORY, _LOCAL_REPO)\
                                else None,
                            pymtpath=config.get(_LIBRARIES, _PYMT)\
                                        if config.has_option(_LIBRARIES, _PYMT)\
                                        else None,
                            collaburl=config.get(_COLLABORATION, _SERVER_URL)\
                                    if config.has_option(_COLLABORATION,
                                                         _SERVER_URL)\
                                    else None,
                            responseurl=config.get(_COLLABORATION,
                                                   _RESPONSE_URL)\
                                    if config.has_option(_COLLABORATION,
                                                         _RESPONSE_URL)\
                                    else None,
                            serverport=config.get(_COLLABORATION,_SERVER_PORT)\
                             if config.has_option(_COLLABORATION,_SERVER_PORT)\
                             else None,
                            localport=config.get(_COLLABORATION, _LOCAL_PORT)\
                             if config.has_option(_COLLABORATION, _LOCAL_PORT)\
                             else None,
                            gitsub=config.get(_COLLABORATION, _GIT_SUBSCRIPTION)\
                             if config.has_option(_COLLABORATION, _GIT_SUBSCRIPTION)\
                             else None,
                            userid=config.get(_COLLABORATION, _USERID)\
                             if config.has_option(_COLLABORATION, _USERID)\
                             else None,
                            logconfig=config.get(_LOG, _LOGPATH)\
                                        if config.has_option(_LOG, _LOGPATH)\
                                        else None,
                            noconsolelog=config.get(_LOG, _CONSOLELOG)\
                                        if config.has_option(_LOG, _CONSOLELOG)\
                                        else None,
                            loglevel=config.get(_LOG, _LOGLEVEL)\
                                     if config.has_option(_LOG,_LOGLEVEL)\
                                     else logLevelMap[_ERROR],
                            storycard=config.get(_TESTING, _STORYCARD)\
                                    if config.has_option(_TESTING, _STORYCARD) \
                                    else None,
                            startdir=config.get(_AWAY, _STARTDIR)\
                                      if config.has_option(_AWAY,_STARTDIR)\
                                      else None,
                            fullscreen=config.get(_TESTING, _FULLSCREEN)\
                                    if config.has_option(_TESTING,_FULLSCREEN)\
                                    else None,
                            testserver=config.get(_TESTING, _TEST_SERVER)\
                                    if config.has_option(_TESTING,
                                                         _TEST_SERVER)\
                                    else None
                           )
        parser.add_argument('-t', '--type', dest='repotype',
                            choices=(_GIT, _HG), help=\
                      'repository type that implements versioned data storage')
        parser.add_argument('-r', '--repourl',
                            action='store', help=\
'url to the shared repository that implements the shared versioned data store')
        parser.add_argument('-p', '--repopath',
                            action=RepopathChecker, help=\
       'path to the local repository that implements the versioned data store')
        parser.add_argument('--collaburl',
                            action='store', help=\
          'Url to the server that provides collaboration services to the team')
        parser.add_argument('--responseurl',
                            action='store', help=\
'Url to the workstation that receives responses from the collaboration server')
        parser.add_argument('-s', '--serverport', type=int,
                            help='collaboration server access port')
        parser.add_argument('-l', '--localport', type=int, help=\
                        'access port on your computer that allows asynchronous'
                                       ' access from the collaboration server')
        parser.add_argument('-u', '--userid', help=\
                            'Your user id on the collaboration server')
        parser.add_argument('--gitsub', help=\
               'name of git notification subscription on collaboration server')
        parser.add_argument('--pymt', dest='pymtpath',
                            action=PymtChecker, help=\
                                            'path to your installation of PyMT'
                             ' if you want to force use of a specific version')
        parser.add_argument('--logconfig', action=LogcfgChecker, help=\
                          'path to standard Python logging configuration file')
        parser.add_argument('--noconsolelog', action=DisableLogChecker, help=\
                            'disable console logging')
        parser.add_argument('--loglevel', action=LogLevelChecker,
                            choices=(_CRITICAL, _ERROR, _WARNING,
                                     _INFO, _DEBUG),
                            help = 'Specify console logging level')
        parser.add_argument('-v', '--version', action='version',
                             version='%(prog)s: ' + self.__version__)
        parser.add_argument('--storycard', dest='storycard',
                            help=petaapan.utilities.argparse.SUPPRESS)
        parser.add_argument('--no_git', action='store_true',
                            help=petaapan.utilities.argparse.SUPPRESS)
        parser.add_argument('--startdir', dest='startdir',
                            help='Specify fully qualified starting directory') 
        parser.add_argument('--fullscreen', dest='fullscreen',
                  help='True (none zero) if we are running in fullscreen mode')
        parser.add_argument('--testserver', action='store_true',
                            help=petaapan.utilities.argparse.SUPPRESS) 
        # We need to parse the arguments we are interested in and pass the rest
        # to PyMt         
        self._args, balance = parser.parse_known_args()
        # Fixes the argument list for PyMT
        sys.argv = [sys.argv[0]]
        sys.argv.extend(balance)

        # Setup logging if a logging configuration file has been specified
        if (not self._logcfgChecked and config.has_option(_LOG, _LOGPATH)):
            self._logcfgChecked = True
            result, errmsg =\
                            ValidateExistingFile(config.get(_LOG, _LOGPATH))
            if result != logging.NOTSET:
                Log.log(result,
                     'Requested log configuration file not found: %s' % errmsg)
            else:
                self._loggingEnabled = True
        if (self._loggingEnabled):
            logging.config.fileConfig(self._args.logconfig)
                    
        # Check the type
        if self._args:
            if self._args.repotype != _GIT:
                Log.error('Git is the only repository type currently supported')
                self._repo_supported = False
            else:
                self._repo_supported = True
        
        # Finish validating the datastore if necessary
        if self._no_data_store and not self._datastoreChecked:
            if config.has_option(_REPOSITORY, _LOCAL_REPO):
                path = config.get(_REPOSITORY, _LOCAL_REPO)
                result, errmsg = ValidateExistingDirectory(path)
                if result != logging.NOTSET:
                    Log.log(result, errmsg)
                    self._datastoreChecked = True
                else:
                    self._no_data_store = False
                    drive, tail = splitdrive(path)
                    if drive:
                        path = capitalize(drive) + tail
                    self._datastore_path = path
            else:
                Log.error('Datastore not configured')
                
        if  not self._args or self._args.no_git:
            self._shared_repo_not_available = True
            self._repoUrlChecked = True
            self._repo_supported = False
            self._local_repo_not_available = True
            self._no_git = True
        else:                   
            # Finish validating the remote repository if necessary
            if self._shared_repo_not_available and not self._repoUrlChecked:
                if config.has_option(_REPOSITORY, _REPO_URL):
                    self._shared_repo_not_available = False
                    self._repoUrlChecked = True
                else:
                    self._repoUrlChecked = True
                 
        # Finish validating the collaboration location if necessary
        if self._args and self._args.collaburl:
            self._collaboration_not_available = False
            self._collaborationServerUrl = self._args.collaburl
            self._gitSubscription = self._args.gitsub
        else:
            self._collaboration_not_available = True
            Log.warning('Collaboration Service not configured')
                
        # Finish validating the collaboration response URL
        if not self._args or not self._args.responseurl:            
            Log.warning(\
'No collaboration response URL configured. Collaboration will be disabled')
            self._collaboration_not_available = True
        else:
            self._collaborationResponseUrl = self._args.responseurl

            
        # Make sure that the collaboration userid is present
        if not self._args or not self._args.userid:
            Log.warning(\
            'No collaboration userid supplied. Collaboration will be disabled')
            self._collaboration_not_available = True
        else:
            self._collaboration_user = self._args.userid

        # Finish validating the PyMt path
        if self._pymt_unavailable and not self._pymtChecked:
            if config.has_option(_LIBRARIES, _PYMT):
                result, errmsg =\
                      ValidateExistingDirectory(config.get(_LIBRARIES,_PYMT))
                if result != logging.NOTSET:
                    Log.log(result, errmsg)
                    self._pymtChecked = True
                else: # We have a PyMT directory - see if it for real
                    self._pymt_unavailable = False
                    # Put PyMT on PYTHONPATH
                    Log.debug('PyMT at %s' % config.get(_LIBRARIES,_PYMT))
                    sys.path.append(config.get(_LIBRARIES,_PYMT))
            else:
                Log.info('No PyMT path configured')
                
        # Final check
        logger = None
        if not self._pymt_unavailable or (self._pymt_unavailable
                                          and not self._pymtChecked):
            try:
                if self._args.pymtpath:
                    sys.path.append(self._args.pymtpath)

                from pymt import logger
                self._pymt_unavailable = False
            except ImportError:
                self._pymt_unavailable = True
                Log.exception('PyMT problem: PYTHONPATH %s' % unicode(sys.path))
        # Set default PyMT logging to the same as us
        if not self._pymt_unavailable:
            logger.pymt_logger.setLevel(self._args.loglevel)
        
        if not self._no_git:
            # Make sure Git is installed
            env = petaapan.utilities.envpath.EnvironmentPath()
            gp = (self._args.repotype if self._args.repotype else 'git')\
                 + '.exe' if sys.platform == 'win32' else ''
            self._repo_supported = True if env.findPath(gp, X_OK) else False
            
            # See if we have a local repository
            if not self._no_data_store:
                self._local_repo_not_available = False if exists(\
                                    join(self._args.repopath, '.git')) else True
                if not self._local_repo_not_available:
                    self._no_data_store = False
                    self._datastore_path = self._args.repopath
        
        # Make the other configuration data available externally
        self._local_port = self._args.localport if self._args else None
        self._collaboration_port = self._args.serverport if self._args else None
        self._testing_server = self._args.testserver if self._args else None                
        # Setup the asynchronous handling for CMAP
        import async
        if _AsyncSingleton is None:
            _AsyncSingleton = async.Async()                  
    
    @property    
    def args(self):
        return self._args
    
    @property
    def repoSupported(self):
        return self._repo_supported
    
    @property
    def sharedRepoNotAvailable(self):
        return self._shared_repo_not_available\
               or not self._repo_supported
    
    @property
    def localRepoNotAvailable(self):
        return self._local_repo_not_available\
               or not self._repo_supported
    
    @property
    def collaborationSupported(self):
        return self._collaboration_supported
    
    @property
    def collaborationNotAvailable(self):
        return self._collaboration_not_available
    
    @property
    def pymtUnavailable(self):
        return self._pymt_unavailable
    
    @property
    def noDatastore(self):
        return self._no_data_store
    
    @property
    def version(self):
        return self.__version__
    
    @property
    def log(self):
        return self._log
    
    @property
    def using_git(self):
        return self._no_git
    
    @property
    def local_port(self):
        return self._local_port
    
    @property
    def collaboration_port(self):
        return self._collaboration_port
    
    @property
    def collaborationServerUrl(self):
        return self._collaborationServerUrl
    
    @property
    def collaborationResponseUrl(self):
        return self._collaborationResponseUrl
    
    @property
    def collaborationUser(self):
        return self._collaboration_user
    
    @property
    def testingServer(self):
        return self._testing_server
    
    @property
    def datastore(self):
        return self._datastore_path
    
    @property
    def gitSubscription(self):
        return self._gitSubscription
    
    @property
    def baseDirectory(self):
        return self._base_directory
    
    @property
    def xmlTemplates(self):
        return join(self.baseDirectory,'Data')
    
    @property
    def gestures(self):
        return join(self.baseDirectory, 'cmap', 'gestures')
        
    
        