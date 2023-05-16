# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the
# License is located at
#
#	 http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""Integration tests for the ACM API Certificate resource
"""

import time

import pytest

from acktest.k8s import resource as k8s
from acktest.resources import random_suffix_name
from e2e import service_marker, CRD_GROUP, CRD_VERSION, load_resource
from e2e.replacement_values import REPLACEMENT_VALUES
from e2e import certificate

RESOURCE_PLURAL = 'certificates'

CREATE_WAIT_AFTER_SECONDS = 65

DELETE_WAIT_AFTER_SECONDS = 30

# Time we wait for the certificate to get to ACK.ResourceSynced=True
MAX_WAIT_FOR_SYNCED_MINUTES = 1

@pytest.fixture
def certificate_public_fake():
    certificate_name = random_suffix_name("certificate", 20)
    domain_name = "fakedomain.net"

    replacements = REPLACEMENT_VALUES.copy()
    replacements['CERTIFICATE_NAME'] = certificate_name
    replacements['DOMAIN_NAME'] = domain_name

    resource_data = load_resource(
        "certificate_public",
        additional_replacements=replacements,
    )

    # Create the k8s resource
    ref = k8s.CustomResourceReference(
        CRD_GROUP, CRD_VERSION, RESOURCE_PLURAL,
        certificate_name, namespace="default",
    )
    k8s.create_custom_resource(ref, resource_data)
    cr = k8s.wait_resource_consumed_by_controller(ref)

    assert cr is not None
    assert k8s.get_resource_exists(ref)

    time.sleep(CREATE_WAIT_AFTER_SECONDS)

    yield (ref, cr)

    # Try to delete, if doesn't already exist
    try:
        _, deleted = k8s.delete_custom_resource(ref, 3, 10)
        assert deleted
        certificate.wait_until_deleted(certificate_arn)
    except:
        pass    


@service_marker
@pytest.mark.canary
class TestCertificateValidationStatus:        
    #Test certificateDomainValidationOptions Status  
    def test_cert_domain_validation_status(
            self,
            certificate_public_fake,
    ):
        (ref, cr) = certificate_public_fake
        certificate_arn = cr["status"]["ackResourceMetadata"]["arn"] 
        # Wait for the resource to get synced
        assert k8s.wait_on_condition(
            ref,
            "ACK.ResourceSynced",
            "True",
            wait_periods=MAX_WAIT_FOR_SYNCED_MINUTES,
        )
               
        certificate.wait_until(
            certificate_arn,
            certificate.status_matches("PENDING_VALIDATION"),
        )
        
        time.sleep(MAX_WAIT_FOR_SYNCED_MINUTES)

        cr = k8s.get_resource(ref)
        assert "status" in cr
        assert 'status' in cr['status']
        assert cr['status']['status'] == 'PENDING_VALIDATION'
        assert "certificateDomainValidationOptions" in cr['status']
        assert cr['status']['certificateDomainValidationOptions'][0]['domainName'] == "fakedomain.net"
        if cr['status']['status'] in ['PENDING_VALIDATION','SUCCESS']:
            assert 'resourceRecord' in cr['status']['certificateDomainValidationOptions'][0]
                                       
        k8s.delete_custom_resource(ref)

        time.sleep(DELETE_WAIT_AFTER_SECONDS)

        certificate.wait_until_deleted(certificate_arn)    
