from app.boundaries import LoginBoundary, STORY_BOUNDARIES
from app.controllers import RoleLoginControllerBase, STORY_CONTROLLERS


def test_all_50_user_stories_have_a_controller():
    assert set(STORY_CONTROLLERS) == set(range(1, 51))


def test_each_user_story_uses_a_unique_controller_class():
    controllers = list(STORY_CONTROLLERS.values())
    assert len(controllers) == 50
    assert len(set(controllers)) == 50


def test_story_controllers_are_named_as_controllers():
    assert all(controller.__name__.endswith("Controller") for controller in STORY_CONTROLLERS.values())


def test_all_50_user_stories_have_a_boundary_mapping():
    assert set(STORY_BOUNDARIES) == set(range(1, 51))


def test_login_stories_share_the_central_login_boundary():
    for story in [11, 18, 35, 47]:
        assert STORY_BOUNDARIES[story] is LoginBoundary


def test_non_login_story_boundaries_are_unique():
    login_stories = {11, 18, 35, 47}
    boundaries = [boundary for story, boundary in STORY_BOUNDARIES.items() if story not in login_stories]
    assert len(boundaries) == len(set(boundaries))


def test_story_boundaries_are_named_as_boundaries():
    assert all(boundary.__name__.endswith("Boundary") for boundary in STORY_BOUNDARIES.values())


def test_login_story_controllers_share_role_login_procedure():
    for story in [11, 18, 35, 47]:
        assert issubclass(STORY_CONTROLLERS[story], RoleLoginControllerBase)


def test_login_story_controllers_keep_unique_roles():
    roles = [STORY_CONTROLLERS[story].role for story in [11, 18, 35, 47]]
    assert roles == [
        "User Admin",
        "Interior Designer",
        "Customer",
        "Platform Manager",
    ]


def test_story_49_has_dedicated_delete_profile_classes():
    assert STORY_CONTROLLERS[49].__name__ == "DeleteUserProfileController"
    assert STORY_BOUNDARIES[49].__name__ == "DeleteUserProfileBoundary"


def test_story_50_has_dedicated_read_only_browse_classes():
    assert STORY_CONTROLLERS[50].__name__ == "BrowseIDPController"
    assert STORY_BOUNDARIES[50].__name__ == "BrowseIDPBoundary"
