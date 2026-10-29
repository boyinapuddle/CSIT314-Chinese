"""Structural tests for 1:1 user-story-to-Control-class traceability."""
from app.controllers import STORY_CONTROLLERS


def test_all_48_user_stories_have_a_controller():
    assert set(STORY_CONTROLLERS) == set(range(1, 49))


def test_each_user_story_uses_a_unique_controller_class():
    controllers = list(STORY_CONTROLLERS.values())
    assert len(controllers) == 48
    assert len(set(controllers)) == 48


def test_story_controllers_are_named_as_controllers():
    assert all(cls.__name__.endswith('Controller') for cls in STORY_CONTROLLERS.values())
