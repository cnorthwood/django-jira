import traceback
import hashlib
import sys

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
import suds.client

class JiraExceptionReporterMiddleware:
    
    def __init__(self):
        
        # If we're in debug mode, and JIRA_REPORT_IN_DEBUG is false (or not set)
        # then don't report errors
        if settings.DEBUG:
            try:
                if not settings.JIRA_REPORT_IN_DEBUG:
                    raise MiddlewareNotUsed
            except AttributeError:
                raise MiddlewareNotUsed
        
        # Silently fail if any settings are missing
        try:
            settings.JIRA_ISSUE_DEFAULTS
            
            # Set up SOAP
            self._soap = suds.client.Client(settings.JIRA_URL + 'rpc/soap/jirasoapservice-v2?wsdl')        
            
            # Authenticate
            self._auth = self._soap.service.login(settings.JIRA_USER, settings.JIRA_PASSWORD)
        
        except AttributeError:
            raise MiddlewareNotUsed
    
    def process_exception(self, request, exc):
        
        
        # See if this exception has already been reported inside JIRA, and is
        # currently an open issue
        
        # If it has, add a comment noting that we've had another report of it
        
        # Otherwise, create it
        issue = settings.JIRA_ISSUE_DEFAULTS.copy()
        print exc
        issue['summary'] = traceback.format_exception_only(type(exc), exc)[0]
        issue['description'] = '{noformat:title=Traceback}\n' + traceback.format_exc() + '\n{noformat}\n\n' + \
                               '{noformat:title=Request}\n' + repr(request) + '\n{noformat}'
        
        print self._soap.service.createIssue(self._auth, issue)
        