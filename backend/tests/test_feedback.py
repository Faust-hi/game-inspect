"""Петля обратной связи: голоса копятся, предложения считаются, не применяются сами."""
from __future__ import annotations

from app.services import feedback as feedback_service


def _save(client):
    response = client.post("/api/projects", json={
        "profile": {"name": "T", "world_type": "hub", "functions": ["upscaling_frame_generation", "open_world_streaming", "geometry_pipeline"]},
        "basket": ["temporal_upscaling", "baked_occlusion_culling", "hierarchical_lod"],
    })
    assert response.status_code == 200, response.text
    return response.json()["public_id"]


def test_feedback_roundtrip(client):
    public_id = _save(client)
    response = client.post(f"/api/projects/{public_id}/feedback",
                           json={"method_code": "temporal_upscaling", "useful": True})
    assert response.status_code == 200, response.text
    assert response.json() == {"public_id": public_id, "method_code": "temporal_upscaling",
                               "up": 1, "down": 0}
    response = client.post(f"/api/projects/{public_id}/feedback",
                           json={"method_code": "temporal_upscaling", "useful": False})
    assert response.json()["down"] == 1
    assert response.json()["up"] == 0
    response = client.post(f"/api/projects/{public_id}/feedback",
                           json={"method_code": "temporal_upscaling", "useful": False})
    assert response.json()["down"] == 1


def test_feedback_rejects_unknown_method(client):
    public_id = _save(client)
    response = client.post(f"/api/projects/{public_id}/feedback",
                           json={"method_code": "no_such_method", "useful": True})
    assert response.status_code == 404


def test_feedback_rejects_unknown_project(client):
    response = client.post("/api/projects/doesnotexist123/feedback",
                           json={"method_code": "temporal_upscaling", "useful": True})
    assert response.status_code == 404


def test_summary_aggregates_across_projects(client):
    # Each saved project contributes at most one vote per included method.
    first, second = _save(client), _save(client)
    client.post(f"/api/projects/{first}/feedback",
                json={"method_code": "baked_occlusion_culling", "useful": True})
    client.post(f"/api/projects/{second}/feedback",
                json={"method_code": "baked_occlusion_culling", "useful": False})
    client.post(f"/api/projects/{second}/feedback",
                json={"method_code": "hierarchical_lod", "useful": False})
    summary = client.get("/api/admin/feedback-summary").json()
    assert summary["projects_with_feedback"] >= 2
    rows = {item["method_code"]: item for item in summary["methods"]}
    assert (rows["baked_occlusion_culling"]["up"], rows["baked_occlusion_culling"]["down"]) == (1, 1)
    assert rows["hierarchical_lod"]["down"] >= 1
    # Голосов мало — предложений быть не должно.
    assert summary["suggestions"] == []


def test_suggestions_require_quorum_and_rate():
    summary = feedback_service.summarize({"m": {"up": 1, "down": 3}})
    assert feedback_service.suggest_confidence_adjustments(summary, {"m": 0.8}) == []
    summary = feedback_service.summarize({"m": {"up": 1, "down": 5}})
    suggestions = feedback_service.suggest_confidence_adjustments(summary, {"m": 0.8})
    assert len(suggestions) == 1
    assert suggestions[0].suggested_confidence == 0.7


def test_suggestions_reward_helpful():
    summary = feedback_service.summarize({"m": {"up": 9, "down": 1}})
    suggestions = feedback_service.suggest_confidence_adjustments(summary, {"m": 0.7})
    assert suggestions[0].suggested_confidence == 0.75
