from wrapper.api_client import APIClient


def test_get_sample_list(client: APIClient) -> None:
    """Checks retrieval of the samples list from lims.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.sample_changer.get("/samples_list")

    assert isinstance(data["sampleList"], dict)
    assert isinstance(data["sampleOrder"], list)


def test_get_sc_state(client: APIClient) -> None:
    """Checks retrieval of the sample changer state.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    assert isinstance(client.sample_changer.state, str)


def test_get_loaded_sample(client: APIClient) -> None:
    """Checks retrieval of the sample changer loaded sample.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.sample_changer.get("/loaded_sample")

    assert isinstance(data["address"], str)
    assert isinstance(data["barcode"], str)


def test_get_sc_contents_view(client: APIClient) -> None:
    """Checks retrieval of the sample changer contents.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    contents_data = client.sample_changer.get("/contents")
    capacity_data = client.sample_changer.get("/capacity")

    assert isinstance(contents_data["children"], list)
    assert (
        len(contents_data["children"]) == capacity_data["capacity"]["num_baskets"]
    )  # pucks

    num_samples = 0
    for basket in contents_data["children"]:
        num_samples += len(basket["children"])

    assert num_samples == capacity_data["capacity"]["num_samples"]  # samples


def test_get_maintenance_cmds(client: APIClient) -> None:
    """Checks retrieval of the sample changer manteniance commands.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.sample_changer.get("/get_maintenance_cmds")

    assert isinstance(data["cmds"], list)


def test_get_global_state(client: APIClient) -> None:
    """Checks retrieval of the sample changer global state.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.sample_changer.get("/get_global_state")

    assert isinstance(data["commands_state"], dict)
    assert isinstance(data["message"], str)
    assert isinstance(data["state"], dict)


def test_get_initial_state(client: APIClient) -> None:
    """Checks retrieval of the sample changer initial state.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.sample_changer.get("/get_initial_state")

    assert isinstance(data["cmds"], dict)
    assert isinstance(data["cmds"]["cmds"], list)
    assert isinstance(data["contents"], dict)
    assert isinstance(data["global_state"], dict)
    assert isinstance(data["loaded_sample"], dict)
    assert isinstance(data["msg"], str)
    assert isinstance(data["state"], str)
