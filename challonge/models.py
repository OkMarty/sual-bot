# models.py

from typing import Any, List, Optional, Union, Dict
from pydantic import BaseModel, Field


#
# ----------------------------- COMMON MODELS -----------------------------
#

class Timestamps(BaseModel):
    """
    Common timestamp fields appearing in several definitions.
    """
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    starts_at: Optional[str] = Field(None, alias="startsAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")


#
# ----------------------------- MATCH ATTACHMENT -----------------------------
#

class MatchAttachment(BaseModel):
    """
    For input or nested usage:
      url: str
      description: str
      asset: (object, if the API supports file uploads as JSON)
    """
    url: Optional[str] = None
    description: Optional[str] = None
    asset: Optional[Dict[str, Any]] = None


class MatchAttachmentOutput(BaseModel):
    """
    For reading an attachment from the API:
      {
        "id": 332211,
        "url": "...",
        "description": "...",
        "timestamps": { ... }
      }
    """
    id: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    timestamps: Optional[Timestamps] = None


class MatchAttachmentModel(BaseModel):
    """
    Full resource shape:
      {
        "id": "332211",
        "type": "match_attachment",
        "attributes": { ... } -> MatchAttachmentOutput
      }
    """
    id: str
    type: str
    attributes: MatchAttachmentOutput


#
# ----------------------------- PARTICIPANTS -----------------------------
#

class Participant(BaseModel):
    """
    Participant input shape. 
    For creation:
      name (required)
      seed
      misc
      email
      username
    """
    name: str
    seed: Optional[int] = None
    misc: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None


class ParticipantOutput(BaseModel):
    """
    Participant read shape from the API:
      {
        "name": "...",
        "seed": 1,
        "group_id": ...,
        "username": "...",
        "final_rank": ...,
        "states": { "active": true },
        "misc": "...",
        "timestamps": { ... }
      }
    """
    name: Optional[str] = None
    seed: Optional[int] = None
    group_id: Optional[int] = None
    username: Optional[str] = None
    final_rank: Optional[int] = Field(None, alias="final_rank")
    states: Optional[Dict[str, Any]] = None
    misc: Optional[str] = None
    timestamps: Optional[Timestamps] = None


class ParticipantModel(BaseModel):
    """
    {
      "id": "76",
      "type": "participant",
      "attributes": ParticipantOutput
    }
    """
    id: str
    type: str
    attributes: ParticipantOutput


#
# ----------------------------- TOURNAMENTS -----------------------------
#

# Sub-models for advanced tournament fields

class Notifications(BaseModel):
    upon_matches_open: Optional[bool] = Field(False, alias="upon_matches_open")
    upon_tournament_ends: Optional[bool] = Field(False, alias="upon_tournament_ends")


class MatchOptions(BaseModel):
    consolation_matches_target_rank: Optional[int] = Field(3, alias="consolation_matches_target_rank")
    accept_attachments: Optional[bool] = Field(False, alias="accept_attachments")


class RegistrationOptions(BaseModel):
    open_signup: Optional[bool] = Field(False, alias="open_signup")
    signup_cap: Optional[int] = Field(None, alias="signup_cap")
    check_in_duration: Optional[int] = Field(None, alias="check_in_duration")


class SeedingOptions(BaseModel):
    hide_seeds: Optional[bool] = Field(False, alias="hide_seeds")
    sequential_pairings: Optional[bool] = Field(False, alias="sequential_pairings")


class StationOptions(BaseModel):
    auto_assign: Optional[bool] = Field(False, alias="auto_assign")
    only_start_matches_with_assigned_stations: Optional[bool] = Field(
        False, alias="only_start_matches_with_assigned_stations"
    )


class GroupStageOptions(BaseModel):
    stage_type: Optional[str] = Field("round robin", alias="stage_type")
    group_size: Optional[int] = Field(4, alias="group_size")
    participant_count_to_advance_per_group: Optional[int] = Field(2, alias="participant_count_to_advance_per_group")
    rr_iterations: Optional[int] = Field(1, alias="rr_iterations")
    ranked_by: Optional[str] = Field("", alias="ranked_by")
    rr_pts_for_match_win: Optional[float] = Field(1.0, alias="rr_pts_for_match_win")
    rr_pts_for_match_tie: Optional[float] = Field(0.5, alias="rr_pts_for_match_tie")
    rr_pts_for_game_win: Optional[float] = Field(0.0, alias="rr_pts_for_game_win")
    rr_pts_for_game_tie: Optional[float] = Field(0.0, alias="rr_pts_for_game_tie")
    split_participants: Optional[bool] = Field(False, alias="split_participants")


class DoubleEliminationOptions(BaseModel):
    split_participants: Optional[bool] = Field(False, alias="split_participants")
    grand_finals_modifier: Optional[str] = Field("", alias="grand_finals_modifier")


class RoundRobinOptions(BaseModel):
    iterations: Optional[int] = Field(2, alias="iterations")
    ranking: Optional[str] = Field("", alias="ranking")
    pts_for_game_win: Optional[float] = Field(1.0, alias="pts_for_game_win")
    pts_for_game_tie: Optional[float] = Field(0.0, alias="pts_for_game_tie")
    pts_for_match_win: Optional[float] = Field(1.0, alias="pts_for_match_win")
    pts_for_match_tie: Optional[float] = Field(0.5, alias="pts_for_match_tie")


class SwissOptions(BaseModel):
    rounds: Optional[int] = Field(2, alias="rounds")
    pts_for_game_win: Optional[float] = Field(1.0, alias="pts_for_game_win")
    pts_for_game_tie: Optional[float] = Field(0.0, alias="pts_for_game_tie")
    pts_for_match_win: Optional[float] = Field(1.0, alias="pts_for_match_win")
    pts_for_match_tie: Optional[float] = Field(0.5, alias="pts_for_match_tie")


class FreeForAllOptions(BaseModel):
    max_participants: Optional[int] = Field(4, alias="max_participants")


class Tournament(BaseModel):
    """
    The main 'attributes' for a Tournament, as per the Swagger's 'Tournament' definition.
    """
    name: str = Field(..., alias="name")
    url: Optional[str] = Field(None, alias="url")
    tournament_type: str = Field(..., alias="tournament_type")
    game_name: Optional[str] = Field(None, alias="game_name")
    private: Optional[bool] = Field(False, alias="private")
    starts_at: Optional[str] = Field(None, alias="starts_at")
    description: Optional[str] = None
    notifications: Optional[Notifications] = None
    match_options: Optional[MatchOptions] = None
    registration_options: Optional[RegistrationOptions] = None
    seeding_options: Optional[SeedingOptions] = None
    station_options: Optional[StationOptions] = None
    group_stage_enabled: Optional[bool] = Field(False, alias="group_stage_enabled")
    group_stage_options: Optional[GroupStageOptions] = None
    double_elimination_options: Optional[DoubleEliminationOptions] = None
    round_robin_options: Optional[RoundRobinOptions] = None
    swiss_options: Optional[SwissOptions] = None
    free_for_all_options: Optional[FreeForAllOptions] = None


class TournamentAttributes(Tournament):
    """
    Extends the main tournament fields, but also includes timestamps for reading.
    """
    timestamps: Optional[Timestamps] = None


class TournamentModel(BaseModel):
    """
    Outer structure for reading a Tournament from the API:
      {
        "id": "30201",
        "type": "tournament",
        "attributes": { ... } -> TournamentAttributes
      }
    """
    id: str
    type: str
    attributes: TournamentAttributes


#
# ----------------------------- MATCHES -----------------------------
#

# Relationship data for a participant reference
class RelationshipResourceIdentifier(BaseModel):
    """
    A simple { "id": "355", "type": "participant" } object
    """
    id: str
    type: str


class ParticipantRelationship(BaseModel):
    """
    For something like:
    "player1": {
      "data": { "id": "355", "type": "participant" }
    }
    """
    data: Optional[RelationshipResourceIdentifier] = None


class MatchRelationships(BaseModel):
    """
    For "relationships": { "player1": {...}, "player2": {...} }
    """
    player1: Optional[ParticipantRelationship] = None
    player2: Optional[ParticipantRelationship] = None


class MatchParticipantPoints(BaseModel):
    """
    For 'points_by_participant':
      { "participant_id": 355, "scores": [3,4] }
    """
    participant_id: Optional[int] = None
    scores: Optional[List[int]] = None


class MatchAttributes(BaseModel):
    """
    Detailed fields from the 'MatchOutput' definition:
      state, round, identifier, scores, winner_id, etc.
    """
    state: Optional[str] = None
    round: Optional[int] = None
    identifier: Optional[str] = None
    suggested_play_order: Optional[int] = None
    scores: Optional[str] = None
    score_in_sets: Optional[List[List[int]]] = None
    points_by_participant: Optional[List[MatchParticipantPoints]] = None
    timestamps: Optional[Timestamps] = None
    winner_id: Optional[int] = None


class MatchModel(BaseModel):
    """
    {
      "id": "8008135",
      "type": "match",
      "attributes": MatchAttributes,
      "relationships": {
        "player1": {
          "data": { "id": "355", "type": "participant" }
        },
        "player2": {
          "data": { "id": "354", "type": "participant" }
        }
      }
    }
    """
    id: str
    type: str
    attributes: MatchAttributes
    relationships: Optional[MatchRelationships] = None


#
# ----------------------------- USER -----------------------------
#

class User(BaseModel):
    """
    {
      "email": "hello@challonge.com",
      "username": "APIUser",
      "image_url": "..."
    }
    """
    email: Optional[str] = None
    username: Optional[str] = None
    image_url: Optional[str] = None


class UserModel(BaseModel):
    """
    {
      "id": "321",
      "type": "user",
      "attributes": User
    }
    """
    id: str
    type: str
    attributes: User


#
# ----------------------------- COMMUNITY -----------------------------
#

class Community(BaseModel):
    """
    {
      "permalink": "nerdfest",
      "subdomain": "nerdfest",
      "identifier": "nerdfest",
      "name": "Nerdfest PH",
      "description": "Everyone should go to Nerdfest. Thank you.",
      "timestamps": { ... }
    }
    """
    permalink: Optional[str] = None
    subdomain: Optional[str] = None
    identifier: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    timestamps: Optional[Timestamps] = None


class CommunityModel(BaseModel):
    """
    {
      "id": "101",
      "type": "Community",
      "attributes": Community
    }
    """
    id: str
    type: str
    attributes: Community


#
# ----------------------------- RACES -----------------------------
#

class RaceNotifications(BaseModel):
    uponMatchesOpen: Optional[bool] = Field(False, alias="uponMatchesOpen")
    uponTournamentEnds: Optional[bool] = Field(False, alias="uponTournamentEnds")


class RaceRegistrationOptions(BaseModel):
    openSignup: Optional[bool] = Field(False, alias="openSignup")
    signupCap: Optional[int] = Field(None, alias="signupCap")


class GrandPrixOptions(BaseModel):
    rounds: Optional[int] = Field(4, alias="rounds")


class RaceAttributes(BaseModel):
    """
    {
      "name": "Horse Racing 101",
      "url": "horse_racing_101",
      "raceType": "time trial",
      "description": "...",
      "private": false,
      "currentLap": { "id": 15, "number": 1 },
      "notifications": { ... },
      "registrationOptions": { ... },
      "grandPrixOptions": { ... },
      "timestamps": { ... }
    }
    """
    name: Optional[str] = None
    url: Optional[str] = None
    raceType: Optional[str] = None
    description: Optional[str] = None
    private: Optional[bool] = None
    currentLap: Optional[Dict[str, Any]] = None
    notifications: Optional[RaceNotifications] = None
    registrationOptions: Optional[RaceRegistrationOptions] = None
    grandPrixOptions: Optional[GrandPrixOptions] = None
    timestamps: Optional[Timestamps] = None


class RaceModel(BaseModel):
    """
    {
      "id": "horse_racing_101",
      "type": "Race",
      "attributes": RaceAttributes
    }
    """
    id: str
    type: str
    attributes: RaceAttributes


#
# ----------------------------- ROUNDS (within Races) -----------------------------
#

class RoundAttributes(BaseModel):
    """
    For a round in a Race:
    {
      "round": 1,
      "state": "pending",
      "timestamps": { ... }
    }
    """
    round: Optional[int] = None
    state: Optional[str] = None
    timestamps: Optional[Timestamps] = None


class RoundModel(BaseModel):
    """
    {
      "id": "8008135",
      "type": "RoundOutput",
      "attributes": RoundAttributes
    }
    """
    id: str
    type: str
    attributes: RoundAttributes


#
# ----------------------------- ELAPSED TIME (within Rounds) -----------------------------
#

class ElapsedTimeAttributes(BaseModel):
    """
    {
      "elapsedTime": 1000,
      "points": 0.0,
      "rank": 1,
      "formattedTime": "00:00:001.001",
      "timestamps": { ... }
    }
    """
    elapsedTime: Optional[int] = None
    points: Optional[float] = None
    rank: Optional[int] = None
    formattedTime: Optional[str] = None
    timestamps: Optional[Timestamps] = None


class ElapsedTimeModel(BaseModel):
    """
    {
      "id": "123456",
      "type": "Elapsed Time",
      "attributes": ElapsedTimeAttributes
    }
    """
    id: str
    type: str
    attributes: ElapsedTimeAttributes
