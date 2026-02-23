from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from typing import List

#sqlmodel
class Region(SQLModel, table=True):
    region_id: int | None = Field(default=None, primary_key=True)
    name_th: str = Field(unique=True)
    total_population: int | None = Field(default=0)

class Constituency(SQLModel, table=True):
    const_id: int | None = Field(default=None, primary_key=True)
    region_id: int
    const_number: int
    total_eligible_voters: int | None = Field(default=0)

class Party(SQLModel, table=True):
    party_id: int | None = Field(default=None, primary_key=True)
    party_name: str = Field(unique=True)
    party_leader: str | None = None
    party_logo_url: str | None = None

class Candidate(SQLModel, table=True):
    candidate_id: int | None = Field(default=None, primary_key=True)
    const_id: int
    party_id: int
    candidate_number: int
    full_name: str

class Voter(SQLModel, table=True):
    voter_id: int | None = Field(default=None, primary_key=True)
    citizen_id: str = Field(unique=True)
    full_name: str
    const_id: int
    has_voted_const: int | None = Field(default=0)
    has_voted_list: int | None = Field(default=0)

class Ballot(SQLModel, table=True):
    ballot_id: int | None = Field(default=None, primary_key=True)
    const_id: int
    candidate_id: int | None = None
    party_id: int | None = None
    vote_type: str
    voted_at: str | None = None

#basemodel

class RegionIn(BaseModel):
    name_th: str
    total_population: int | None = 0

class RegionOut(RegionIn):
    region_id: int

class ConstituencyIn(BaseModel):
    region_id: int
    const_number: int
    total_eligible_voters: int | None = 0

class ConstituencyOut(ConstituencyIn):
    const_id: int

class PartyIn(BaseModel):
    party_name: str
    party_leader: str | None = None
    party_logo_url: str | None = None

class PartyOut(PartyIn):
    party_id: int

class CandidateIn(BaseModel):
    const_id: int
    party_id: int
    candidate_number: int
    full_name: str

class CandidateOut(CandidateIn):
    candidate_id: int
    constituency_detail: ConstituencyOut | None = None

class VoterIn(BaseModel):
    citizen_id: str
    full_name: str
    const_id: int
    has_voted_const: int | None = 0
    has_voted_list: int | None = 0

class VoterOut(VoterIn):
    voter_id: int
    constituency_detail: ConstituencyOut | None = None

class BallotIn(BaseModel):
    const_id: int
    candidate_id: int | None = None
    party_id: int | None = None
    vote_type: str
    voted_at: str | None = None

class BallotOut(BallotIn):
    ballot_id: int
