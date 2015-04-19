import os
import time
import sys
import novaclient.v1_1.client as nvclient
from credentials import get_nova_creds
creds = get_nova_creds()
nova = nvclient.Client(**creds)
name = argv[1]
image = nova.images.find(name=sys.argv[2])
flavor = nova.flavors.find(name=sys.argv[3])
instance = nova.servers.create(name=name, image=image, flavor=flavor)

# Poll at 5 second intervals, until the status is no longer 'BUILD'
status = instance.status
while status == 'BUILD':
    time.sleep(5)
    # Retrieve the instance again so the status field updates
    instance = nova.servers.get(instance.id)
    status = instance.status
#print "status: %s" % status
floating_ip = nova.floating_ips.create()
instance.add_floating_ip(floating_ip)
instance['access_ip_v4'] = floating_ip.ip
#self.public_vms[instance['name']] = inst
