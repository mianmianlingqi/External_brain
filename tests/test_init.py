from pathlib import Path

import pytest

from brain import NotABrain, ask_init, expand, load


def test_expand_yields_running_brain_and_secrets(tmp_path: Path):
    brain, agent_secret, view_secret = expand(str(tmp_path), "analog-electronics")
    assert agent_secret
    assert view_secret
    assert (tmp_path / ".brain" / "agent.secret").read_text(encoding="utf-8") == agent_secret
    assert (tmp_path / ".brain" / "view.secret").read_text(encoding="utf-8") == view_secret
    assert (tmp_path / "WORKSPACE.md").exists()
    assert brain.review("analog-electronics").clear == 0


def test_load_before_expand_is_not_a_brain(tmp_path: Path):
    with pytest.raises(NotABrain):
        load(str(tmp_path))


def test_load_after_expand_can_review(tmp_path: Path):
    expand(str(tmp_path), "analog-electronics")
    brain = load(str(tmp_path))
    assert brain.review("analog-electronics").misses == 0


def test_expand_records_address_and_view_link(tmp_path: Path):
    expand(str(tmp_path), "analog-electronics")
    assert (tmp_path / ".brain" / "agent.address").read_text(encoding="utf-8").startswith("file://")
    assert "secret=" in (tmp_path / ".brain" / "view.link").read_text(encoding="utf-8")


def test_expand_server_writes_public_urls(tmp_path: Path):
    _, _, view_secret = expand(
        str(tmp_path), "analog-electronics", kind="server", public_url="https://brain.fly.dev"
    )
    assert (tmp_path / ".brain" / "agent.address").read_text(encoding="utf-8") == "https://brain.fly.dev/brain"
    assert (tmp_path / ".brain" / "view.link").read_text(encoding="utf-8") == f"https://brain.fly.dev/?secret={view_secret}"
    assert (tmp_path / ".brain" / "target").read_text(encoding="utf-8") == "server"


def test_load_keeps_points_after_expand(tmp_path: Path):
    brain, _, _ = expand(str(tmp_path), "analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    brain.add_question(point, "What is V?", "IR")
    loaded = load(str(tmp_path))
    assert loaded.review("analog-electronics").not_clear == 1


def test_ask_init_asks_direction_and_target(tmp_path: Path):
    answers = iter(["analog-electronics", "server", "https://brain.example"])
    brain, _, _ = ask_init(str(tmp_path), input_fn=lambda _: next(answers))
    assert "analog-electronics" in brain.list_directions()
    assert (tmp_path / ".brain" / "target").read_text(encoding="utf-8") == "server"
    assert (tmp_path / ".brain" / "agent.address").read_text(encoding="utf-8") == "https://brain.example/brain"


def test_expand_again_does_not_change_direction(tmp_path: Path):
    expand(str(tmp_path), "analog-electronics")
    brain, _, _ = expand(str(tmp_path), "italian")
    assert "analog-electronics" in brain.list_directions()
    assert "italian" not in brain.list_directions()
