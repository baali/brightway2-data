# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import bw2test
from bw2data import parameters, projects, Database
from bw2data.parameters import (
    ActivityParameter,
    DatabaseParameter,
    Group,
    GroupDependency,
    ParameterizedExchange,
    parameters,
    ProjectParameter,
)
from bw2parameters.errors import MissingName
from peewee import IntegrityError
import pytest
import time


######################
### Project parameters
######################

@bw2test
def test_project_parameters():
    assert not len(parameters)
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    assert obj.name == "foo"
    assert obj.amount == 3.14
    assert obj.data == {'uncertainty type': 0}
    assert str(obj)
    assert isinstance(str(obj), str)

@bw2test
def test_project_parameter_autocreate_group():
    assert not Group.select().count()
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    assert Group.get(name='project')
    assert not Group.get(name='project').fresh

@bw2test
def test_expire_downstream():
    Group.create(fresh=True, name="A")
    Group.create(fresh=True, name="B")
    GroupDependency.create(group="B", depends="A")
    assert Group.get(name="A").fresh
    assert Group.get(name="B").fresh
    ProjectParameter.expire_downstream("A")
    assert not Group.get(name="B").fresh

@bw2test
def test_project_parameters_ordering():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    with pytest.raises(TypeError):
        obj < 0
    assert not (obj < obj)
    another = ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    assert another < obj

@bw2test
def test_project_parameters_dict():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    expected = {
        'name': 'foo',
        'amount': 3.14,
        'uncertainty type': 0,
    }
    assert obj.dict == expected


@bw2test
def test_project_parameters_load():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    another = ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    expected = {
        'foo': {'amount': 3.14, 'uncertainty type': 0},
        'bar': {'formula': '2 * foo'}
    }
    assert ProjectParameter.load() == expected

@bw2test
def test_project_parameters_static():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    another = ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    assert ProjectParameter.static() == {'foo': 3.14, 'bar': None}
    assert ProjectParameter.static(only=['foo']) == {'foo': 3.14}
    ProjectParameter.recalculate()
    assert ProjectParameter.static() == {'foo': 3.14, 'bar': 2 * 3.14}
    assert ProjectParameter.static(only=['bar']) == {'bar': 2 * 3.14}

@bw2test
def test_project_parameters_expired():
    assert not ProjectParameter.expired()
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    assert ProjectParameter.expired()
    ProjectParameter.recalculate()
    assert not ProjectParameter.expired()

@bw2test
def test_project_parameters_recalculate():
    ProjectParameter.recalculate()
    Group.create(name="project")
    ProjectParameter.recalculate()
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    another = ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    ProjectParameter.recalculate()
    obj = ProjectParameter.get(name="bar")
    assert obj.amount == 2 * 3.14

@bw2test
def test_project_parameters_expire_downstream():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    Group.create(name="bar")
    GroupDependency.create(group="bar", depends="project")
    assert Group.get(name="bar").fresh
    ProjectParameter.recalculate()
    assert not Group.get(name="bar").fresh

@bw2test
def test_project_autoupdate_triggers():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    first = Group.get(name="project").updated
    time.sleep(1.1)
    another = ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    second = Group.get(name="project").updated
    assert first != second
    time.sleep(1.1)
    ProjectParameter.update(amount=7).execute()
    third = Group.get(name="project").updated
    assert second != third
    time.sleep(1.1)
    ProjectParameter.get(name="foo").delete_instance()
    fourth = Group.get(name="project").updated
    assert fourth != third

@bw2test
def test_project_name_uniqueness():
    obj = ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    with pytest.raises(IntegrityError):
        ProjectParameter.create(
            name="foo",
            amount=7,
        )

#######################
### Database parameters
#######################

@bw2test
def test_create_database_parameters():
    assert not len(parameters)
    obj = DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    assert obj.name == "foo"
    assert obj.database == "bar"
    assert obj.amount == 3.14
    assert str(obj)
    assert isinstance(str(obj), str)
    assert len(parameters)

@bw2test
def test_database_parameters_group_autocreated():
    assert not Group.select().count()
    obj = DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    assert Group.get(name='bar')
    assert not Group.get(name='bar').fresh

@bw2test
def test_database_parameters_expired():
    assert not DatabaseParameter.expired('bar')
    DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    assert DatabaseParameter.expired('bar')

@bw2test
def test_database_parameters_dict():
    obj = DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    expected = {
        'database': 'bar',
        'name': 'foo',
        'amount': 3.14,
    }
    assert obj.dict == expected

@bw2test
def test_database_parameters_load():
    DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    DatabaseParameter.create(
        database='bar',
        name="baz",
        formula="foo + baz"
    )
    expected = {
        'foo': {'database': 'bar', 'amount': 3.14},
        'baz': {'database': 'bar', 'formula': "foo + baz"}
    }
    assert DatabaseParameter.load("bar") == expected

@bw2test
def test_database_parameters_static():
    DatabaseParameter.create(
        database='bar',
        name="foo",
        amount=3.14,
    )
    DatabaseParameter.create(
        database='bar',
        name="baz",
        amount=7,
        formula="foo + baz"
    )
    expected = {
        'foo': 3.14,
        'baz': 7
    }
    assert DatabaseParameter.static("bar") == expected
    assert DatabaseParameter.static("bar", only=['baz']) == {'baz': 7}

@bw2test
def test_database_parameters_check():
    with pytest.raises(IntegrityError):
        DatabaseParameter.create(
            database='project',
            name="foo",
            amount=3.14,
        )

@bw2test
def test_database_autoupdate_triggers():
    obj = DatabaseParameter.create(
        database="A",
        name="foo",
        amount=3.14,
    )
    first = Group.get(name="A").updated
    time.sleep(1.1)
    another = DatabaseParameter.create(
        database="A",
        name="bar",
        formula="2 * foo",
    )
    second = Group.get(name="A").updated
    assert first != second
    time.sleep(1.1)
    DatabaseParameter.update(amount=7).execute()
    third = Group.get(name="A").updated
    assert second != third
    time.sleep(1.1)
    DatabaseParameter.get(name="foo").delete_instance()
    fourth = Group.get(name="A").updated
    assert fourth != third

@bw2test
def test_database_uniqueness_constraint():
    DatabaseParameter.create(
        database="A",
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    with pytest.raises(IntegrityError):
        DatabaseParameter.create(
            database="A",
            name="foo",
            amount=7,
        )

@bw2test
def test_update_database_parameters():
    assert not Group.select().count()
    assert not GroupDependency.select().count()

    DatabaseParameter.create(
        database='A',
        name="B",
        amount=5,
    )
    o = DatabaseParameter.create(
        database='A',
        name="C",
        formula="B * 2 + foo",
    )
    Group.create(name="Zed")
    GroupDependency.create(group="Zed", depends="A")
    assert Group.get(name="A")
    with pytest.raises(MissingName):
        DatabaseParameter.recalculate("A")
    o.formula = "B * 2"
    o.save()
    DatabaseParameter.recalculate("A")
    assert Group.get(name="A").fresh
    assert DatabaseParameter.get(name="C").amount == 10
    assert not Group.get(name="Zed").fresh

    o.formula = "B * 2 + foo + bar"
    o.save()
    ProjectParameter.create(
        name="foo",
        amount=3.14,
        data={'uncertainty type': 0}
    )
    ProjectParameter.create(
        name="bar",
        formula="2 * foo",
    )
    assert Group.get(name="project")
    Database("A").register()

    obj = DatabaseParameter.get(name="C")
    assert obj.amount != 3.14 * 3 + 10
    with pytest.raises(GroupDependency.DoesNotExist):
        GroupDependency.get(group="A", depends="project")

    DatabaseParameter.recalculate("A")
    assert GroupDependency.get(group="A", depends="project")
    assert Group.get(name="A")
    assert Group.get(name="project")
    obj = DatabaseParameter.get(name="C")
    assert obj.amount == 3.14 * 3 + 10

###########################
### Parameterized exchanges
###########################

@bw2test
def test_create_parameterized_exchange():
    assert not ParameterizedExchange.select().count()
    obj = ParameterizedExchange.create(
        group="A",
        exchange=42,
        formula="foo + bar"
    )
    assert obj.group == "A"
    assert obj.exchange == 42
    assert obj.formula == "foo + bar"
    assert ParameterizedExchange.select().count()

#######################
### Activity parameters
#######################

@bw2test
def test_create_activity_parameter():
    assert not ActivityParameter.select().count()
    obj = ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        amount=3.14
    )
    assert obj.group == "A"
    assert obj.database == "B"
    assert obj.code == "C"
    assert obj.name == "D"
    assert obj.amount == 3.14
    assert str(obj)
    assert isinstance(str(obj), str)
    assert ActivityParameter.select().count()
    assert len(parameters)

@bw2test
def test_activity_parameters_group_autocreated():
    assert not Group.select().count()
    ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        amount=3.14
    )
    assert Group.get(name='A')
    assert not Group.get(name='A').fresh

@bw2test
def test_activity_parameter_expired():
    assert not ActivityParameter.expired("A")
    ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        amount=3.14
    )
    assert ActivityParameter.expired("A")
    Group.get(name="A").freshen()
    assert not ActivityParameter.expired("A")

@bw2test
def test_activity_parameter_dict():
    a = ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        amount=3.14
    )
    expected = {
        'database': 'B',
        'code': 'C',
        'name': 'D',
        'amount': 3.14
    }
    assert a.dict == expected
    b = ActivityParameter.create(
        group="A",
        database="B",
        code="E",
        name="F",
        amount=7,
        data={"foo": "bar"},
        formula="7 * 1"
    )
    expected = {
        'database': 'B',
        'code': 'E',
        'name': 'F',
        'amount': 7,
        'foo': 'bar',
        'formula': "7 * 1"
    }
    assert b.dict == expected

@bw2test
def test_activity_parameter_load():
    ActivityParameter.create(
        group="A",
        database="B",
        code="E",
        name="F",
        amount=7,
        data={"foo": "bar"},
        formula="7 * 1"
    )
    expected = {'F': {
        'database': 'B',
        'code': 'E',
        'amount': 7,
        'foo': 'bar',
        'formula': "7 * 1"
    }}
    assert ActivityParameter.load("A") == expected

@bw2test
def test_activity_parameter_static():
    # Only, full
    pass

@bw2test
def test_activity_parameter_recalculate_shortcut():
    assert not ActivityParameter.recalculate("A")
    ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        amount=3.14
    )
    Group.get(name="A").freshen()
    assert not ActivityParameter.recalculate("A")

@bw2test
def test_activity_parameter_dependency_chain():
    pass

@bw2test
def test_activity_parameter_static_dependencies():
    # with, without
    pass

@bw2test
def test_activity_parameter_recalculate():
    Database("B").register()
    ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        formula="2 ** 3"
    )
    ActivityParameter.create(
        group="A",
        database="B",
        code="E",
        name="F",
        formula="2 * D"
    )
    assert not Group.get(name="A").fresh
    ActivityParameter.recalculate("A")
    assert ActivityParameter.get(name="D").amount == 8
    assert ActivityParameter.get(name="F").amount == 16
    assert Group.get(name="A").fresh

    Database("K").register()
    ActivityParameter.create(
        group="G",
        database="K",
        code="H",
        name="J",
        formula="F + D * 2"
    )
    ActivityParameter.create(
        group="G",
        database="K",
        code="E",
        name="F",
        amount=3,
    )
    assert not Group.get(name="G").fresh
    with pytest.raises(MissingName):
        ActivityParameter.recalculate("G")

    assert not Group.get(name="G").fresh
    g = Group.get(name="G")
    g.order = ["A"]
    g.save()
    ActivityParameter.recalculate("G")
    assert Group.get(name="G").fresh
    assert ActivityParameter.get(name="J").amount == 19
    assert ActivityParameter.get(name="F", database="K").amount == 3

    DatabaseParameter.create(
        database="B",
        name="foo",
        formula="2 ** 2",
    )
    ProjectParameter.create(
        name="bar",
        formula="2 * 2 * 2",
    )
    a = ActivityParameter.get(database="B", code="E")
    a.formula = "foo + bar + D"
    a.save()
    assert not Group.get(name="A").fresh
    ActivityParameter.recalculate("A")
    assert ActivityParameter.get(database="B", code="E").amount == 4 + 8 + 8
    assert Group.get(name="A").fresh

@bw2test
def test_activity_parameter_crossdatabase_triggers():
    ActivityParameter.create(
        group="A",
        database="B",
        name="C",
        code="D"
    )
    with pytest.raises(IntegrityError):
        ActivityParameter.create(
            group="A",
            database="E",
            name="F",
            code="G"
        )
    with pytest.raises(IntegrityError):
        a = ActivityParameter.get(name="C")
        a.database = "E"
        a.save()
    with pytest.raises(IntegrityError):
        ActivityParameter.update(database="C").execute()

@bw2test
def test_activity_parameter_crossgroup_triggers():
    ActivityParameter.create(
        group="A",
        database="B",
        name="C",
        code="D",
        amount=11,
    )
    with pytest.raises(IntegrityError):
        ActivityParameter.create(
            group="E",
            database="B",
            name="C",
            code="D",
            amount=1,
        )
    ActivityParameter.create(
        group="E",
        database="B",
        name="C",
        code="F",
        amount=1,
    )

@bw2test
def test_activity_parameter_autoupdate_triggers():
    obj = ActivityParameter.create(
        group="A",
        database="B",
        name="C",
        code="D",
        amount=11,
    )
    first = Group.get(name="A").updated
    time.sleep(1.1)
    another = ActivityParameter.create(
        group="A",
        database="B",
        code="E",
        name="F",
        formula="2 * foo",
    )
    second = Group.get(name="A").updated
    assert first != second
    time.sleep(1.1)
    ActivityParameter.update(amount=7).execute()
    third = Group.get(name="A").updated
    assert second != third
    time.sleep(1.1)
    ActivityParameter.get(name="F").delete_instance()
    fourth = Group.get(name="A").updated
    assert fourth != third

@bw2test
def test_activity_parameter_checks_uniqueness_constraints():
    ActivityParameter.create(
        group="A",
        database="B",
        name="C",
        code="D",
        amount=11,
    )
    with pytest.raises(IntegrityError):
        ActivityParameter.create(
            group="A",
            database="B",
            name="C",
            code="G",
            amount=111,
        )

@bw2test
def test_activity_parameter_checks():
    with pytest.raises(IntegrityError):
        ActivityParameter.create(
            group="project",
            database="E",
            name="F",
            code="G"
        )
    with pytest.raises(IntegrityError):
        ActivityParameter.create(
            group="E",
            database="E",
            name="F",
            code="G"
        )

##########
### Groups
##########

@bw2test
def test_group():
    o = Group.create(name="foo")
    assert o.fresh
    o.expire()
    assert not o.fresh
    o = Group.get(name="foo")
    assert not o.fresh
    o.freshen()
    assert o.fresh
    o = Group.get(name="foo")
    assert o.fresh
    with pytest.raises(IntegrityError):
        Group.create(name="foo")
    Group.create(name="bar")

@bw2test
def test_group_purging():
    Database("A").register()
    Database("B").register()
    o = Group.create(
        name="one",
        order=["C", "project", "B", "D", "A"]
    )
    expected = ["C", "D"]
    assert o.updated
    assert o.fresh
    assert o.order == expected
    assert Group.get(name="one").order == expected

######################
### Group dependencies
######################

@bw2test
def test_group_dependency():
    d = GroupDependency.create(group="foo", depends="bar")
    assert d.group == "foo"
    assert d.depends == "bar"

@bw2test
def test_group_dependency_save_checks():
    with pytest.raises(ValueError):
        GroupDependency.create(group="project", depends="foo")
    Database("A").register()
    GroupDependency.create(group="A", depends="project")
    with pytest.raises(ValueError):
        GroupDependency.create(group="A", depends="foo")

@bw2test
def test_group_dependency_constraints():
    GroupDependency.create(group="foo", depends="bar")
    with pytest.raises(IntegrityError):
        GroupDependency.create(group="foo", depends="bar")
    with pytest.raises(IntegrityError):
        GroupDependency.create(group="foo", depends="foo")

@bw2test
def test_group_dependency_circular():
    GroupDependency.create(group="foo", depends="bar")
    with pytest.raises(IntegrityError):
        GroupDependency.create(group="bar", depends="foo")

######################
### Parameters manager
######################

@bw2test
def test_parameters_new_project_parameters():
    with pytest.raises(AssertionError):
        parameters.new_project_parameters([{'name': 'foo'}, {'name': 'foo'}])
    data = [
        {'name': 'foo', 'amount': 4},
        {'name': 'bar', 'formula': 'foo + 3'},
    ]
    assert not len(parameters)
    parameters.new_project_parameters(data)
    assert len(parameters) == 2
    assert ProjectParameter.get(name="foo").amount == 4
    assert ProjectParameter.get(name="bar").amount == 7
    assert Group.get(name="project").fresh

@bw2test
def test_parameters_repr():
    assert repr(parameters) == "Parameters manager with 0 objects"

@bw2test
def test_parameters_recalculate():
    Database("B").register()
    ActivityParameter.create(
        group="A",
        database="B",
        code="C",
        name="D",
        formula="2 ** 3"
    )
    ActivityParameter.create(
        group="A",
        database="B",
        code="E",
        name="F",
        formula="foo + bar + D"
    )
    DatabaseParameter.create(
        database="B",
        name="foo",
        formula="2 ** 2",
    )
    ProjectParameter.create(
        name="bar",
        formula="2 * 2 * 2",
    )
    parameters.recalculate()
    assert ProjectParameter.get(name="bar").amount == 8
    assert DatabaseParameter.get(name="foo").amount == 4
    assert ActivityParameter.get(name="F").amount == 20
    assert ActivityParameter.get(name="D").amount == 8

@bw2test
def test_parameters_new_database_parameters():
    with pytest.raises(AssertionError):
        parameters.new_database_parameters([], 'another')
    Database("another").register()
    with pytest.raises(AssertionError):
        parameters.new_database_parameters([{'name': 'foo'}, {'name': 'foo'}], 'another')
    data = [
        {'name': 'foo', 'amount': 4},
        {'name': 'bar', 'formula': 'foo + 3'},
    ]
    assert not len(parameters)
    parameters.new_database_parameters(data, "another")
    assert len(parameters) == 2
    assert DatabaseParameter.get(name="foo").amount == 4
    assert DatabaseParameter.get(name="bar").amount == 7
    assert Group.get(name="another").fresh

@bw2test
def test_parameters_new_activity_parameters_errors():
    pass

@bw2test
def test_parameters_new_activity_parameters():
    with pytest.raises(AssertionError):
        parameters.new_database_parameters([], 'another')
    Database("another").register()
    with pytest.raises(AssertionError):
        parameters.new_database_parameters([{'name': 'foo'}, {'name': 'foo'}], 'another')
    data = [
        {'name': 'foo', 'amount': 4},
        {'name': 'bar', 'formula': 'foo + 3'},
    ]
    assert not len(parameters)
    parameters.new_database_parameters(data, "another")
    assert len(parameters) == 2
    assert DatabaseParameter.get(name="foo").amount == 4
    assert DatabaseParameter.get(name="bar").amount == 7
    assert Group.get(name="another").fresh
