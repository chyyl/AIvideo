import asyncio

from aivscript import GenInput, Generator, MockBackend, validate
from aivscript.serialize import (
    from_json,
    from_markdown,
    from_yaml,
    to_json,
    to_markdown,
    to_yaml,
)


def make_script(duration: int = 90):
    return Generator(MockBackend()).generate(GenInput(target_duration=duration, genre="悬疑"))


def test_generation_structure():
    script = make_script()
    assert script.meta.title
    assert len(script.acts) == 3
    assert len(list(script.shots)) > 0
    assert script.duration <= script.meta.target_duration * 1.15
    assert all(shot.id for shot in script.shots)
    assert all(shot.image_prompt.en for shot in script.shots)


def test_no_errors_in_demo_script():
    issues = validate(make_script())
    assert [i for i in issues if i.level == "error"] == []


def test_yaml_json_roundtrip():
    script = make_script()
    assert from_yaml(to_yaml(script)).to_dict() == script.to_dict()
    assert from_json(to_json(script)).to_dict() == script.to_dict()


def test_markdown_roundtrip_is_lossless():
    script = make_script()
    restored = from_markdown(to_markdown(script))
    assert restored.to_dict() == script.to_dict()


def test_validation_flags_bad_script():
    script = make_script()
    script.acts[0].scenes[0].shots[0].duration = 0
    script.acts[0].scenes[0].shots.append(script.acts[0].scenes[0].shots[0])
    issues = validate(script)
    codes = {issue.code for issue in issues}
    assert "H003" in codes
    assert "H002" in codes


def test_regenerate_shot_changes_look():
    script = make_script()
    shot = next(iter(script.shots))
    new_shot = Generator(MockBackend()).regenerate_shot(GenInput(), shot)
    assert new_shot.id == shot.id
    assert new_shot.shot_size != shot.shot_size or new_shot.camera != shot.camera
