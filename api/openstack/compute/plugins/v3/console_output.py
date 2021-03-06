# Copyright 2011 OpenStack Foundation
# Copyright 2011 Grid Dynamics
# Copyright 2011 Eldar Nugaev, Kirill Shileev, Ilya Alekseyev
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import webob

from nova.api.openstack import common
from nova.api.openstack.compute.schemas.v3 import console_output
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova import compute
from nova import exception
from nova.i18n import _

ALIAS = "os-console-output"
authorize = extensions.extension_authorizer('compute', "v3:" + ALIAS)


class ConsoleOutputController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(ConsoleOutputController, self).__init__(*args, **kwargs)
        self.compute_api = compute.API()

    @extensions.expected_errors((400, 404, 409, 501))
    @wsgi.action('get_console_output')
    @validation.schema(console_output.get_console_output)
    def get_console_output(self, req, id, body):
        """Get text console output."""
        context = req.environ['nova.context']
        authorize(context)

        instance = common.get_instance(self.compute_api, context, id,
                                       want_objects=True)
        length = body['get_console_output'].get('length')
        if length is not None and int(length) == -1:
            # NOTE: -1 means an unlimited length. So here translates it to None
            # which also means an unlimited in the internal implementation.
            length = None

        try:
            output = self.compute_api.get_console_output(context,
                                                         instance,
                                                         length)
        except exception.InstanceNotReady as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        except NotImplementedError:
            msg = _("Unable to get console log, functionality not implemented")
            raise webob.exc.HTTPNotImplemented(explanation=msg)

        return {'output': output}


class ConsoleOutput(extensions.V3APIExtensionBase):
    """Console log output support, with tailing ability."""

    name = "ConsoleOutput"
    alias = ALIAS
    version = 1

    def get_controller_extensions(self):
        controller = ConsoleOutputController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]

    def get_resources(self):
        return []
