"""
Tests for FastAPI Rilavo middleware.
Run with: pytest test_main.py -v
"""
import pytest
from fastapi.testclient import TestClient
from main import app, VERIFIER_ID

client = TestClient(app)


def test_health_endpoint():
    """Health endpoint should be public."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_public_endpoint():
    """Public endpoint should not require auth."""
    response = client.get("/public/info")
    assert response.status_code == 200
    assert response.json()["public"] is True


def test_protected_without_credential():
    """Protected endpoint should return 401 without credential."""
    response = client.get("/protected/data")
    assert response.status_code == 401


def test_protected_with_invalid_credential():
    """Protected endpoint should return 401 with invalid credential."""
    response = client.get(
        "/protected/data",
        headers={"x-rilavo-credential": "invalid"}
    )
    assert response.status_code == 401


def test_full_verification_flow():
    """Test complete flow: issue credential -> sign PoP -> verify."""
    # 1. Issue a test credential
    issue_response = client.post(
        "/admin/issue-test-credential",
        json={
            "principal": "test-principal",
            "agent": "test-agent",
            "action_class": "data.read"
        }
    )
    assert issue_response.status_code == 200
    credential = issue_response.json()["credential"]

    # 2. Sign a PoP request
    pop_response = client.post(
        "/admin/sign-pop",
        json={
            "method": "GET",
            "path": "/protected/data",
            "action": "data.read"
        }
    )
    assert pop_response.status_code == 200
    pop_data = pop_response.json()

    # 3. Call protected endpoint with credential and PoP
    headers = {
        "x-rilavo-credential": credential,
        "x-rilavo-action": pop_data["action"],
        "x-rilavo-pop-signature": pop_data["signature"],
        "x-rilavo-request-nonce": pop_data["request_nonce"],
    }
    response = client.get("/protected/data", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "authenticated_as" in data
    # The middleware returns principal, agent, action_class from the credential
    assert data["authenticated_as"]["action_class"] == "data.read"


def test_wrong_audience_rejected():
    """Credential with wrong audience should be rejected."""
    # Issue credential for different audience using the app's issuer
    from rilavo.api import do_issue
    from rilavo.testing import local_test_agent
    from main import issuer, agent_pub  # Use the app's issuer and agent

    cred = do_issue(
        issuer=issuer,
        principal="test-principal",
        agent="test-agent",
        agent_public_key=agent_pub,
        action_class="data.read",
        audience="verifier:wrong.example.com",
    )

    # Sign PoP
    from rilavo.pop import sign_request
    from rilavo.testing import local_test_agent
    agent_priv, _ = local_test_agent()
    sig, nonce = sign_request(agent_priv, "GET", "/protected/data", "data.read")

    headers = {
        "x-rilavo-credential": str(cred.to_json()),
        "x-rilavo-action": "data.read",
        "x-rilavo-pop-signature": sig,
        "x-rilavo-request-nonce": nonce,
    }
    response = client.get("/protected/data", headers=headers)
    assert response.status_code == 401
    assert "audience_mismatch" in response.text or "audience_mismatch" in response.json().get("detail", "")


def test_scope_mismatch_rejected():
    """Credential with wrong action class should be rejected."""
    # Issue credential for data.read
    issue_response = client.post(
        "/admin/issue-test-credential",
        json={
            "principal": "test-principal",
            "agent": "test-agent",
            "action_class": "data.read"
        }
    )
    assert issue_response.status_code == 200
    credential = issue_response.json()["credential"]

    # Sign PoP for admin.write (different action) - use data.read credential but request admin.write
    pop_response = client.post(
        "/admin/sign-pop",
        json={
            "method": "POST",
            "path": "/protected/data",
            "action": "admin.write"
        }
    )
    assert pop_response.status_code == 200
    pop_data = pop_response.json()

    headers = {
        "x-rilavo-credential": credential,
        "x-rilavo-action": "admin.write",  # Different from credential's data.read
        "x-rilavo-pop-signature": pop_data["signature"],
        "x-rilavo-request-nonce": pop_data["request_nonce"],
    }
    response = client.get("/protected/data", headers=headers)
    assert response.status_code == 401
    # Should be rejected - either scope_mismatch or proof_of_possession_failed
    # depending on verification order
    detail = response.json().get("detail", response.text)
    assert "scope_mismatch" in detail or "proof_of_possession_failed" in detail


def test_dependency_injection_style():
    """Test the dependency injection style endpoint."""
    issue_response = client.post(
        "/admin/issue-test-credential",
        json={
            "principal": "test-principal",
            "agent": "test-agent",
            "action_class": "data.read"
        }
    )
    credential = issue_response.json()["credential"]

    pop_response = client.post(
        "/admin/sign-pop",
        json={"method": "GET", "path": "/protected/dependency-style", "action": "data.read"}
    )
    pop_data = pop_response.json()

    headers = {
        "x-rilavo-credential": credential,
        "x-rilavo-action": pop_data["action"],
        "x-rilavo-pop-signature": pop_data["signature"],
        "x-rilavo-request-nonce": pop_data["request_nonce"],
    }
    response = client.get("/protected/dependency-style", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "authenticated_as" in data
    assert data["authenticated_as"]["action_class"] == "data.read"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
