import requests
from typing import Any, Dict, List, Optional, Union

import challonge.models as models


class Challonge:
    """
    A Python client for the Challonge API (v2.1), covering all endpoints from the
    provided Swagger specification. Supports:
      - v1 authentication with an API key
      - v2 authentication with an OAuth2 token
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        oauth_token: Optional[str] = None,
        authorization_type: str = "v1",
        base_url: str = "https://api.challonge.com/v2.1"
    ):
        """
        :param api_key: Your Challonge API key (for v1 auth).
        :param oauth_token: OAuth2 token (for v2 auth).
        :param authorization_type: 'v1' for API key, 'v2' for OAuth2 token.
        :param base_url: Base URL for the Challonge v2.1 API.
        """
        self.session = requests.Session()
        self.base_url = base_url

        # Required headers as per the Swagger spec
        self.session.headers.update({
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/json",
            "Authorization-Type": authorization_type,
            # Provide a custom User-Agent if needed:
            "User-Agent": "ChallongePythonClient/1.0",
        })

        # Set Authorization header according to v1 or v2
        if authorization_type == "v1" and api_key:
            self.session.headers.update({"Authorization": api_key})
        elif authorization_type == "v2" and oauth_token:
            self.session.headers.update({"Authorization": f"Bearer {oauth_token}"})
        else:
            raise ValueError(
                "Must provide a valid api_key (for v1) or oauth_token (for v2) "
                "that matches the chosen authorization_type."
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Internal helper to make the HTTP request to the Challonge API.

        :param method: 'GET', 'POST', 'PUT', or 'DELETE'
        :param endpoint: The endpoint path, e.g. '/tournaments.json'
        :param params: Query parameters for GET or DELETE
        :param json_data: JSON body for POST or PUT
        :return: Parsed JSON response (as a dict/list) or None for 204/no content
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data
        )

        # Raise an HTTPError if we got an unsuccessful status code
        response.raise_for_status()

        # Some DELETE requests (204) or empty bodies return no content
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    # -------------------------------------------------------------------------
    # Tournaments
    # -------------------------------------------------------------------------
    def find_tournaments(
        self,
        page: int = 1,
        per_page: int = 25,
        state: Optional[str] = None,
        tournament_type: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None
    ) -> List[models.TournamentModel]:
        """
        GET /tournaments.json
        Returns tournaments based on the given filter parameters.
        The Swagger suggests an array of "TournamentModel" as the top-level response.
        """
        endpoint = "/tournaments.json"
        params = {
            "page": str(page),
            "per_page": str(per_page),
        }
        if state:
            params["state"] = state
        if tournament_type:
            params["type"] = tournament_type
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before

        resp = self._request("GET", endpoint, params=params)
        # According to the Swagger, the top-level might be an array of tournaments:
        # [
        #   {
        #     "id": "...",
        #     "type": "tournament",
        #     "attributes": { ... }
        #   },
        #   ...
        # ]
        if not resp:
            return []
        return [models.TournamentModel.parse_obj(item) for item in resp["data"]]

    def create_tournament(self, tournament_attributes: Dict[str, Any]) -> models.TournamentModel:
        """
        POST /tournaments.json
        Creates a tournament. Returns a single TournamentModel in "data".
        """
        endpoint = "/tournaments.json"
        payload = {
            "data": {
                "type": "Tournaments",
                "attributes": tournament_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        # According to the Swagger, the response might look like:
        # {
        #   "data": {
        #     "id": "...", 
        #     "type": "tournament", 
        #     "attributes": { ... }
        #   }
        # }
        return models.TournamentModel.parse_obj(resp["data"])

    def show_tournament(self, tournament_id: str) -> models.TournamentModel:
        """
        GET /tournaments/{tournament_id}.json
        Gets a tournament by ID or URL. Returns a single TournamentModel in "data".
        """
        endpoint = f"/tournaments/{tournament_id}.json"
        resp = self._request("GET", endpoint)
        return models.TournamentModel.parse_obj(resp["data"])

    def update_tournament(self, tournament_id: str, tournament_attributes: Dict[str, Any]) -> models.TournamentModel:
        """
        PUT /tournaments/{tournament_id}.json
        Updates a tournament. Returns updated TournamentModel in "data".
        """
        endpoint = f"/tournaments/{tournament_id}.json"
        payload = {
            "data": {
                "type": "Tournaments",
                "attributes": tournament_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.TournamentModel.parse_obj(resp["data"])

    def delete_tournament(self, tournament_id: str) -> None:
        """
        DELETE /tournaments/{tournament_id}.json
        Deletes a tournament. Usually returns 204 No Content.
        """
        endpoint = f"/tournaments/{tournament_id}.json"
        self._request("DELETE", endpoint)
        # No return (None)

    def change_state_tournament(self, tournament_id: str, new_state: str) -> models.TournamentModel:
        """
        PUT /tournaments/{tournament_id}/change_state.json
        Changes a tournament's state (e.g., "process_checkin", "start", "finalize", etc.).
        Returns an updated TournamentModel in "data".
        """
        endpoint = f"/tournaments/{tournament_id}/change_state.json"
        payload = {
            "data": {
                "type": "TournamentState",
                "attributes": {
                    "state": new_state
                }
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.TournamentModel.parse_obj(resp["data"])

    # -------------------------------------------------------------------------
    # Matches
    # -------------------------------------------------------------------------
    def find_matches(
        self,
        tournament_id: str,
        page: int = 1,
        per_page: int = 25,
        state: Optional[str] = None,
        participant_id: Optional[str] = None
    ) -> List[models.MatchModel]:
        """
        GET /tournaments/{tournament_id}/matches.json
        Returns an array of matches (MatchModel) for a given tournament, with optional filters.
        Swagger: "schema": { "type": "array", "items": { "$ref": "#/definitions/MatchModel" } }
        """
        endpoint = f"/tournaments/{tournament_id}/matches.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        if state:
            params["state"] = state
        if participant_id:
            params["participant_id"] = participant_id

        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.MatchModel.parse_obj(item) for item in resp["data"]]

    def show_match(self, tournament_id: str, match_id: str) -> models.MatchModel:
        """
        GET /tournaments/{tournament_id}/matches/{match_id}.json
        Returns a single MatchModel.
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}.json"
        resp = self._request("GET", endpoint)
        return models.MatchModel.parse_obj(resp)

    def update_match(self, tournament_id: str, match_id: str, match_attributes: Dict[str, Any]) -> models.MatchModel:
        """
        PUT /tournaments/{tournament_id}/matches/{match_id}.json
        Updates a match (e.g. records scores). Returns an updated MatchModel.
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}.json"
        payload = {
            "data": {
                "type": "Match",
                "attributes": match_attributes,
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.MatchModel.parse_obj(resp)

    def change_state_match(self, tournament_id: str, match_id: str, new_state: str) -> models.MatchModel:
        """
        PUT /tournaments/{tournament_id}/matches/{match_id}/change_state.json
        Changes a match's state (e.g., "reopen", "mark_as_underway", "unmark_as_underway").
        Returns an updated MatchModel.
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}/change_state.json"
        payload = {
            "data": {
                "type": "MatchState",
                "attributes": {
                    "state": new_state
                }
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.MatchModel.parse_obj(resp)

    # -------------------------------------------------------------------------
    # Participants
    # -------------------------------------------------------------------------
    def find_participants(
        self,
        tournament_id: str,
        page: int = 1,
        per_page: int = 25
    ) -> List[models.ParticipantModel]:
        """
        GET /tournaments/{tournament_id}/participants.json
        Returns participants (ParticipantModel) for a given tournament.
        Swagger: "schema": { "type": "array", "items": { "$ref": "#/definitions/ParticipantModel" } }
        """
        endpoint = f"/tournaments/{tournament_id}/participants.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    def create_participant(self, tournament_id: str, participant_attributes: Dict[str, Any]) -> models.ParticipantModel:
        """
        POST /tournaments/{tournament_id}/participants.json
        Creates a single participant. Returns ParticipantModel.
        Swagger might have: { "data": { "id": "...", "type": "participant", ... } }
        Or an array of participants. We'll assume a single object.
        """
        endpoint = f"/tournaments/{tournament_id}/participants.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": participant_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        # Some endpoints might return a single object or an array. 
        # The swagger for "participants" says 200 => array. But for a single participant,
        # let's assume we get a single object. 
        # If it actually returns an array of 1 item, adapt as needed:
        if isinstance(resp, dict) and "data" in resp:
            # single object shape
            return models.ParticipantModel.parse_obj(resp["data"])
        elif isinstance(resp, list):
            # Possibly an array with one item
            if resp:
                return models.ParticipantModel.parse_obj(resp[0])
        raise ValueError("Unexpected response format for create_participant.")

    def show_participant(self, tournament_id: str, participant_id: str) -> models.ParticipantModel:
        """
        GET /tournaments/{tournament_id}/participants/{participant_id}.json
        Gets a participant by ID. Returns ParticipantModel.
        """
        endpoint = f"/tournaments/{tournament_id}/participants/{participant_id}.json"
        resp = self._request("GET", endpoint)
        return models.ParticipantModel.parse_obj(resp["data"])

    def update_participant(
        self,
        tournament_id: str,
        participant_id: str,
        participant_attributes: Dict[str, Any]
    ) -> models.ParticipantModel:
        """
        PUT /tournaments/{tournament_id}/participants/{participant_id}.json
        Updates a participant. Returns updated ParticipantModel.
        """
        endpoint = f"/tournaments/{tournament_id}/participants/{participant_id}.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": participant_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.ParticipantModel.parse_obj(resp["data"])

    def delete_participant(self, tournament_id: str, participant_id: str) -> None:
        """
        DELETE /tournaments/{tournament_id}/participants/{participant_id}.json
        Deletes (or deactivates) a participant. Usually returns 204 No Content.
        """
        endpoint = f"/tournaments/{tournament_id}/participants/{participant_id}.json"
        self._request("DELETE", endpoint)

    def bulk_create_participants(
        self, 
        tournament_id: str, 
        participants: List[Dict[str, Any]]
    ) -> List[models.ParticipantModel]:
        """
        POST /tournaments/{tournament_id}/participants/bulk_add.json
        Bulk creates participants (up to 20 at a time).
        Returns an array of newly-created ParticipantModel objects.
        """
        endpoint = f"/tournaments/{tournament_id}/participants/bulk_add.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": {
                    "participants": participants
                }
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        if not resp:
            return []
        # If the API returns an array of participants, each shaped like ParticipantModel:
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    def clear_all_participants(self, tournament_id: str) -> None:
        """
        DELETE /tournaments/{tournament_id}/participants/clear.json
        Clears all participants from a tournament (204 No Content).
        """
        endpoint = f"/tournaments/{tournament_id}/participants/clear.json"
        self._request("DELETE", endpoint)

    def randomize_participants(self, tournament_id: str) -> List[models.ParticipantModel]:
        """
        PUT /tournaments/{tournament_id}/participants/randomize.json
        Randomizes participant seeding for a tournament. 
        Typically returns an array of ParticipantModel with new seeds.
        """
        endpoint = f"/tournaments/{tournament_id}/participants/randomize.json"
        resp = self._request("PUT", endpoint)
        if not resp:
            return []
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    # -------------------------------------------------------------------------
    # Match Attachments
    # -------------------------------------------------------------------------
    def find_match_attachments(
        self,
        tournament_id: str,
        match_id: str,
        page: int = 1,
        per_page: int = 25
    ) -> List[models.MatchAttachmentModel]:
        """
        GET /tournaments/{tournament_id}/matches/{match_id}/attachments.json
        Returns attachments for a match (array of MatchAttachmentModel).
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}/attachments.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.MatchAttachmentModel.parse_obj(item) for item in resp["data"]]

    def create_match_attachment(
        self,
        tournament_id: str,
        match_id: str,
        attachment_attributes: Dict[str, Any]
    ) -> models.MatchAttachmentModel:
        """
        POST /tournaments/{tournament_id}/matches/{match_id}/attachments.json
        Creates a match attachment and returns a single MatchAttachmentModel.
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}/attachments.json"
        payload = {
            "data": {
                "type": "match_attachment",
                "attributes": attachment_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        return models.MatchAttachmentModel.parse_obj(resp)

    def delete_match_attachment(
        self,
        tournament_id: str,
        match_id: str,
        attachment_id: str
    ) -> None:
        """
        DELETE /tournaments/{tournament_id}/matches/{match_id}/attachments/{attachment_id}.json
        Deletes a match attachment (204 No Content).
        """
        endpoint = f"/tournaments/{tournament_id}/matches/{match_id}/attachments/{attachment_id}.json"
        self._request("DELETE", endpoint)

    # -------------------------------------------------------------------------
    # Races
    # -------------------------------------------------------------------------
    def find_races(self, page: int = 1, per_page: int = 25) -> List[models.RaceModel]:
        """
        GET /races.json
        Returns a list of races. The Swagger indicates the top-level shape:
        {
          "data": [
            { "id": "...", "type": "Race", "attributes": {...} },
            ...
          ]
        }
        We'll parse "data" into RaceModel. 
        """
        endpoint = "/races.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        # According to the swagger, might be { "data": [ ... ] }
        if "data" in resp and isinstance(resp["data"], list):
            return [models.RaceModel.parse_obj(item) for item in resp["data"]]
        return []

    def create_race(self, race_attributes: Dict[str, Any]) -> models.RaceModel:
        """
        POST /races.json
        Creates a new Race. 
        Swagger indicates the response might be:
        {
          "data": { "id": "...", "type": "Race", "attributes": {...} }
        }
        """
        endpoint = "/races.json"
        payload = {
            "data": {
                "type": "Race",
                "attributes": race_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        return models.RaceModel.parse_obj(resp["data"])

    def show_race(self, race_id: str) -> models.RaceModel:
        """
        GET /races/{race_id}.json
        Returns a single RaceModel in { "data": { ... } } shape.
        """
        endpoint = f"/races/{race_id}.json"
        resp = self._request("GET", endpoint)
        return models.RaceModel.parse_obj(resp["data"])

    def update_race(self, race_id: str, race_attributes: Dict[str, Any]) -> models.RaceModel:
        """
        PUT /races/{race_id}.json
        Updates a Race. Returns updated RaceModel in "data".
        """
        endpoint = f"/races/{race_id}.json"
        payload = {
            "data": {
                "type": "Race",
                "attributes": race_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.RaceModel.parse_obj(resp["data"])

    def delete_race(self, race_id: str) -> None:
        """
        DELETE /races/{race_id}.json
        Deletes a Race (204 No Content).
        """
        endpoint = f"/races/{race_id}.json"
        self._request("DELETE", endpoint)

    def change_state_race(self, race_id: str, new_state: str) -> models.RaceModel:
        """
        PUT /races/{race_id}/change_state.json
        Changes a Race's state. Returns updated RaceModel.
        """
        endpoint = f"/races/{race_id}/change_state.json"
        payload = {
            "data": {
                "type": "RaceState",
                "attributes": {
                    "state": new_state
                }
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.RaceModel.parse_obj(resp["data"])

    # -------------------------------------------------------------------------
    # Rounds (within Races)
    # -------------------------------------------------------------------------
    def find_rounds(self, race_id: str, page: int = 1, per_page: int = 25) -> List[models.RoundModel]:
        """
        GET /races/{race_id}/rounds.json
        Returns all rounds for a given Race. Possibly in the shape:
        {
          "data": [
            { "id": "...", "type": "RoundOutput", "attributes": {...} },
            ...
          ]
        }
        """
        endpoint = f"/races/{race_id}/rounds.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        if "data" in resp and isinstance(resp["data"], list):
            return [models.RoundModel.parse_obj(item) for item in resp["data"]]
        return []

    def show_round(self, race_id: str, round_id: str) -> models.RoundModel:
        """
        GET /races/{race_id}/rounds/{round_id}.json
        Returns a single RoundModel in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}.json"
        resp = self._request("GET", endpoint)
        return models.RoundModel.parse_obj(resp["data"])

    def update_round(self, race_id: str, round_id: str, round_state: Dict[str, Any]) -> models.RoundModel:
        """
        PUT /races/{race_id}/rounds/{round_id}.json
        Updates a Round's state. Returns updated RoundModel in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}.json"
        payload = {
            "data": {
                "type": "RoundStateInput",  # or just "Round" if your backend is flexible
                "attributes": round_state
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.RoundModel.parse_obj(resp["data"])

    # -------------------------------------------------------------------------
    # Elapsed Times (within a Round)
    # -------------------------------------------------------------------------
    def find_elapsed_times(
        self,
        race_id: str,
        round_id: str,
        page: int = 1,
        per_page: int = 25
    ) -> List[models.ElapsedTimeModel]:
        """
        GET /races/{race_id}/rounds/{round_id}/elapsed_times.json
        Returns an array of ElapsedTimeModels in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}/elapsed_times.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        if "data" in resp and isinstance(resp["data"], list):
            return [models.ElapsedTimeModel.parse_obj(item) for item in resp["data"]]
        return []

    def show_elapsed_time(self, race_id: str, round_id: str, elapsed_time_id: str) -> models.ElapsedTimeModel:
        """
        GET /races/{race_id}/rounds/{round_id}/elapsed_times/{id}.json
        Returns a single ElapsedTimeModel in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}/elapsed_times/{elapsed_time_id}.json"
        resp = self._request("GET", endpoint)
        return models.ElapsedTimeModel.parse_obj(resp["data"])

    def update_elapsed_time(
        self,
        race_id: str,
        round_id: str,
        elapsed_time_id: str,
        elapsed_time_attributes: Dict[str, Any]
    ) -> models.ElapsedTimeModel:
        """
        PUT /races/{race_id}/rounds/{round_id}/elapsed_times/{id}.json
        Updates a single elapsed time. Returns updated ElapsedTimeModel in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}/elapsed_times/{elapsed_time_id}.json"
        payload = {
            "data": {
                "type": "ElaspedTime",
                "attributes": elapsed_time_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.ElapsedTimeModel.parse_obj(resp["data"])

    def bulk_update_elapsed_times(
        self,
        race_id: str,
        round_id: str,
        bulk_attributes: Dict[str, Any]
    ) -> List[models.ElapsedTimeModel]:
        """
        POST /races/{race_id}/rounds/{round_id}/elapsed_times/bulk_update.json
        Bulk updates multiple elapsed time records at once. 
        Typically returns an array of updated ElapsedTimeModels in "data".
        """
        endpoint = f"/races/{race_id}/rounds/{round_id}/elapsed_times/bulk_update.json"
        resp = self._request("POST", endpoint, json_data=bulk_attributes)
        if not resp or "data" not in resp:
            return []
        return [models.ElapsedTimeModel.parse_obj(item) for item in resp["data"]]

    # -------------------------------------------------------------------------
    # Communities & Community Tournaments
    # -------------------------------------------------------------------------
    def find_communities(self) -> List[models.CommunityModel]:
        """
        GET /communities.json
        Returns administered communities by the user in shape: {"data": [ ... ]}
        """
        endpoint = "/communities.json"
        resp = self._request("GET", endpoint)
        if not resp or "data" not in resp:
            return []
        return [models.CommunityModel.parse_obj(item) for item in resp["data"]]

    def find_community_tournaments(
        self,
        community_identifier: str,
        page: int = 1,
        per_page: int = 25,
        state: Optional[str] = None,
        tournament_type: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None
    ) -> List[models.TournamentModel]:
        """
        GET /communities/{community_identifier}/tournaments.json
        Returns tournaments belonging to a community (array of TournamentModel).
        """
        endpoint = f"/communities/{community_identifier}/tournaments.json"
        params = {
            "page": str(page),
            "per_page": str(per_page),
        }
        if state:
            params["state"] = state
        if tournament_type:
            params["type"] = tournament_type
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before

        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.TournamentModel.parse_obj(item) for item in resp["data"]]

    def create_community_tournament(
        self,
        community_identifier: str,
        tournament_attributes: Dict[str, Any]
    ) -> models.TournamentModel:
        """
        POST /communities/{community_identifier}/tournaments.json
        Creates a tournament under a community (returns single TournamentModel in "data").
        """
        endpoint = f"/communities/{community_identifier}/tournaments.json"
        payload = {
            "data": {
                "type": "Tournaments",
                "attributes": tournament_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        return models.TournamentModel.parse_obj(resp["data"])

    def show_community_tournament(
        self,
        community_identifier: str,
        tournament_id: str
    ) -> models.TournamentModel:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}.json
        Returns a single TournamentModel in "data".
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}.json"
        resp = self._request("GET", endpoint)
        return models.TournamentModel.parse_obj(resp["data"])

    def update_community_tournament(
        self,
        community_identifier: str,
        tournament_id: str,
        tournament_attributes: Dict[str, Any]
    ) -> models.TournamentModel:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}.json
        Updates a community tournament. Returns updated TournamentModel in "data".
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}.json"
        payload = {
            "data": {
                "type": "Tournaments",
                "attributes": tournament_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.TournamentModel.parse_obj(resp["data"])

    def delete_community_tournament(
        self,
        community_identifier: str,
        tournament_id: str
    ) -> None:
        """
        DELETE /communities/{community_identifier}/tournaments/{tournament_id}.json
        Deletes a community tournament (204 No Content).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}.json"
        self._request("DELETE", endpoint)

    def change_state_community_tournament(
        self,
        community_identifier: str,
        tournament_id: str,
        new_state: str
    ) -> models.TournamentModel:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}/change_state.json
        Changes a community tournament's state. Returns updated TournamentModel in "data".
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/change_state.json"
        payload = {
            "data": {
                "type": "TournamentState",
                "attributes": {
                    "state": new_state
                }
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.TournamentModel.parse_obj(resp["data"])

    # -------------------------------------------------------------------------
    # Community Matches
    # -------------------------------------------------------------------------
    def find_community_matches(
        self,
        community_identifier: str,
        tournament_id: str,
        page: int = 1,
        per_page: int = 25,
        state: Optional[str] = None,
        participant_id: Optional[str] = None
    ) -> List[models.MatchModel]:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}/matches.json
        Returns an array of matches (MatchModel) for a community tournament.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/matches.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        if state:
            params["state"] = state
        if participant_id:
            params["participant_id"] = participant_id

        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.MatchModel.parse_obj(item) for item in resp["data"]]

    def show_community_match(
        self,
        community_identifier: str,
        tournament_id: str,
        match_id: str
    ) -> models.MatchModel:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}/matches/{id}.json
        Returns a single MatchModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/matches/{match_id}.json"
        resp = self._request("GET", endpoint)
        return models.MatchModel.parse_obj(resp)

    def update_community_match(
        self,
        community_identifier: str,
        tournament_id: str,
        match_id: str,
        match_attributes: Dict[str, Any]
    ) -> models.MatchModel:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}/matches/{id}.json
        Updates a match (scores, etc.) in a community tournament.
        Returns updated MatchModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/matches/{match_id}.json"
        payload = {
            "data": {
                "type": "Match",
                "attributes": match_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.MatchModel.parse_obj(resp)

    def change_stage_community_tournament(
        self,
        community_identifier: str,
        tournament_id: str,
        match_state_attributes: Dict[str, Any]
    ) -> models.MatchModel:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}/change_stage.json
        Possibly changes the 'stage' of a community tournament or match 
        (Swagger tags: "Community Match" but references a MatchStateInput).
        Returns a MatchModel (based on the Swagger).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/change_stage.json"
        payload = {
            "data": {
                "type": "MatchState",
                "attributes": match_state_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.MatchModel.parse_obj(resp)

    # -------------------------------------------------------------------------
    # Community Participants
    # -------------------------------------------------------------------------
    def find_community_participants(
        self,
        community_identifier: str,
        tournament_id: str,
        page: int = 1,
        per_page: int = 25
    ) -> List[models.ParticipantModel]:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}/participants.json
        Returns participants (ParticipantModel) of a community tournament.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants.json"
        params = {
            "page": str(page),
            "per_page": str(per_page)
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    def create_community_participant(
        self,
        community_identifier: str,
        tournament_id: str,
        participant_attributes: Dict[str, Any]
    ) -> models.ParticipantModel:
        """
        POST /communities/{community_identifier}/tournaments/{tournament_id}/participants.json
        Creates a participant in a community tournament. Returns a single ParticipantModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": participant_attributes
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        if isinstance(resp, dict) and "data" in resp:
            return models.ParticipantModel.parse_obj(resp["data"])
        elif isinstance(resp, list) and resp:
            return models.ParticipantModel.parse_obj(resp[0])
        raise ValueError("Unexpected response format for create_community_participant.")

    def show_community_participant(
        self,
        community_identifier: str,
        tournament_id: str,
        participant_id: str
    ) -> models.ParticipantModel:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json
        Shows a single participant (ParticipantModel).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json"
        resp = self._request("GET", endpoint)
        return models.ParticipantModel.parse_obj(resp)

    def update_community_participant(
        self,
        community_identifier: str,
        tournament_id: str,
        participant_id: str,
        participant_attributes: Dict[str, Any]
    ) -> models.ParticipantModel:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json
        Updates a participant in a community tournament. Returns updated ParticipantModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": participant_attributes
            }
        }
        resp = self._request("PUT", endpoint, json_data=payload)
        return models.ParticipantModel.parse_obj(resp)

    def delete_community_participant(
        self,
        community_identifier: str,
        tournament_id: str,
        participant_id: str
    ) -> None:
        """
        DELETE /communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json
        Deletes or deactivates a participant (204 No Content).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/{participant_id}.json"
        self._request("DELETE", endpoint)

    def bulk_community_create_participant(
        self,
        community_identifier: str,
        tournament_id: str,
        participants: List[Dict[str, Any]]
    ) -> List[models.ParticipantModel]:
        """
        POST /communities/{community_identifier}/tournaments/{tournament_id}/participants/bulk_add.json
        Bulk creates participants in a community tournament.
        Returns an array of ParticipantModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/bulk_add.json"
        payload = {
            "data": {
                "type": "Participants",
                "attributes": {
                    "participants": participants
                }
            }
        }
        resp = self._request("POST", endpoint, json_data=payload)
        if not resp:
            return []
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    def clear_all_community_participants(
        self,
        community_identifier: str,
        tournament_id: str
    ) -> None:
        """
        DELETE /communities/{community_identifier}/tournaments/{tournament_id}/participants/clear.json
        Clears all participants from a community tournament (204 No Content).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/clear.json"
        self._request("DELETE", endpoint)

    def randomize_community_participants(
        self,
        community_identifier: str,
        tournament_id: str
    ) -> List[models.ParticipantModel]:
        """
        PUT /communities/{community_identifier}/tournaments/{tournament_id}/participants/randomize.json
        Randomizes participant seeding within a community tournament. Returns an array of ParticipantModel.
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/participants/randomize.json"
        resp = self._request("PUT", endpoint)
        if not resp:
            return []
        return [models.ParticipantModel.parse_obj(item) for item in resp["data"]]

    # -------------------------------------------------------------------------
    # Community Match Attachments
    # -------------------------------------------------------------------------
    def find_community_match_attachments(
        self,
        community_identifier: str,
        tournament_id: str,
        match_id: str,
        page: int = 1,
        per_page: int = 25
    ) -> List[models.MatchAttachmentModel]:
        """
        GET /communities/{community_identifier}/tournaments/{tournament_id}/match_attachments.json
        Returns match attachments for a given community match as an array (MatchAttachmentModel).
        Possibly via query param "match_id".
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/match_attachments.json"
        params = {
            "page": str(page),
            "per_page": str(per_page),
            "match_id": match_id,
        }
        resp = self._request("GET", endpoint, params=params)
        if not resp:
            return []
        return [models.MatchAttachmentModel.parse_obj(item) for item in resp["data"]]

    def create_community_match_attachment(
        self,
        community_identifier: str,
        tournament_id: str,
        match_id: str,
        attachment_attributes: Dict[str, Any]
    ) -> models.MatchAttachmentModel:
        """
        POST /communities/{community_identifier}/tournaments/{tournament_id}/match_attachments.json
        Creates an attachment for a community match (returns one MatchAttachmentModel).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/match_attachments.json"
        payload = {
            "data": {
                "type": "match_attachment",
                "attributes": attachment_attributes
            }
        }
        # We'll store match_id in the payload if needed
        payload["data"]["attributes"]["match_id"] = match_id
        resp = self._request("POST", endpoint, json_data=payload)
        return models.MatchAttachmentModel.parse_obj(resp)

    def delete_community_match_attachment(
        self,
        community_identifier: str,
        tournament_id: str,
        match_id: str,
        attachment_id: str
    ) -> None:
        """
        DELETE /communities/{community_identifier}/tournaments/{tournament_id}/match_attachments/{id}.json
        Deletes a match attachment in a community tournament (204 No Content).
        """
        endpoint = f"/communities/{community_identifier}/tournaments/{tournament_id}/match_attachments/{attachment_id}.json"
        self._request("DELETE", endpoint)

    # -------------------------------------------------------------------------
    # User (i.e. /me)
    # -------------------------------------------------------------------------
    def get_me(self) -> models.UserModel:
        """
        GET /me.json
        Returns the user (logged in via OAuth2 or the API key owner).
        Typically in shape: {"id": "xyz", "type": "user", "attributes": { ... }} or 
        { "data": { "id": ..., "type": "user", "attributes": ... } } depending on the doc.

        The original swagger suggests it's "schema":{"$ref":"#/definitions/UserModel"} 
        without a "data" wrapper. We'll adapt carefully.
        """
        endpoint = "/me.json"
        resp = self._request("GET", endpoint)
        # If the server returns a top-level object shaped like UserModel:
        # {
        #   "id": "321",
        #   "type": "user",
        #   "attributes": { ... }
        # }
        # then just parse_obj(resp).
        # If the server instead sends { "data": { ... } }, parse_obj(resp["data"]).
        if "data" in resp:
            return models.UserModel.parse_obj(resp["data"])
        return models.UserModel.parse_obj(resp)
