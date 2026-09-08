"""Persistence, catalogue revisions and exchange preserve the actual calculation."""
import json

from app.models.entities import Method, Project
from app.schemas.catalog import ProjectProfile, input_fingerprint
from app.services.catalog_revision import published_revision
from app.services import gower
from sqlalchemy import select


def test_fingerprint_canonical_sets_and_resolution():
    a = ProjectProfile(functions=["b", "a"], target_resolution="4k")
    b = ProjectProfile(functions=["a", "b"], target_resolution="2160p")
    assert input_fingerprint(a, ["x", "y", "x"]) == input_fingerprint(b, ["y", "x"])


def test_catalog_revision_tracks_content_not_timestamps(db):
    before = published_revision(db)
    method = db.scalar(select(Method).where(Method.status == "published"))
    method.summary += " Revised explanation."
    assert published_revision(db) != before
    method.status = "draft"
    draft = published_revision(db)
    method.summary += " private edit"
    assert published_revision(db) == draft


def test_full_snapshot_survives_catalogue_edit_and_file_roundtrip(client, db):
    saved = client.post('/api/projects', json={"profile": {}, "basket": []}).json()
    assert saved["result"]["snapshot_id"]
    assert saved["result"]["hardware"]["caveats"]
    method = db.scalar(select(Method).where(Method.status == "published"))
    method.summary += " changed"
    db.flush()
    loaded = client.get('/api/projects/' + saved["public_id"]).json()
    assert loaded["result"] == saved["result"]
    payload = {"format": "gamedev-dss-project", "version": 2,
               "exported_at": "2026-09-08T12:00:00Z", "profile": loaded["profile"],
               "basket": loaded["basket"], "result": loaded["result"]}
    response = client.post('/api/project-file-import', files={"file": ('p.json', json.dumps(payload))})
    assert response.status_code == 200, response.text
    assert response.json()["result"] == saved["result"]
    payload["profile"]["target_fps"] = 144
    assert client.post('/api/project-file-import', files={"file": ('p.json', json.dumps(payload))}).status_code == 422


def test_legacy_project_does_not_invent_history(client, db):
    db.add(Project(public_id="legacy123", name="old", profile={}, basket=[],
                   result={"snapshot": ["temporal_upscaling"]}))
    db.flush()
    body = client.get('/api/projects/legacy123').json()
    assert body["result"] is None
    assert body["snapshot_status"] == "legacy_incomplete"


def test_unknown_file_version_and_structure_rejected(client):
    for payload in ({}, {"format": "gamedev-dss-project", "version": 999}, [], "text"):
        response = client.post('/api/project-file-import', files={"file": ('p.json', json.dumps(payload))})
        assert response.status_code == 422
        assert response.json()["request_id"]


def test_feedback_outside_snapshot_is_rejected(client):
    project = client.post('/api/projects', json={"profile": {}, "basket": []}).json()
    response = client.post('/api/projects/' + project["public_id"] + '/feedback',
                           json={"method_code": "temporal_upscaling", "useful": True})
    assert response.status_code == 409


def test_unknown_levels_and_engines_do_not_claim_similarity():
    vector = gower.project_vector(ProjectProfile(object_count_level="unknown", npc_count_level="unknown"))
    assert vector["object_count"] is None and vector["npc_count"] is None
    assert gower.canonical_engine('custom') is None
    assert gower.canonical_engine('id tech 7') != gower.canonical_engine('Decima')


def test_unknown_basket_is_preserved_in_fingerprint(client):
    empty = client.post('/api/recommend', json={"profile": {}, "basket": []}).json()
    unknown = client.post('/api/recommend', json={"profile": {}, "basket": ["obsolete_method"]}).json()
    assert unknown['input_key'] != empty['input_key']
    assert any(risk['code'] == 'unknown_method' for risk in unknown['risks'])
