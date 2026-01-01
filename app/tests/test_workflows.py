from app.models.workflow import Workflow, Organization, Repository

def test_list_workflows_empty(client, db):
    response = client.get("/api/workflows/")
    assert response.status_code == 200
    assert response.json() == []

def test_list_workflows_with_data(client, db):
    # Create test data
    org = Organization(
        github_org_id=123,
        installation_id=456,
        name="testorg"
    )
    db.add(org)
    db.commit()
    
    repo = Repository(
        github_repo_id=789,
        org_id=org.id,
        name="test-repo",
        full_name="testorg/test-repo"
    )
    db.add(repo)
    db.commit()
    
    wf1 = Workflow(
        id=1,
        github_workflow_id=101,
        name="CI Build",
        path=".github/workflows/ci.yml",
        active=True,
        repo_id=repo.id,
        cron_expression="0 0 * * *"
    )
    wf2 = Workflow(
        id=2,
        github_workflow_id=102,
        name="Deploy",
        path=".github/workflows/deploy.yml",
        active=True,
        repo_id=repo.id,
        cron_expression=None
    )
    db.add(wf1)
    db.add(wf2)
    db.commit()

    # Test listing
    response = client.get("/api/workflows/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify data
    names = [w["name"] for w in data]
    assert "CI Build" in names
    assert "Deploy" in names
