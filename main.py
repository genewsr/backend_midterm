from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select, func
from database import engine, create_db_and_tables
from models import (
    Region, Constituency, Party, Candidate, Voter, Ballot,
    PartyIn, CandidateIn, VoterIn, BallotIn
)

app = FastAPI()

def insert_mock_data():
    r1 = Region(name_th="ภาคกลาง", total_population=2500000)
    r2 = Region(name_th="ภาคเหนือ", total_population=1200000)
    r3 = Region(name_th="ภาคอีสาน", total_population=2000000)
    r4 = Region(name_th="ภาคใต้", total_population=1000000)

    c1 = Constituency(region_id=1, const_number=1, total_eligible_voters=50000)
    c2 = Constituency(region_id=2, const_number=1, total_eligible_voters=45000)
    
    p1 = Party(party_name="พรรคประชาชน", party_leader="ณัฐพงศ์", party_logo_url="logo1.jpg")
    p2 = Party(party_name="พรรคเพื่อไทย", party_leader="ยศชนันดิ์", party_logo_url="logo2.jpg")
    p3 = Party(party_name="พรรคภูมิใจไทย", party_leader="อนุทิน", party_logo_url="logo3.jpg")

    with Session(engine) as s:
        s.add(r1)
        s.add(r2)
        s.add(r3)
        s.add(r4)
        s.add(c1)
        s.add(c2)
        s.add(p1)
        s.add(p2)
        s.add(p3)
        s.commit()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#1.เพิ่ม/แสดงรายชื่อพรรคการเมือง,ผู้สมัคร ส.ส. เขต 
@app.post("/Parties/")
async def create_party(party: PartyIn):
    new_party = Party(**party.model_dump())
    with Session(engine) as s:
        s.add(new_party)
        s.commit()
        s.refresh(new_party)
        return new_party

@app.get("/Parties/")
async def get_parties():
    with Session(engine) as s:
        parties = s.exec(select(Party)).all()
        return parties

@app.post("/Candidates/")
async def create_candidate(candidate: CandidateIn):
    new_candidate = Candidate(**candidate.model_dump())
    with Session(engine) as s:
        s.add(new_candidate)
        s.commit()
        s.refresh(new_candidate)
        return new_candidate

@app.get("/Candidates/")
async def get_candidates():
    with Session(engine) as s:
        candidates = s.exec(select(Candidate)).all()
        result = []
        
        for c in candidates:
            statement_party = select(Party).where(Party.party_id == c.party_id)
            party = s.exec(statement_party).first()
            
            c_dict = c.model_dump()
            
            if party:
                c_dict["party_detail"] = party.model_dump()
            else:
                c_dict["party_detail"] = None
                
            statement_const = select(Constituency).where(Constituency.const_id == c.const_id)
            const = s.exec(statement_const).first()
            
            if const:
                c_dict["constituency_detail"] = const.model_dump()
                
            result.append(c_dict)
            
        return result

#2.เพิ่ม/แสดงผู้มีสิทธิ์เลือกตั้งและอัพเดทสถานะ

@app.post("/Voters/")
async def create_voter(voter: VoterIn):
    new_voter = Voter(**voter.model_dump())
    with Session(engine) as s:
        s.add(new_voter)
        s.commit()
        s.refresh(new_voter)
        return new_voter

@app.get("/Voters/")
async def get_voters():
    with Session(engine) as s:
        voters = s.exec(select(Voter)).all()
        result = []
        for v in voters:
            const = s.exec(select(Constituency).where(Constituency.const_id == v.const_id)).first()
            
            v_dict = v.model_dump()
            if const:
                v_dict["constituency_detail"] = const.model_dump()
            else:
                v_dict["constituency_detail"] = None
                
            result.append(v_dict)
            
        return result

@app.get("/Voters/{voter_id}")
async def get_voter(voter_id: int):
    with Session(engine) as s:
        voter = s.get(Voter, voter_id)
        
        if not voter:
            raise HTTPException(status_code=404, detail="ไม่พบผู้มีสิทธิ์เลือกตั้งท่านนี้")
            
        statement = select(Constituency).where(Constituency.const_id == voter.const_id)
        const = s.exec(statement).first()
        
        v_dict = voter.model_dump()
        if const:
            v_dict["constituency_detail"] = const.model_dump()
        else:
            v_dict["constituency_detail"] = None
            
        return v_dict
    
@app.patch("/Voters/{voter_id}/vote_status")
async def update_vote_status(voter_id: int):
    with Session(engine) as s:
        voter = s.get(Voter, voter_id)
        
        if not voter:
            raise HTTPException(status_code=404, detail="Voter not found")
            
        if voter.has_voted_const == 1 and voter.has_voted_list == 1:
             raise HTTPException(status_code=400, detail="ผู้มีสิทธิ์ท่านนี้ลงคะแนนไปแล้ว")
             
        voter.has_voted_const = 1
        voter.has_voted_list = 1
        
        s.add(voter)
        s.commit()
        s.refresh(voter)
        
        return {"message": "อัพเดทสถานะการลงคะแนนเรียบร้อย", "voterID": voter.voter_id}

#3.บันทึกการลงคะแนน/แสดงจำนวนผู้ลงคะแนนแยกตามเขต

@app.post("/Ballots/")
async def create_ballot(ballot: BallotIn):
    new_ballot = Ballot(**ballot.model_dump())
    with Session(engine) as s:
        s.add(new_ballot)
        s.commit()
        s.refresh(new_ballot)
        return new_ballot

@app.get("/Ballots/count")
async def get_vote_count():
    with Session(engine) as s:
        statement = select(Ballot.const_id, Ballot.vote_type, func.count(Ballot.ballot_id)).group_by(Ballot.const_id, Ballot.vote_type)
        results = s.exec(statement).all()
        
        output = []
        for const_id, vote_type, count in results:
            output.append({
                "const_id": const_id,
                "vote_type": vote_type,
                "total_votes": count
            })
        return output

# 4.แสดงผลการเลือกตั้งแบบภาพรวมและแบบแยกตามเขต

@app.get("/Results/Parties/")
async def get_party_results(const_id: int | None = None):
    with Session(engine) as s:
        statement = select(Ballot.party_id, func.count(Ballot.ballot_id)).where(Ballot.vote_type == 'PartyList')
        
        if const_id:
            statement = statement.where(Ballot.const_id == const_id)
            
        statement = statement.group_by(Ballot.party_id)
        results = s.exec(statement).all()
        
        output = []
        for pid, count in results:
            if pid is not None:
                output.append({"party_id": pid, "total_votes": count})
        return output

@app.get("/Results/Candidates/")
async def get_candidate_results(const_id: int | None = None):
    with Session(engine) as s:
        statement = select(Ballot.candidate_id, Ballot.const_id, func.count(Ballot.ballot_id)).where(Ballot.vote_type == 'Constituency')
        
        if const_id:
            statement = statement.where(Ballot.const_id == const_id)
            
        statement = statement.group_by(Ballot.candidate_id, Ballot.const_id)
        results = s.exec(statement).all()
        
        output = []
        for cid, c_id, count in results:
            if cid is not None:
                output.append({"candidate_id": cid, "const_id": c_id, "total_votes": count})
        return output