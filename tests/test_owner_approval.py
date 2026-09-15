import pytest

from devintel.control import (
    ApprovalAuthorizationError,
    OwnerApprovalAuthority,
    OwnerControlCenter,
)
from devintel.runtime import DEVINTELRuntime


SECRET = b"dormammu-owner-approval-test-secret-32-bytes!"


def test_owner_approval_is_scoped_and_single_use():
    authority = OwnerApprovalAuthority(SECRET)
    center = OwnerControlCenter(DEVINTELRuntime(), approval_authority=authority)
    command = center.request("scope:a", "sensitive")
    approval = authority.approve(command, issued_at=1000)

    assert center.consume(command, approval=approval).value == "allow"
    assert center.decide(command, approval=approval).value == "deny"


def test_owner_approval_rejects_wrong_scope():
    authority = OwnerApprovalAuthority(SECRET)
    center = OwnerControlCenter(DEVINTELRuntime(), approval_authority=authority)
    command = center.request("scope:a", "sensitive")
    other = center.request("scope:b", "sensitive")
    approval = authority.approve(command, issued_at=1000)

    assert center.decide(other, approval=approval).value == "deny"


def test_owner_approval_rejects_tampering_and_expiry():
    authority = OwnerApprovalAuthority(SECRET, max_age_seconds=10)
    center = OwnerControlCenter(DEVINTELRuntime(), approval_authority=authority)
    command = center.request("scope:a", "sensitive")
    approval = authority.approve(command, issued_at=1000)

    with pytest.raises(ApprovalAuthorizationError):
        authority.verify(command, type(approval)(
            approval.command_id, approval.scope_id, approval.nonce, approval.issued_at, "bad"
        ), now=1000)
    with pytest.raises(ApprovalAuthorizationError):
        authority.verify(command, approval, now=1011)


def test_short_secret_is_rejected():
    with pytest.raises(ValueError):
        OwnerApprovalAuthority(b"too-short")
