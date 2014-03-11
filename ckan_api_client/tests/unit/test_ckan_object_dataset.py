"""Tests for CkanDataset"""

import json

import pytest

from ckan_api_client.objects import CkanDataset, CkanResource
from ckan_api_client.objects.ckan_dataset import ResourcesList


def test_ckandataset_creation():
    dataset = CkanDataset({
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
        'extras': {'foo': 'bar', 'baz': 'SPAM!'},
        'groups': ['one', 'two', 'three'],
    })
    assert dataset.name == 'example-dataset'
    assert dataset.title == 'Example Dataset'
    assert dataset.groups == ['one', 'two', 'three']
    assert dataset.extras == {'foo': 'bar', 'baz': 'SPAM!'}

    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0

    assert dataset.serialize() == {
        'id': '',
        'name': 'example-dataset',
        'title': 'Example Dataset',
        'author': 'Foo Bar',
        'author_email': 'foobar@example.com',
        'license_id': '',
        'maintainer': '',
        'maintainer_email': '',
        'notes': '',
        'owner_org': '',
        'private': False,
        'state': 'active',
        'type': 'dataset',
        'url': '',
        'extras': {'foo': 'bar', 'baz': 'SPAM!'},
        'groups': ['one', 'two', 'three'],
        'resources': [],
    }


def test_ckan_dataset_resources():
    dataset = CkanDataset({
        'name': 'example-dataset',
    })
    assert dataset.is_modified() is False

    ## By asking for resources, a copy will be made,
    ## but the two items should match..
    assert isinstance(dataset.resources, ResourcesList)
    assert len(dataset.resources) == 0
    assert dataset.is_modified() is False

    ## Resources can be passed as normal objects and
    ## will be converted to CkanResource() objects.
    dataset.resources = [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    ## Make sure type conversions have been applied
    assert isinstance(dataset.resources, ResourcesList)
    for item in dataset.resources:
        assert isinstance(item, CkanResource)

    ## Make sure dataset is marked as modified
    assert dataset.is_modified() is True

    ## We allow comparison to plain objects
    assert dataset.resources == [
        {'name': 'resource-1'},
        {'name': 'resource-2'},
    ]

    ## Or to the actual types used internally, of course
    assert dataset.resources == ResourcesList([
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ])

    ## Do some tests for object serialization
    serialized = dataset.serialize()

    assert isinstance(serialized['resources'], list)
    assert len(serialized['resources']) == 2

    assert isinstance(serialized['resources'][0], dict)
    assert serialized['resources'][0]['name'] == 'resource-1'

    assert isinstance(serialized['resources'][1], dict)
    assert serialized['resources'][1]['name'] == 'resource-2'

    ## Serialized data must be json-serializable
    json.dumps(serialized)


def test_ckandataset_resources_update():
    dataset = CkanDataset({
        'name': 'example-dataset',
        'resources': [
            {'name': 'resource-1'},
            {'name': 'resource-2'},
        ]
    })
    assert dataset.is_modified() is False

    assert dataset.resources == [
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
    ]
    assert dataset.is_modified() is False

    dataset.resources.append(CkanResource({'name': 'resource-3'}))
    assert dataset.is_modified() is True
    assert dataset.resources == [
        CkanResource({'name': 'resource-1'}),
        CkanResource({'name': 'resource-2'}),
        CkanResource({'name': 'resource-3'}),
    ]

    serialized = dataset.serialize()
    assert isinstance(serialized['resources'], list)
    assert len(serialized['resources']) == 2
    assert isinstance(serialized['resources'][0], CkanResource)
    assert serialized['resources'][0].name == 'resource-1'
    assert isinstance(serialized['resources'][1], CkanResource)
    assert serialized['resources'][1].name == 'resource-2'
    assert isinstance(serialized['resources'][2], CkanResource)
    assert serialized['resources'][2].name == 'resource-3'
