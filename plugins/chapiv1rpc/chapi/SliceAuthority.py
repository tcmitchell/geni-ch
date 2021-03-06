#----------------------------------------------------------------------
# Copyright (c) 2011-2016 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

import logging
import tools.pluginmanager as pm
from DelegateBase import DelegateBase
from HandlerBase import HandlerBase
from Exceptions import *
from tools.cert_utils import *
from tools.chapi_log import *
from MethodContext import *

sa_logger = logging.getLogger('sav1')

# Handler for SA APi. This version only handles the Slice service
class SAv1Handler(HandlerBase):
    def __init__(self):
        super(SAv1Handler, self).__init__(sa_logger)

    ## SLICE SERVICE methods

    # This call is unprotected: no checking of credentials
    # Return version information about this SA including what
    # services are provided and underlying object model
    def get_version(self, options={}):
        with MethodContext(self, SA_LOG_PREFIX, 'get_version',
                           {}, [], options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_version(options, mc._session)
        return mc._result

    # Generic V2 service methods
    def create(self, type, credentials, options):
        if type == "SLICE":
            result = \
                self.create_slice(credentials, options)
        elif type == "SLIVER_INFO":
            result = \
                self.create_sliver_info(credentials, options)
        elif type == "PROJECT":
            result = \
                self.create_project(credentials, options)
        else:
             result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    def update(self, type, urn, credentials, options):
        if type == "SLICE":
            result = self.update_slice(urn, credentials, options)
        elif type == "SLIVER_INFO":
            result = self.update_sliver_info(urn, credentials, options)
        elif type == "PROJECT":
            result = self.update_project(urn, credentials, options)
        else:
            return self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    def delete(self, type, urn, credentials, options):
        if type == "SLICE":
          msg = "method delete not implemented for type %s" % (type)
          return self._errorReturn(CHAPIv1NotImplementedError(msg))
        elif type == "SLIVER_INFO":
            result = self.delete_sliver_info(urn, credentials, options)
        elif type == "PROJECT":
          msg = "method delete not implemented for type %s" % (type)
          return self._errorReturn(CHAPIv1NotImplementedError(msg))
        else:
             result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    def lookup(self, type, credentials, options):
        if type == "SLICE":
            result = self.lookup_slices(credentials, options)
        elif type == "SLIVER_INFO":
            result = self.lookup_sliver_info(credentials, options)
        elif type == "PROJECT":
            result = self.lookup_projects(credentials, options)
        else:
            result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    # Generic v2 membership methods
    def modify_membership(self, type, urn, credentials, options):
        if type == "SLICE":
            result = self.modify_slice_membership(urn, credentials, options)
        elif type == "PROJECT":
            result = self.modify_project_membership(urn, credentials, options)
        else:
            result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    def lookup_members(self, type, urn, credentials, options):
        if type == "SLICE":
            result = self.lookup_slice_members(urn, credentials, options)
        elif type == "PROJECT":
            result = self.lookup_project_members(urn, credentials, options)
        else:
            result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result

    def lookup_for_member(self, type, urn, credentials, options):
        if type == "SLICE":
            result = self.lookup_slices_for_member(urn, credentials, options)
        elif type == "PROJECT":
            result = self.lookup_projects_for_member(urn, credentials, options)
        else:
            result = self._errorReturn(CHAPIv1ArgumentError("Invalid type: %s" % type))
        return result


    # This call is protected
    # Create a slice given provided options and authorized by client_cert
    # and given credentials
    def create_slice(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'create_slice',
                           {}, credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.create_slice(mc._client_cert,
                                                credentials,
                                                options,
                                                mc._session)
        return mc._result

    # This call is protected
    # Lookup slices with filters and match criterial given in options
    # Authorized by client cert and credentials
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_slices(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_slices',
                           {}, credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_slices(mc._client_cert,
                                                 credentials,
                                                 options,
                                                 mc._session)
        return mc._result

    # This call is protected
    # Update slice with fields specified in given options for given slice
    # Authorized by client cert and credentials
    def update_slice(self, slice_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'update_slice',
                           {'slice_urn' : slice_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.update_slice(mc._client_cert,
                                                slice_urn,
                                                credentials,
                                                options,
                                                mc._session)
        return mc._result

    # This call is protected
    # Get credentials for given user with respect to given slice or project
    # Authorization based on client cert and given credentials
    # Note the session is _not_ read_only because it may update_expirations
    def get_credentials(self, urn, credentials, options):
        urn_parts = parse_urn(urn)
        if urn_parts is None:
            msg = "Invalid URN: %s" % urn
            return self._errorReturn(CHAPIv1ArgumentError(msg))
        (authority, typ, name) = urn_parts
        if typ == "slice":
            result = self.get_slice_credentials(urn, credentials, options)
        elif typ == "project":
            result = self.get_project_credentials(urn, credentials, options)
        else:
            msg = "Not a slice or project"
            result = self._errorReturn(CHAPIv1ArgumentError(msg))
        return result

    def get_slice_credentials(self, slice_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_slice_credentials',
                           {'slice_urn' : slice_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_slice_credentials(mc._client_cert,
                                                   slice_urn,
                                                   credentials,
                                                   options,
                                                   mc._session)
        return mc._result

    def get_project_credentials(self, project_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_project_credentials',
                           {'project_urn': project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_project_credentials(mc._client_cert,
                                                           project_urn,
                                                           credentials,
                                                           options,
                                                           mc._session)
        return mc._result

    ## SLICE MEMBER SERVICE methods

    # Modify slice membership, adding, removing and changing roles
    # of members with respect to given slice
    # The list of members_to_add, members_to_remove, members_to_modify
    # are fields in the options directionary
    # 'members_to_add' : List of {URN : ROLE} dictionaries
    # 'members_to_remove' : List of URNs
    # 'members_to_modify' : List of {URN : ROLE} dictionaries
    def modify_slice_membership(self, slice_urn,
                                    credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'modify_slice_membership',
                           {'slice_urn' : slice_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.modify_slice_membership(mc._client_cert,
                                                           slice_urn,
                                                           credentials,
                                                           options,
                                                           mc._session)
        return mc._result

    # Lookup members of given slice and their roles within that slice
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_slice_members(self, slice_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_slice_members',
                           {'slice_urn' : slice_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_slice_members(mc._client_cert,
                                                           slice_urn,
                                                           credentials,
                                                           options,
                                                           mc._session)
        return mc._result

    # Lookup slices to which member belongs and their roles
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_slices_for_member(self, member_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_slices_for_member',
                           {'member_urn' : member_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_slices_for_member(mc._client_cert,
                                                           member_urn,
                                                           credentials,
                                                           options,
                                                           mc._session)
        return mc._result

    ## SLIVER INFO SERVICE methods

    # Create a record of sliver creation
    # Provide a dictionary of required fields and return a
    # dictionary of completed fields for new records
    def create_sliver_info(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'create_sliver_info',
                           {},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.create_sliver_info(mc._client_cert,
                                                      credentials,
                                                      options,
                                                      mc._session)
        return mc._result

    # Delete a sliver_info record of given sliver_urn
    def delete_sliver_info(self, sliver_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'delete_sliver_info',
                           {'sliver_urn' : sliver_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.delete_sliver_info(mc._client_cert,
                                                      sliver_urn,
                                                      credentials,
                                                      options,
                                                      mc._session)
        return mc._result

    # Update the details of a sliver_info record of given sliver_urn
    def update_sliver_info(self, sliver_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'update_sliver_info',
                           {'sliver_urn' : sliver_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.update_sliver_info(mc._client_cert,
                                                      sliver_urn,
                                                      credentials,
                                                      options,
                                                      mc._session)
        return mc._result

    # Lookup sliver info for given match criteria
    # return fields in given fillter driteria
    def lookup_sliver_info(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_sliver_info',
                           {},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_sliver_info(mc._client_cert,
                                                      credentials,
                                                      options,
                                                      mc._session)
        return mc._result

    ## PROJECT SERVICE methods

    # Create project with given details in options
    def create_project(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'create_project',
                           {},
                           credentials, options,
                           read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.create_project(mc._client_cert,
                                                  credentials,
                                                  options,
                                                  mc._session)
        return mc._result

    # Lookup project detail for porject matching 'match' option
    # returning fields in 'filter' option
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_projects(self, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_projects',
                           {},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_projects(mc._client_cert,
                                                   credentials,
                                                   options,
                                                   mc._session)
        return mc._result

    # Update fields in given project object specified in options
    def update_project(self, project_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'update_project',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.update_project(mc._client_cert,
                                                  project_urn,
                                                  credentials,
                                                  options,
                                                  mc._session)
        return mc._result


    ## PROJECT MEMBER SERVICE methods

    # Modify project membership, adding, removing and changing roles
    # of members with respect to given project
    # The list of members_to_add, members_to_remove, members_to_modify
    # are fields in the options directionary
    # 'members_to_add' : List of {URN : ROLE} dictionaries
    # 'members_to_remove' : List of URNs
    # 'members_to_modify' : List of {URN : ROLE} dictionaries
    def modify_project_membership(self, project_urn,
                                      credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'modify_project_membership',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.modify_project_membership(mc._client_cert,
                                                             project_urn,
                                                             credentials,
                                                             options,
                                                             mc._session)
        return mc._result

    # Lookup members of given project and their roles within that project
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_project_members(self, project_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_project_members',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_project_members(mc._client_cert,
                                                          project_urn,
                                                          credentials,
                                                          options,
                                                          mc._session)
        return mc._result


    # Lookup projects to which member belongs and their roles
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_projects_for_member(self, member_urn, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_projects_for_member',
                           {'member_urn' : member_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_projects_for_member(mc._client_cert,
                                                          member_urn,
                                                          credentials,
                                                          options,
                                                          mc._session)
        return mc._result

    ## PROJECT ATTRIBUTE SERVICE methods

    # Lookup, add, or remove project attributes
    # of members with respect to given project
    # The name and value of the attribute to add
    #    are fields in the options directionary
    # 'attribute_to_add' : NAME,VALUE
    # 'attribute_to_remove' : NAME
    # Note the session is _not_ read_only because it may update_expirations
    def lookup_project_attributes(self, project_urn,
                                 credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'lookup_project_attributes',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.lookup_project_attributes(mc._client_cert,
                                                             project_urn,
                                                             credentials,
                                                             options,
                                                             mc._session)
        return mc._result

    # Add an attribute to a given project
    # arguments: project_urn
    #     options {'attr_name' : attr_name, 'attr_value' : attr_value}
    def add_project_attribute(self, \
                                  project_urn, \
                                  credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'add_project_attribute',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.add_project_attribute(mc._client_cert,
                                                             project_urn,
                                                             credentials,
                                                             options,
                                                             mc._session)
        return mc._result

    # remove an attribute from a given project
    # arguments: project_urn
    #     options {'attr_name' : attr_name}
    def remove_project_attribute(self, \
                                     project_urn, \
                                     credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'remove_project_attribute',
                           {'project_urn' : project_urn},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.remove_project_attribute(mc._client_cert,
                                                            project_urn,
                                                            credentials,
                                                            options,
                                                            mc._session)
        return mc._result


    # Methods for handling pending project / slice requests and invitations
    # Note: Not part of standard Federation API

    def create_request(self, context_type, context_id, request_type, request_text,
                       request_details, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'create_request',
                           {'context_type' : context_type,
                            'context_id' : context_id,
                            'request_type' : request_type,
                            'request_text' : request_text,
                            'request_details' : request_details},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.create_request(mc._client_cert,
                                                  context_type,
                                                  context_id,
                                                  request_type,
                                                  request_text,
                                                  request_details,
                                                  credentials,
                                                  options,
                                                  mc._session)
        return mc._result

    def resolve_pending_request(self, context_type, request_id, \
                                    resolution_status, resolution_description,  \
                                    credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'resolve_pending_request',
                           {'context_type' : context_type,
                            'request_id' : request_id,
                            'resolution_status' : resolution_status,
                            'resolution_description' : resolution_description},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.resolve_pending_request(mc._client_cert,
                                                           context_type,
                                                           request_id,
                                                           resolution_status,
                                                           resolution_description,
                                                           credentials,
                                                           options,
                                                           mc._session)
        return mc._result

    def get_requests_for_context(self, context_type, context_id, status, \
                                     credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_requests_for_context',
                           {'context_type' : context_type,
                            'context_id' : context_id,
                            'status' : status},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_requests_for_context(mc._client_cert,
                                                            context_type,
                                                            context_id,
                                                            status,
                                                            credentials,
                                                            options,
                                                            mc._session)
        return mc._result


    def get_requests_by_user(self, member_id, context_type,
                             context_id, status,
                             credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_requests_by_user',
                           {'member_id' : member_id,
                            'context_type' : context_type,
                            'context_id' : context_id,
                            'status' : status},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_requests_by_user(mc._client_cert,
                                                        member_id,
                                                        context_type,
                                                        context_id,
                                                        status,
                                                        credentials,
                                                        options,
                                                        mc._session)
        return mc._result

    def get_pending_requests_for_user(self, member_id, context_type, context_id, \
                                     credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_pending_requests_for_user',
                           {'member_id' : member_id,
                            'context_type' : context_type,
                            'context_id' : context_id},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_pending_requests_for_user(mc._client_cert,
                                                                 member_id,
                                                                 context_type,
                                                                 context_id,
                                                                 credentials,
                                                                 options,
                                                                 mc._session)
        return mc._result

    def get_number_of_pending_requests_for_user(self, member_id, \
                                                    context_type, context_id, \
                                                    credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_number_of_pending_requests_for_user',
                           {'member_id' : member_id,
                            'context_type' : context_type,
                            'context_id' : context_id},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_number_of_pending_requests_for_user(mc._client_cert,
                                                                           member_id,
                                                                           context_type,
                                                                           context_id,
                                                                           credentials,
                                                                           options,
                                                                           mc._session)
        return mc._result

    def get_request_by_id(self, request_id, context_type, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'get_requests_by_id',
                           {'request_id' : request_id,
                            'context_type' : context_type},
                           credentials, options, read_only=True) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.get_request_by_id(mc._client_cert,
                                                     request_id,
                                                     context_type,
                                                     credentials,
                                                     options,
                                                     mc._session)
        return mc._result

    def invite_member(self, role, project_id, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'invite_member',
                           {'project_id' : project_id},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.invite_member(mc._client_cert,
                                                 role,
                                                 project_id,
                                                 credentials,
                                                 options,
                                                 mc._session)
        return mc._result

    def accept_invitation(self, invite_id, member_id, credentials, options):
        with MethodContext(self, SA_LOG_PREFIX, 'accept_invitation',
                           {'invite_id' : invite_id, 'member_id' : member_id},
                           credentials, options, read_only=False) as mc:
            if not mc._error:
                mc._result = \
                    self._delegate.accept_invitation(mc._client_cert,
                                                     invite_id,
                                                     member_id,
                                                     credentials,
                                                     options,
                                                     mc._session)
        return mc._result


# Base class for implementing the SA Slice interface. Must be
# implemented in a derived class, and that derived class
# must call setDelegate on the handler
class SAv1DelegateBase(DelegateBase):

    ## SLICE SERVICE methods

    def __init__(self):
        super(SAv1DelegateBase, self).__init__(sa_logger)

    def get_version(self, options, session):
        raise CHAPIv1NotImplementedError('')

    # This call is protected
    def create_slice(self, client_cert, credentials, options,
                     session):
        raise CHAPIv1NotImplementedError('')

    # This call is protected
    def lookup_slices(self, client_cert, credentials, options,
                      session):
        raise CHAPIv1NotImplementedError('')

    # This call is protected
    def update_slice(self, client_cert, slice_urn, credentials, options,
                     session):
        raise CHAPIv1NotImplementedError('')

    # This call is protected
    def get_credentials(self, client_cert, slice_urn, credentials, options,
                        session):
        raise CHAPIv1NotImplementedError('')

    ## SLICE MEMBER SERVICE methods

    def modify_slice_membership(self,  \
                                    client_cert, slice_urn,
                                    credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def lookup_slice_members(self, \
                                 client_cert, slice_urn, credentials, options,
                             session):
        raise CHAPIv1NotImplementedError('')

    def lookup_slices_for_member(self, \
                                     client_cert, member_urn, \
                                     credentials, options, session):
        raise CHAPIv1NotImplementedError('')


    ## SLIVER INFO SERVICE methods

    def create_sliver_info(self, client_cert, credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def delete_sliver_info(self, client_cert, sliver_urn, \
                               credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def update_sliver_info(self, client_cert, sliver_urn, \
                               credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def lookup_sliver_info(self, client_cert, credentials, options, session):
        raise CHAPIv1NotImplementedError('')


    ## PROJECT SERVICE methods

    def create_project(self, client_cert, credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def lookup_projects(self, client_cert, credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def update_project(self, client_cert, project_urn, credentials,
                       options, session):
        raise CHAPIv1NotImplementedError('')

    ## PROJECT MEMBER SERVICE methods

    def modify_project_membership(self,  \
                                    client_cert, project_urn,
                                    credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def lookup_project_members(self, \
                                 client_cert, project_urn, \
                                   credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def lookup_projects_for_member(self, \
                                     client_cert, member_urn, \
                                     credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    ## PROJECT ATTRIBUTE SERVICE methods

    def lookup_project_attributes(self,  \
                                      client_cert, project_urn,  \
                                      credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    # Add an attribute to a given project
    # arguments: project_urn
    #     options {'attr_name' : attr_name, 'attr_value' : attr_value}
    def add_project_attribute(self, \
                                  client_cert, project_urn, \
                                  credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    # remove an attribute from a given project
    # arguments: project_urn
    #     options {'attr_name' : attr_name}
    def remove_project_attribute(self, \
                                     client_cert, project_urn, \
                                     credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    # Request handling methods

    def create_request(self, client_cert, context_type, \
                           context_id, request_type, request_text, \
                           request_details, credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def resolve_pending_request(self, client_cert, context_type, request_id, \
                                    resolution_status, resolution_description,  \
                                    credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def get_requests_for_context(self, client_cert, context_type, \
                                 context_id, status, \
                                 credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def get_requests_by_user(self, client_cert, member_id, context_type, \
                                 context_id, status, \
                                 credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def get_pending_requests_for_user(self, client_cert, member_id, \
                                          context_type, context_id, \
                                          credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def get_number_of_pending_requests_for_user(self, client_cert, member_id, \
                                                    context_type, context_id, \
                                                    credentials, options,
                                                session):
        raise CHAPIv1NotImplementedError('')

    def get_request_by_id(self, client_cert, request_id, context_type, \
                              credentials, options, session):
        raise CHAPIv1NotImplementedError('')



    def invite_member(self, client_cert, role, project_id,
                      credentials, options, session):
        raise CHAPIv1NotImplementedError('')

    def accept_invitation(self, client_cert, invite_id, member_id,
                          credentials, options, session):
        raise CHAPIv1NotImplementedError('')
