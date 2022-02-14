import copy
import time
from typing import List

import pytest
from input_parameters import (
    default_char_acq_params,
    default_mesh_params,
    test_edit_task,
    test_sample_1,
    test_sample_5,
    test_sample_6,
    test_task,
)
from wrapper.api_client import APIClient


from fixture import client

    Tests MXCube3 Flask endpoints relevant to the sample queue.
    """

def test_queue_get(client):
    """Test if we can get the queue."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert resp.status_code == 200

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        # Clear exisiting queue.
        client.queue.put("/clear", data={})

def test_add_and_get_sample(client):
    """Test if we can add a sample. The sample is added by a fixture."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert resp.status_code == 200 and json.loads(resp.data).get("1:05")

        # Update sample 5 with test task.
        queue = client.queue.get("/")
        queue_id = queue["1:05"]["queueID"]
        task_to_add = copy.deepcopy(test_task)
        task_to_add["queueID"] = queue_id
        task_to_add["tasks"][0]["sampleQueueID"] = queue_id
        client.queue.post("/", data=[task_to_add])

def test_add_and_get_task(client):
    """Test if we can add a task to the sample."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        sample : dict
            Sample to attempt to add to the queue.
        """
        # Clear exisiting queue.
        client.queue.put("/clear", data={})

def test_add_and_edit_task(client):
    """Test if we can add edit a task i the sample in the queue."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    queue_id = json.loads(resp.data).get("1:05")["queueID"]
    task_queue_id = json.loads(resp.data).get("1:05")["tasks"][0]["queueID"]

        # Verify sample has been successfully added to the queue.
        data = client.queue.get("/")
        queue_samples = data.get("sample_order", [])
        assert sample["sampleID"] in queue_samples

    def test_queue_get(self, client: APIClient) -> None:
        """Test if we can fetch the queue.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        data = client.queue.get("/")
        assert isinstance(data, dict)

def test_queue_start(client):
    """
    Test if we can start the queue.
    The queue requires a sample and a task to start which are added by fixtures.
    It also requires a 3d point to be saved before it move from paused state to running.
    Unpause is called to mimick that.
    """
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        client.queue.put("/clear", data={})

    def test_add_and_get_task(self, client: APIClient) -> None:
        """Test if we can add a task to a sample.

    time.sleep(1)

    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("queueStatus") == "QueueRunning"
    )

        # Add task to existing sample.
        client.queue.post("/", data=[test_task])

        # Verify task has been added to sample in queue successfully.
        data = client.queue.get("/")
        assert isinstance(data, dict)
        assert len(data.get("1:05", {}).get("tasks", [])) == 1

    def test_add_and_edit_task(self, client: APIClient) -> None:
        """Test if we can edit a sample task in the queue.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        # Reset queue to known state.
        self.queue_set_known_state(client)

    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("queueStatus") == "QueueRunning"
    )

        task_to_update = copy.deepcopy(test_edit_task)
        task_to_update["parameters"]["num_images"] = 10
        data = client.queue.post(
            "/%s/%s" % (queue_id, task_queue_id), data=task_to_update, is_json=True
        )

    time.sleep(2)
    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("queueStatus") == "QueueStopped"
    )

    def test_queue_get_state(self, client: APIClient) -> None:
        """Test if we can get the queue state.

def test_queue_abort(client):
    """Test if we can abort the queue. The queue is started and then aborted."""
    resp = client.put(
        "/mxcube/api/v0.1/queue/start",
        data=json.dumps({"sid": "1:05"}),
        content_type="application/json",
    )
    assert resp.status_code == 200

        It requires a 3d point to be saved before it move from paused state to running.
        Unpause is called to mimick that.

    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("queueStatus") == "QueueRunning"
    )

        # Start the queue.
        client.queue.put("/start", data={"sid": "1:05"})
        client.queue.put("/unpause", data={})

    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("queueStatus") == "QueueStopped"
    )

        # Verify queue has started.
        queue_state = client.queue.get("/queue_state")
        assert (
            isinstance(queue_state, dict)
            and queue_state.get("queueStatus") == "QueueRunning"
        )

    def test_queue_stop(self, client: APIClient) -> None:
        """Test if we can stop the queue.
        The queue is started and then stopped.

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert len(json.loads(resp.data)) == 0

        # Start the queue.
        client.queue.put("/start", data={"sid": "1:05"})
        client.queue.put("/unpause", data={})

def test_queue_get_state(client):
    """Test if we can get the queue state."""
    resp = client.get("/mxcube/api/v0.1/queue/queue_state")
    assert resp.status_code == 200

        # Stop the queue.
        client.queue.put("/stop", data={})

def test_queue_delete_item(client):
    """Test if we can delete a task from sample in the queue."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

        # Verify queue has stopped.
        queue_state = client.queue.get("/queue_state")
        assert (
            isinstance(queue_state, dict)
            and queue_state.get("queueStatus") == "QueueStopped"
        )

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 0
    )

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        # Reset queue to known state.
        self.queue_set_known_state(client)

def test_queue_enable_item(client):
    """Test if we can disable a task in the sample in queue."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    queue_id = json.loads(resp.data).get("1:05")["queueID"]

        # Verify queue has started.
        queue_state = client.queue.get("/queue_state")
        assert (
            isinstance(queue_state, dict)
            and queue_state.get("queueStatus") == "QueueRunning"
        )

        # Abort the running queue.
        client.queue.put("/abort", data={})

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("1:05")["checked"] is False
    )

    def test_queue_delete_item(self, client: APIClient) -> None:
        """Test if we can delete a task from sample in the queue.

def test_queue_swap_task_item(client):
    """Test if we can swap tasks in a sample in queue. Two tasks are added with a different param and then swaped and tested"""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 1

    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([task_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 2
    )

    def test_queue_enable_item(self, client: APIClient) -> None:
        """Test if we can disable a task in the sample in queue.

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("1:05")["tasks"][0]["parameters"]["kappa"] == 90
    )

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 1

def test_queue_move_task_item(client):
    """Test if we can move tasks in a sample in queue.
    Three tasks are added with a different param and then moved and tested."""
    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

        client.queue.post(
            "/set_enabled", data={"qidList": [queue_id], "enabled": False}
        )

    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([task_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 2
    )

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        # Reset queue to known state.
        self.queue_set_known_state(client)

    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([task_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 3
    )

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 2

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("1:05")["tasks"][2]["parameters"]["kappa"] == 0
    )

        # Verify the task has been swaped.
        queue = client.queue.get("/")
        assert (
            isinstance(queue, dict)
            and queue["1:05"]["tasks"][0]["parameters"]["kappa"] == 90
        )

def test_queue_move_task_item_fail(client):
    """Test if we can move tasks in a sample in queue with boundry condition.
    Three tasks are added with a different param and then moved and tested."""

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 1
    )

    queue_id = json.loads(resp.data).get("1:05")["queueID"]
    task_to_add = test_task
    task_to_add["queueID"] = queue_id
    task_to_add["tasks"][0]["sampleQueueID"] = queue_id
    task_to_add["tasks"][0]["parameters"]["kappa"] = 90
    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([task_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 2
    )

    task_to_add = test_task
    task_to_add["queueID"] = queue_id
    task_to_add["tasks"][0]["sampleQueueID"] = queue_id
    task_to_add["tasks"][0]["parameters"]["kappa"] = 180
    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([task_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200 and len(json.loads(resp.data).get("1:05")["tasks"]) == 3
    )

    resp = client.post(
        ("/mxcube/api/v0.1/queue/{}/{}/{}/move").format("1:05", 2, 2),
        content_type="application/json",
    )
    resp = client.get("/mxcube/api/v0.1/queue/")

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 3

        client.queue.post("/%s/%s/%s/move" % ("1:05", 0, 2), data={})

def test_queue_set_sample_order(client):
    """Test if we can set the sample order in the queue."""
    sample_to_add = test_sample_6
    resp = client.post(
        "/mxcube/api/v0.1/queue/",
        data=json.dumps([sample_to_add]),
        content_type="application/json",
    )
    assert resp.status_code == 200

    def test_queue_move_task_item_fail(self, client: APIClient) -> None:
        """Test if we can move tasks in a sample in queue with boundry condition.
        Three tasks are added with a different param and then moved and tested.

    resp = client.get("/mxcube/api/v0.1/queue/")
    assert (
        resp.status_code == 200
        and json.loads(resp.data).get("sample_order")[1] == "1:06"
    )

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 1

def assert_and_remove_keys_with_random_value(parameters):
    assert "osc_start" in parameters["acq_parameters"]
    assert "energy" in parameters["acq_parameters"]
    assert "resolution" in parameters["acq_parameters"]
    assert "kappa" in parameters["acq_parameters"]
    assert "kappa_phi" in parameters["acq_parameters"]

    parameters["acq_parameters"].pop("osc_start")
    parameters["acq_parameters"].pop("energy")
    parameters["acq_parameters"].pop("resolution")
    parameters["acq_parameters"].pop("kappa")
    parameters["acq_parameters"].pop("kappa_phi")


def test_get_default_dc_params(client):
    """Test if we get the right default data collection params."""

    resp = client.get("/mxcube/api/v0.1/queue/available_tasks")
    actual = json.loads(resp.data)["datacollection"]

    # some values are taken from current value/position which is random,
    # so ignore those. But make sure they keys exist
    assert_and_remove_keys_with_random_value(actual)

        queue = client.queue.get("/")
        assert isinstance(queue, dict) and len(queue["1:05"]["tasks"]) == 3

        client.queue.post("/%s/%s/%s/move" % ("1:05", 2, 2), data={})

def test_get_default_char_acq_params(client):
    """Test if we get the right default characterisation acq params."""
    resp = client.get("/mxcube/api/v0.1/queue/available_tasks")
    actual = json.loads(resp.data)["characterisation"]

    # some values are taken from current value/position which is random,
    # so ignore those. But make sure they keys exist
    assert_and_remove_keys_with_random_value(actual)

    assert resp.status_code == 200 and actual == default_char_acq_params

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        sample_order : List[str]
            New sample order to attempt to apply to the queue.
        """
        # Reset queue to known state.
        client.queue.put("/clear", data={})
        client.queue.post("/", data=[test_sample_1, test_sample_5, test_sample_6])

def test_get_default_mesh_params(client):
    """Test if we get the right default mesh params."""

    resp = client.get("/mxcube/api/v0.1/queue/available_tasks")
    actual = json.loads(resp.data)["mesh"]

    # some values are taken from current value/position which is random,
    # so ignore those. But make sure they keys exist
    assert_and_remove_keys_with_random_value(actual)

    def test_get_default_char_acq_params(self, client: APIClient) -> None:
        """Test if we get the right default characterisation acq params.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        actual = client.queue.get("/char_acq")

def test_get_default_xrf_parameters(client):
    """Test if we get the right default xrf params."""
    resp = client.get("/mxcube/api/v0.1/queue/available_tasks")
    actual = json.loads(resp.data)["xrf"]

    # some values are taken from current value/position which is random,
    # so ignore those. But make sure they keys exist
    assert_and_remove_keys_with_random_value(actual)

    assert resp.status_code == 200 and actual == default_xrf_parameters


def test_set_automount(client):
    """Test if we can set automount for samples."""

    def test_get_default_mesh_params(self, client: APIClient) -> None:
        """Test if we get the right default mesh params.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        actual = client.queue.get("/mesh")

        # Some values are taken from current value/position which is random, so ignore those.
        actual["acq_parameters"].pop("osc_start")
        actual["acq_parameters"].pop("energy")
        actual["acq_parameters"].pop("resolution")
        actual["acq_parameters"].pop("transmission")

        assert actual == default_mesh_params

    def test_get_default_xrf_parameters(self, client: APIClient) -> None:
        """Test if we get the right default xrf params.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        data = client.queue.get("/xrf")
        assert data["countTime"].isnumeric()
        assert int(data["countTime"]) == 5

    def test_set_automount(self, client: APIClient) -> None:
        """Test if we can set automount for samples.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        data = client.queue.post("/automount", data=True, is_json=True)
        assert data["automount"]

    def test_set_num_snapshots(self, client: APIClient) -> None:
        """Test if we can set num of snapshots for acq.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        data = client.queue.put(
            "/num_snapshots", data={"numSnapshots": 2}, is_json=True
        )
        assert data["numSnapshots"] == 2

    def test_set_group_folder(self, client: APIClient) -> None:
        """Test if we can set group folder.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        client.queue.post("/group_folder", data={"path": "tmp/"}, is_json=True)
        assert client.queue.group_folder == "tmp/"

    def test_set_autoadd(self, client: APIClient) -> None:
        """Test if we can set autoadd for samples.

        Parameters
        ----------
        client : APIClient
            Authenticated client session.
        """
        data = client.queue.post("/auto_add_diffplan", data=True, is_json=True)
        assert data["auto_add_diffplan"]
