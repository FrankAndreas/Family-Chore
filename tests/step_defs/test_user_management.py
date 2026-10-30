"""
Step definitions for the game roles of the family (the family itself comes from the family hub, spec 2026-10-30).
"""

from pytest_bdd import scenarios, given, when, then, parsers
from backend import models
from tests.people import add_person_json

# Load scenarios from feature file
scenarios('../features/user_management.feature')


def _role(db, name):
    return db.query(models.Role).filter(models.Role.name == name).first()


# Given steps

@given("the system is initialized with default roles", target_fixture="seeded_db")
def system_initialized(seeded_db):
    """System has default roles."""
    return seeded_db


@given('the following roles exist:')
def roles_exist(seeded_db, datatable):
    """Verify roles exist in database."""
    # Roles are already created by seeded_db fixture
    pass


@given(parsers.parse('a family member "{nickname}" with role "{role_name}"'))
def family_member(seeded_db, nickname, role_name, context):
    """Someone the family hub lists for the app, with a game role picked here."""
    context['user'] = add_person_json(seeded_db, nickname, _role(seeded_db, role_name).id)


# When steps

@when(parsers.parse('a parent gives "{nickname}" the role "{role_name}"'))
def give_role(seeded_db, client, nickname, role_name, context):
    response = client.put(f"/users/{context['user']['id']}", json={"role_id": _role(seeded_db, role_name).id})
    context['response'] = response
    if response.status_code == 200:
        context['user'] = response.json()


# Then steps

@then(parsers.parse('the user should have role "{role_name}"'))
def user_has_role(seeded_db, context, role_name):
    role = seeded_db.query(models.Role).filter(models.Role.id == context['user']['role_id']).first()
    assert role.name == role_name


@then(parsers.parse('the user should have multiplier value {multiplier:f}'))
def user_has_multiplier(seeded_db, context, multiplier):
    role = seeded_db.query(models.Role).filter(models.Role.id == context['user']['role_id']).first()
    assert role.multiplier_value == multiplier


@then(parsers.parse('the change should be refused with "{code}"'))
def change_refused(context, code):
    assert context['response'].status_code == 400
    assert context['response'].json()['detail'] == code
