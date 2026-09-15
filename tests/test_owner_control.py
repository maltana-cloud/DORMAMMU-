from devintel.control import ControlDecision, OwnerApprovalAuthority, OwnerControlCenter
from devintel.runtime import DEVINTELRuntime


SECRET = b"dormammu-owner-approval-test-secret-32-bytes!"


def test_control_snapshot_is_observation_only():
    center = OwnerControlCenter(DEVINTELRuntime())
    snap = center.snapshot("channel:test")
    assert snap.scope_id == "channel:test"
    assert snap.plugin_count == 1
    assert snap.pending_approvals == 0


def test_pending_approvals_are_scoped():
    center = OwnerControlCenter(DEVINTELRuntime())
    center.request("scope:a", "publish")
    center.request("scope:b", "publish")
    assert center.snapshot("scope:a").pending_approvals == 1
    assert center.snapshot("scope:b").pending_approvals == 1


def test_sensitive_command_requires_authenticated_owner_approval():
    authority = OwnerApprovalAuthority(SECRET)
    center = OwnerControlCenter(DEVINTELRuntime(), approval_authority=authority)
    command = center.request("channel:test", "sensitive", reason="owner action")
    assert center.decide(command) is ControlDecision.DENY
    assert center.decide(command, owner_approved=True) is ControlDecision.DENY
    approval = authority.approve(command)
    assert center.consume(command, approval=approval) is ControlDecision.ALLOW
    assert center.decide(command, approval=approval) is ControlDecision.DENY


def test_authenticated_approval_is_required_even_when_legacy_flag_is_true():
    center = OwnerControlCenter(DEVINTELRuntime())
    command = center.request("channel:test", "sensitive")
    assert center.consume(command, owner_approved=True) is ControlDecision.DENY


def test_unknown_command_fails_closed():
    authority = OwnerApprovalAuthority(SECRET)
    center = OwnerControlCenter(DEVINTELRuntime(), approval_authority=authority)
    command = center.request("scope:a", "x")
    foreign = type(command)("foreign", command.scope_id, command.action)
    approval = authority.approve(command)
    assert center.decide(foreign, approval=approval) is ControlDecision.DENY
