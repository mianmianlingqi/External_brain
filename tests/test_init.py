from pathlib import Path

import pytest

from brain import NotABrain, expand, load


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
