# -*- coding: utf-8 -*-
import json
import logging
import math
import re
import sys
from http import HTTPStatus
from urllib.parse import urljoin
from time import sleep


import httpx
from flask_login import current_user
from mxcubecore import HardwareRepository as HWR
from mxcubecore.configuration.ansto.config import settings
from mxcubecore.HardwareObjects.ANSTO.redis_utils import get_redis_connection
from mxcubecore.model import queue_model_objects as qmo
from mxcubecore.model.lims_session import LimsSessionManager

from mxcubeweb.core.components.component_base import ComponentBase
from mxcubeweb.core.util import fsutils

VALID_SAMPLE_NAME_REGEXP = re.compile("^[a-zA-Z0-9:+_-]+$")


class Lims(ComponentBase):
    def __init__(self, app, config):
        super().__init__(app, config)

    def new_sample_list(self):
        return {"sampleList": {}, "sampleOrder": []}

    def init_sample_list(self):
        self.sample_list_set(self.new_sample_list())

    def sample_list_set(self, sample_list):
        self.app.SAMPLE_LIST = sample_list

    def sample_list_set_order(self, sample_order):
        self.app.SAMPLE_LIST["sampleOrder"] = sample_order

    def sample_list_get(self, loc=None, current_queue=None):
        self.synch_sample_list_with_queue(current_queue)
        res = self.app.SAMPLE_LIST

        if loc:
            res = self.app.SAMPLE_LIST.get("sampleList").get(loc, {})

        return res

    def sample_list_sync_sample(self, lims_sample):
        lims_code = lims_sample.get("code", None)
        lims_location = lims_sample.get("lims_location")
        sample_to_update = None

        # LIMS sample has code, check if the code was read by SC
        if lims_code and self.app.sample_changer.sc_contents_from_code_get(lims_code):
            sample_to_update = self.app.sample_changer.sc_contents_from_code_get(
                lims_code
            )
        elif lims_location:
            # Asume that the samples have been put in the right place of the SC
            sample_to_update = self.app.sample_changer.sc_contents_from_location_get(
                lims_location
            )

        if sample_to_update:
            loc = sample_to_update["sampleID"]
            self.sample_list_update_sample(loc, lims_sample)

    def synch_sample_list_with_queue(self, current_queue=None):
        if not current_queue:
            current_queue = self.app.queue.queue_to_dict(include_lims_data=True)

        current_queue.get("sample_order", [])

        for loc, data in self.app.SAMPLE_LIST["sampleList"].items():
            if loc in current_queue:
                sample = current_queue[loc]

                # Don't synchronize, lims attributes from queue sample, if
                # they are already set by sc or lims
                if data.get("sampleName", ""):
                    sample.pop("sampleName")

                if data.get("proteinAcronym", ""):
                    sample.pop("proteinAcronym")

                # defaultSubDir and prefix are derived from proteinAcronym
                # and/or sampleName so make sure that those are removed from
                # queue sample so that they can be updated if changed.
                if data.get("proteinAcronym", "") or data.get("sampleName", ""):
                    sample.pop("defaultPrefix")
                    sample.pop("defaultSubDir")

                # Make sure that sample in queue is updated with lims information
                model, entry = self.app.queue.get_entry(sample["queueID"])
                model.set_from_dict(data)

                # Update sample location, location is Manual for free pin mode
                # in MXCuBE Web
                model.loc_str = data.get("sampleID", -1)
                model.free_pin_mode = data.get("location", "") == "Manual"

                self.sample_list_update_sample(loc, sample)

    def sample_list_update_sample(self, loc, sample):
        _sample = self.app.SAMPLE_LIST["sampleList"].get(loc, {})

        # If sample exists in sample list update it, otherwise add it
        if _sample:
            _sample.update(sample)
        else:
            self.app.SAMPLE_LIST["sampleList"][loc] = sample
            self.app.SAMPLE_LIST["sampleOrder"].append(loc)

        return self.app.SAMPLE_LIST["sampleList"].get(loc, {})

    def apply_template(self, params, sample_model, path_template):
        # Apply subdir template if used:
        if "{" in params.get("subdir", ""):
            if sample_model.crystals[0].protein_acronym:
                params["subdir"] = params["subdir"].format(
                    NAME=sample_model.get_name(),
                    ACRONYM=sample_model.crystals[0].protein_acronym,
                )
            else:
                stripped = params["subdir"][0 : params["subdir"].find("{")]
                params["subdir"] = stripped + sample_model.get_name()

            # The template was only applied partially if subdir ends with '-'
            # probably because either acronym or protein name is null in LIMS
            if params["subdir"].endswith("-"):
                params["subdir"] = sample_model.get_name()

        # Making sure that there are no ":" left from the sample name incase
        # no synchronisation with LIMS was done
        params["subdir"] = params["subdir"].replace(":", "-")

        if "{" in params.get("prefix", ""):
            sample = self.app.SAMPLE_LIST["sampleList"].get(sample_model.loc_str, {})
            prefix = self.get_default_prefix(sample)
            shape = params["shape"] if params["shape"] > 0 else ""
            params["prefix"] = params["prefix"].format(PREFIX=prefix, POSITION=shape)

            if params["prefix"].endswith("_"):
                params["prefix"] = params["prefix"][:-1]

        # mxcube web passes entire prefix as prefix, including reference, mad and wedge
        # prefix. So we strip those before setting the actual base_prefix.
        params["prefix"] = self.strip_prefix(path_template, params["prefix"])

    def strip_prefix(self, pt, prefix):
        """
        Strips the reference, wedge and mad prefix from a given prefix. For example
        removes ref- from the beginning and _w[n] and -pk, -ip, -ipp from the end.

        :param PathTemplate pt: path template used to create the prefix
        :param str prefix: prefix from the client
        :returns: stripped prefix
        """
        if (
            pt.reference_image_prefix
            and pt.reference_image_prefix == prefix[0 : len(pt.reference_image_prefix)]
        ):
            prefix = prefix[len(pt.reference_image_prefix) + 1 :]

        if pt.wedge_prefix and pt.wedge_prefix == prefix[-len(pt.wedge_prefix) :]:
            prefix = prefix[: -(len(pt.wedge_prefix) + 1)]

        if pt.mad_prefix and pt.mad_prefix == prefix[-len(pt.mad_prefix) :]:
            prefix = prefix[: -(len(pt.mad_prefix) + 1)]

        return prefix

    def get_session_manager(self) -> LimsSessionManager:
        return LimsSessionManager.parse_obj(json.loads(current_user.limsdata))

    def is_rescheduled_session(self, session):
        """
        Returns true is the session is rescheduled. That means that either currently is not the expected timeslot
        or because it is not in the expected beamline
        """
        return not (session.is_scheduled_beamline and session.is_scheduled_time)

    def allow_session(self, session):
        HWR.beamline.lims.allow_session(session)

    def select_session(self, session_id: str) -> bool:
        """
        param session_id : this is a identifier that could be proposal name or session_id depending of the type of LIMS login type
        """
        logging.getLogger("MX3.HWR").debug("select_session session_id=%s" % session_id)
        session = None

        # Selecting the active session in the LIMS object
        try:
            HWR.beamline.lims.set_active_session_by_id(session_id)
            session = HWR.beamline.lims.set_active_session_by_id(session_id)
            if session is None:
                raise "No session selected on LIMS"
        except BaseException as e:
            import traceback

            traceback.print_exc(file=sys.stdout)
            logging.getLogger("MX3.HWR").info(
                "No session candidate. Force signout. e=%s" % str(e)
            )
            self.app.usermanager.signout()
            return False

        if HWR.beamline.lims.is_user_login_type() and "Commissioning" in session.title:
            if hasattr(HWR.beamline.session, "set_in_commissioning"):
                HWR.beamline.session.set_in_commissioning(self.get_proposal_info())
                logging.getLogger("MX3.HWR").info(
                    "[LIMS] Commissioning proposal flag set."
                )

        HWR.beamline.session.proposal_code = session.code
        HWR.beamline.session.proposal_number = session.number
        HWR.beamline.session.session_id = HWR.beamline.lims.get_session_id()
        HWR.beamline.session.proposal_id = session.proposal_id
        HWR.beamline.session.set_session_start_date(session.start_date)

        logging.getLogger("MX3.HWR").info(
            "[LIMS] Selected session. proposal=%s session_id=%s.",
            session.proposal_name,
            session.session_id,
        )

        if self.is_rescheduled_session(session):
            logging.getLogger("MX3.HWR").info(
                "[LIMS] Session is rescheduled in time or beamline."
            )
            self.allow_session(session)

        if hasattr(HWR.beamline.session, "prepare_directories"):
            try:
                logging.getLogger("MX3.HWR").info(
                    "[LIMS] Creating data directories for proposal %s%s" % session.code,
                    session.number,
                )
                raise "To be implemented for those using prepare_directories"
                # HWR.beamline.session.prepare_directories(proposal_tuple)
            except Exception:
                logging.getLogger("MX3.HWR").info(
                    "[LIMS] Error creating data directories, %s" % sys.exc_info()[1]
                )

        # save selected proposal in users db

        current_user.selected_proposal = session.session_id
        self.app.usermanager.update_user(current_user)

        logging.getLogger("user_log").info(
            "[LIMS] Proposal selected session_id=%s.", session_id
        )

        return True

    def get_default_prefix(self, sample_data, generic_name=False):
        if isinstance(sample_data, dict):
            sample = qmo.Sample()
            sample.code = sample_data.get("code", "")
            sample.name = sample_data.get("sampleName", "").replace(":", "-")
            sample.location = sample_data.get("location", "").split(":")
            sample.lims_id = sample_data.get("limsID", -1)
            sample.crystals[0].protein_acronym = sample_data.get("proteinAcronym", "")
        else:
            sample = sample_data

        return HWR.beamline.session.get_default_prefix(sample, generic_name)

    def get_default_subdir(self, sample_data):
        return HWR.beamline.session.get_default_subdir(sample_data)

    def synch_with_lims(self, lims_name):
        # session_id is not used, so we can pass None as second argument to
        # 'db_connection.get_samples'

        # Try 3 times in case the robot client connection fails
        for _ in range(3):
            samples_info_list = HWR.beamline.sample_changer.refresh_puck_info()
            if not samples_info_list:
                logging.getLogger("MX3.HWR").info(
                    "[LIMS] No sample info retrieved from LIMS, retrying..."
                )
                sleep(0.5)
                continue
            
            break

        _sample_list ={}
        _sample_order = []
        for sample_info in samples_info_list:
            sample_location = sample_info.get("sampleLocation")
            puck_location = sample_info.get("containerSampleChangerLocation")
            if sample_location is None or puck_location is None:
                continue

            try:
                port_int = int(sample_location)
            except (TypeError, ValueError):
                continue

            # The UI filters samples by (cell_no, puck_no) and expects these to
            # match the SC contents tree (cell=1 for single-cell changers).
            cell_no = 1
            puck_no = 1
            container_loc_key = str(puck_location)
            try:
                basket = int(puck_location)
            except (TypeError, ValueError):
                basket = None
            else:
                if HWR.beamline.sample_changer.__class__.__TYPE__ in [
                    "Flex Sample Changer",
                    "FlexHCD",
                    "RoboDiff",
                ]:
                    cell_no = int(math.ceil((basket) / 3.0))
                    puck_no = basket - 3 * (cell_no - 1)
                    container_loc_key = f"{cell_no}:{puck_no}"
                else:
                    puck_no = basket

            sample_list_key = f"{container_loc_key}:{port_int:02d}"
            sample_name = sample_info.get("sampleName") or ""
            _sample_list[sample_list_key] = {
                'sampleID': sample_list_key, 
                'location': sample_list_key, 
                'sampleName': sample_name, 
                'crystalUUID': sample_list_key, 'proteinAcronym': '', 
                'code': sample_list_key,
                'limsID': sample_info.get('sampleId'),
                'loadable': True, 
                'state': 0, 
                'tasks': [], 
                'type': 'Sample', 
                'cell_no': cell_no,
                'puck_no': puck_no,
                'defaultPrefix': sample_name, 
                'defaultSubDir': sample_name + '/'}

            _sample_order.append(sample_list_key)


        self.app.SAMPLE_LIST = {"sampleList": _sample_list, "sampleOrder": _sample_order}

        for sample_info in samples_info_list:
            sample_info["limsID"] = sample_info.pop("sampleId", None)
            sample_info["defaultPrefix"] = self.get_default_prefix(sample_info)
            sample_info["defaultSubDir"] = self.get_default_subdir(sample_info)

            sample_name = sample_info.get("sampleName")
            if not isinstance(sample_name, str) or not sample_name:
                continue

            if not VALID_SAMPLE_NAME_REGEXP.match(sample_name):
                raise AttributeError(
                    "sample name for sample %s contains an incorrect character"
                    % sample_info
                )

            try:
                basket = int(sample_info["containerSampleChangerLocation"])
            except (TypeError, ValueError, KeyError):
                continue
            else:
                if HWR.beamline.sample_changer.__class__.__TYPE__ in [
                    "Flex Sample Changer",
                    "FlexHCD",
                    "RoboDiff",
                ]:
                    cell = int(math.ceil((basket) / 3.0))
                    puck = basket - 3 * (cell - 1)
                    sample_info["containerSampleChangerLocation"] = "%d:%d" % (
                        cell,
                        puck,
                    )

            try:
                lims_location = sample_info[
                    "containerSampleChangerLocation"
                ] + ":%02d" % int(sample_info["sampleLocation"])
            except Exception:
                logging.getLogger("MX3.HWR").info(
                    "[LIMS] Could not parse sample loaction from"
                    " LIMS, (perhaps not set ?)"
                )
            else:
                sample_info["lims_location"] = lims_location

                self.sample_list_sync_sample(sample_info)

        return self.sample_list_get()

    def _get_epn_string(self) -> str:
        """
        [ANSTO] Gets the EPN string from Redis

        Returns
        -------
        str
            The EPN string

        Raises
        ------
        QueueExecutionException
            An exception if the EPN string is not set in Redis
        """
        with get_redis_connection() as redis_connection:
            epn_string: str | None = redis_connection.get("epn")
            if epn_string is None:
                raise ValueError("EPN string is not set in Redis")
            return epn_string

    def _get_visit_id_for_epn(self, client: httpx.Client, epn: str) -> int | None:
        """
        [ANSTO] Gets the visit id for a given EPN string

        Parameters
        ----------
        client : httpx.Client
            The HTTP client to use for the request
        epn : str
            The EPN string to filter by

        Returns
        -------
        int | None
            The visit ID if found, None otherwise
        """
        r = client.get(
            urljoin(
                settings.DATA_LAYER_API, f"visits?filter_by_identifier_startswith={epn}"
            )
        )
        if r.status_code != HTTPStatus.OK:
            logging.getLogger("user_level_log").warning(
                f"Failed to get visit info from the data layer API: {r.text}"
            )
            return None
        data = r.json()
        if len(data) == 0:
            logging.getLogger("user_level_log").error(
                f"No visit found starting with identifier {epn}"
            )
            return None
        if len(data) > 1:
            logging.getLogger("user_level_log").error(
                f"Multiple visits ({len(data)}) found with identifier {epn}"
            )
            return None
        return data[0]["id"]

    def _get_lab_ids_for_visit(self, client: httpx.Client, visit_id: int) -> list[int]:
        """
        [ANSTO] Gets the lab IDs associated with a visit

        Parameters
        ----------
        client : httpx.Client
            The HTTP client
        visit_id : int
            The visit id

        Returns
        -------
        list[int]
            The list of lab IDs associated with the visit
        """
        r = client.get(urljoin(settings.DATA_LAYER_API, f"visits/{visit_id}/labs"))
        if r.status_code != HTTPStatus.OK:
            logging.getLogger("user_level_log").warning(
                f"Failed to get lab info from the data layer API: {r.text}"
            )
            return []
        try:
            return [lab["id"] for lab in r.json()]
        except Exception:
            logging.getLogger("user_level_log").warning(
                f"Unexpected labs payload for visit {visit_id}: {r.text}"
            )
            return []

    def _get_lab_name(self, client: httpx.Client, lab_id: int) -> str | None:
        """
        [ANSTO] Gets the lab name for a given lab ID

        Parameters
        ----------
        client : httpx.Client
            The HTTP client
        lab_id : int
            The lab id

        Returns
        -------
        str | None
            The lab name if found, None otherwise
        """
        r = client.get(urljoin(settings.DATA_LAYER_API, f"labs/{lab_id}"))
        if r.status_code != HTTPStatus.OK:
            logging.getLogger("user_level_log").warning(
                f"Failed to get lab info from the data layer API: {r.text}"
            )
            return None
        return r.json().get("name")

    def _get_active_projects_for_lab(
        self, client: httpx.Client, lab_id: int
    ) -> list[tuple[str, int]]:
        """
        [ANSTO] Gets the active projects for a given lab id

        Parameters
        ----------
        client : httpx.Client
            The HTTP client
        lab_id : int
            The lab id

        Returns
        -------
        list[tuple[str, int]]
            A list of tuples containing the project name and ID
        """

        r = client.get(
            urljoin(
                settings.DATA_LAYER_API,
                f"projects?only_active=true&filter_by_lab={lab_id}",
            )
        )
        if r.status_code != HTTPStatus.OK:
            logging.getLogger("user_level_log").warning(
                f"Failed to get project names from the data layer API: {r.text}"
            )
            return []
        try:
            data = r.json()
            return [(item["name"], item["id"]) for item in data]
        except Exception:
            logging.getLogger("user_level_log").warning(
                f"Unexpected projects payload for lab {lab_id}: {r.text}"
            )
            return []

    def _get_project_paths(
        self, client: httpx.Client, project_id: int
    ) -> list[tuple[str, int]]:
        """
        [ANSTO] Gets the project paths for a given project ID, including sub-project

        Parameters
        ----------
        client : httpx.Client
            The HTTP client
        project_id : int
            The project id

        Returns
        -------
        list[tuple[str, int]]
            A list of tuples containing the project path and ID
        """

        def build_paths(node: dict, prefix: str | None = None) -> list[tuple[str, int]]:
            name = node.get("name", "")
            pid = node.get("id")
            if not name or pid is None:
                return []
            path = f"{prefix}/{name}" if prefix else name
            paths: list[tuple[str, int]] = [(path, pid)]
            for child in node.get("children", []) or []:
                paths.extend(build_paths(child, path))
            return paths

        r = client.get(
            urljoin(
                settings.DATA_LAYER_API,
                f"projects/{project_id}?include_children=true&include_parents=false",
            )
        )
        if r.status_code != HTTPStatus.OK:
            return []
        try:
            return build_paths(r.json())
        except Exception as e:
            logging.getLogger("HWR").warning(
                f"Failed to build path for project id {project_id}: {e}"
            )
            return []

    def get_labs_with_projects(self) -> list[dict[str, object]]:
        """
        [ANSTO] Build project paths per lab including sub-projects.

        Returns
        -------
        list[dict[str, object]]
                Example: [
                    {"id": "Lab A", "name": "Lab A", "projects": [{"id": 1, "name": "Parent/Child"}]} , ...
                ]
        """
        epn = self._get_epn_string()
        result: list[dict[str, object]] = []
        # Cache also as mapping of lab_name -> list[(path, id)] if needed elsewhere
        self.project_id_lab_name_map: dict[str, list[tuple[str, int]]] = {}

        with httpx.Client() as client:
            visit_id = self._get_visit_id_for_epn(client, epn)
            if visit_id is None:
                return []

            lab_ids = self._get_lab_ids_for_visit(client, visit_id)
            for lab_id in lab_ids:
                lab_name = self._get_lab_name(client, lab_id)
                if not lab_name:
                    continue

                self.project_id_lab_name_map[lab_name] = []
                top_level = self._get_active_projects_for_lab(client, lab_id)
                for _, project_id in top_level:
                    paths = self._get_project_paths(client, project_id)
                    if paths:
                        self.project_id_lab_name_map[lab_name].extend(paths)

                if not self.project_id_lab_name_map[lab_name] and top_level:
                    self.project_id_lab_name_map[lab_name] = top_level

                # Convert to endpoint payload for this lab
                projects_payload = [
                    {"id": pid, "name": pname}
                    for (pname, pid) in self.project_id_lab_name_map[lab_name]
                ]
                result.append(
                    {"id": lab_name, "name": lab_name, "projects": projects_payload}
                )

        return result

    def add_hand_mounted_sample(self, project_id: int, sample_name: str) -> int:
        """
        [ANSTO] Adds a hand-mounted sample to the database.

        Args:
            sample_dict: A dictionary with the properties for the entry.
        """
        epn = self._get_epn_string()

        with httpx.Client() as client:
            visit_response = client.get(
                urljoin(
                    settings.DATA_LAYER_API,
                    f"visits?filter_by_identifier_startswith={epn}",
                )
            )
            if visit_response.status_code != HTTPStatus.OK:
                logging.getLogger("user_level_log").warning(
                    "Failed to get visit info from the data layer API:"
                    f" {visit_response.text}"
                )
                raise ValueError("Failed to get visit info from the LIMS")

            visit_response_json = visit_response.json()
            if len(visit_response_json) == 0:
                logging.getLogger("user_level_log").error(
                    f"No visit found starting with identifier {epn}"
                )
                raise ValueError("No visit found in the LIMS")
            elif len(visit_response_json) > 1:
                logging.getLogger("user_level_log").error(
                    f"Multiple visits ({len(visit_response_json)}) found with"
                    f" identifier {epn}"
                )
                raise ValueError("Multiple visits found in the LIMS")
            visit_id = visit_response_json[0]["id"]

            sample_dict = {
                "name": sample_name,
                "description": "Best sample in the world",
                "notes": "We like chocolate",
                "type": "sample_handmount",
                "project_id": project_id,
                "visit_id": visit_id,
            }

            response = client.post(
                urljoin(settings.DATA_LAYER_API, "samples/handmount"),
                json=sample_dict,
            )
            if response.status_code != HTTPStatus.CREATED:
                logging.getLogger("user_level_log").error(
                    "Failed to add hand-mounted sample to the data layer API:"
                    f" {response.text}"
                )
                try:
                    msg = response.json().get("detail", "")
                except Exception:
                    msg = response.text
                raise ValueError(msg)
            return response.json()["id"]
