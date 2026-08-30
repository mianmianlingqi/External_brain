import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from brain import connect, expand, init, load, serve, serve_target, start_view_server


def _post(url: str, payload: dict):
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return urlopen(req, timeout=2)


def test_wrong_agent_secret_cannot_change():
    brain = init("analog-electronics")
    _, agent_url, stop = serve(brain, "view-secret", "agent-secret", host="127.0.0.1")
    try:
        with pytest.raises(HTTPError) as denied:
            _post(agent_url, {"method": "add_direction", "args": {"name": "italian"}, "secret": "nope"})
        assert denied.value.code == 403
        assert brain.list_directions() == ("analog-electronics",)
    finally:
        stop()


def test_view_secret_cannot_post():
    brain = init("analog-electronics")
    _, agent_url, stop = serve(brain, "view-secret", "agent-secret", host="127.0.0.1")
    try:
        with pytest.raises(HTTPError) as denied:
            _post(
                agent_url,
                {"method": "add_direction", "args": {"name": "italian"}, "secret": "view-secret"},
            )
        assert denied.value.code == 403
        assert "italian" not in brain.list_directions()
    finally:
        stop()


def test_view_only_server_rejects_empty_agent_secret():
    brain = init("analog-electronics")
    url, stop = start_view_server(brain, "view-secret")
    try:
        with pytest.raises(HTTPError) as denied:
            _post(
                url.split("?")[0] + "brain",
                {"method": "add_direction", "args": {"name": "italian"}, "secret": ""},
            )
        assert denied.value.code == 403
        assert "italian" not in brain.list_directions()
    finally:
        stop()


def test_remote_add_direction_survives_reload(tmp_path):
    expand(str(tmp_path), "analog-electronics")
    brain = load(str(tmp_path))
    agent_secret = (tmp_path / ".brain" / "agent.secret").read_text(encoding="utf-8")
    view_secret = (tmp_path / ".brain" / "view.secret").read_text(encoding="utf-8")
    _, agent_url, stop = serve(brain, view_secret, agent_secret, host="127.0.0.1")
    try:
        first = connect(agent_url, agent_secret)
        first.add_direction("italian")
        second = connect(agent_url, agent_secret)
        assert "italian" in second.list_directions()
    finally:
        stop()
    assert "italian" in load(str(tmp_path)).list_directions()


def test_serve_target_stays_up_before_init(tmp_path):
    view_url, agent_url, stop = serve_target(str(tmp_path), host="127.0.0.1")
    try:
        base = agent_url.rsplit("/", 1)[0]
        health = urlopen(base + "/health", timeout=2).read().decode("utf-8")
        assert health == "ok"
        page = urlopen(base + "/", timeout=2).read().decode("utf-8")
        assert "Init" in page
        with pytest.raises(HTTPError) as denied:
            _post(agent_url, {"method": "add_direction", "args": {"name": "italian"}, "secret": ""})
        assert denied.value.code == 403
        body = json.loads(
            _post(
                agent_url,
                {
                    "method": "expand",
                    "args": {"first_direction": "analog-electronics", "public_url": "https://brain.example"},
                },
            ).read()
        )
        remote = connect(agent_url, body["result"]["agent_secret"])
        assert "analog-electronics" in remote.list_directions()
        assert body["result"]["agent_address"] == "https://brain.example/brain"
    finally:
        stop()


def test_serve_target_reloads_direction_after_restart(tmp_path):
    _, agent_url, stop = serve_target(str(tmp_path), host="127.0.0.1")
    try:
        body = json.loads(
            _post(
                agent_url,
                {
                    "method": "expand",
                    "args": {
                        "first_direction": "analog-electronics",
                        "public_url": "https://brain.example",
                    },
                },
            ).read()
        )
        secret = body["result"]["agent_secret"]
        view_secret = body["result"]["view_secret"]
    finally:
        stop()

    view_url, agent_url, stop = serve_target(str(tmp_path), host="127.0.0.1")
    try:
        remote = connect(agent_url, secret)
        assert "analog-electronics" in remote.list_directions()
        listing = urlopen(
            view_url.split("?")[0] + "?secret=" + view_secret, timeout=2
        ).read().decode("utf-8")
        assert "analog-electronics" in listing
    finally:
        stop()


def test_remote_brain_matches_protocol_after_drill():
    brain = init("analog-electronics")
    _, agent_url, stop = serve(brain, "view-secret", "agent-secret", host="127.0.0.1")
    try:
        remote = connect(agent_url, "agent-secret")
        remote.add_direction("italian")
        point = remote.add_point("analog-electronics", "Ohm")
        question = remote.add_question(point, "What is V?", "IR")
        drill = remote.drill_named(question)
        assert remote.submit_answer(drill, "IR") is True
        assert remote.review("analog-electronics") == brain.review("analog-electronics")
        assert remote.review("analog-electronics").clear == 1
        assert "italian" in remote.list_directions()
    finally:
        stop()
