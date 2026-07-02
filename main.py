from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="GigHub API",
    version="1.0.0",
    description="Nairobi Freelancing Platform - Student Lab"
)

# ---------- Pydantic Models ----------
class GigCreate(BaseModel):
    title: str
    description: str
    category: str = Field(..., pattern="^(Marketing|Data|Consulting)$")
    budget: float = Field(..., gt=0, description="Budget in KES")
    client_name: str

class GigUpdate(BaseModel):
    budget: Optional[float] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(Open|In Progress|Closed)$")

class Gig(GigCreate):
    id: int
    status: str = "Open"

# ---------- In-memory DB with 8 sample gigs - Your Class ----------
gigs_db: List[Gig] = [
    Gig(id=1, title="Social Media Campaign", description="Run IG + TikTok ads for 1 month", category="Marketing", budget=25000, client_name="James Guchu", status="Open"),
    Gig(id=2, title="Data Cleaning for Survey", description="Clean survey data in Excel", category="Data", budget=15000, client_name="Jimmy Otieno", status="Open"),
    Gig(id=3, title="Business Strategy Consulting", description="2 week consulting for startup", category="Consulting", budget=80000, client_name="Hilary Kiptoo", status="In Progress"),
    Gig(id=4, title="SEO Blog Writing", description="10 blog posts for website", category="Marketing", budget=30000, client_name="Ian Odiek", status="Open"),
    Gig(id=5, title="Sales Dashboard", description="Build PowerBI dashboard", category="Data", budget=60000, client_name="Rodah Kerubo", status="Closed"),
    Gig(id=6, title="Market Research", description="Research for new product launch", category="Consulting", budget=45000, client_name="Brian Kirunde", status="Open"),
    Gig(id=7, title="Email Marketing Setup", description="Setup Mailchimp + templates", category="Marketing", budget=18000, client_name="Mercy Wambui", status="Open"),
    Gig(id=8, title="Data Visualization", description="Create charts from sales data", category="Data", budget=22000, client_name="Kevin Mutiso", status="In Progress"),
]

next_id = 9

# ---------- Endpoints ----------

@app.get("/gigs", response_model=List[Gig])
def get_all_gigs(
    category: Optional[str] = Query(None, pattern="^(Marketing|Data|Consulting)$"),
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None
):
    """Get all gigs with optional filtering by category, min_budget, max_budget"""
    filtered = gigs_db
    if category:
        filtered = [g for g in filtered if g.category == category]
    if min_budget is not None:
        filtered = [g for g in filtered if g.budget >= min_budget]
    if max_budget is not None:
        filtered = [g for g in filtered if g.budget <= max_budget]
    return filtered

@app.get("/gigs/{gig_id}", response_model=Gig)
def get_gig_by_id(gig_id: int):
    """Get single gig by ID"""
    for gig in gigs_db:
        if gig.id == gig_id:
            return gig
    raise HTTPException(status_code=404, detail="Gig not found")

@app.get("/gigs/search", response_model=List[Gig])
def search_gigs(q: str = Query(..., min_length=1)):
    """Search gigs by title"""
    results = [g for g in gigs_db if q.lower() in g.title.lower()]
    return results

@app.post("/gigs", response_model=Gig, status_code=201)
def create_gig(gig: GigCreate):
    """Create a new gig"""
    global next_id
    new_gig = Gig(id=next_id, **gig.dict())
    gigs_db.append(new_gig)
    next_id += 1
    return new_gig

@app.put("/gigs/{gig_id}", response_model=Gig)
def update_gig(gig_id: int, gig_update: GigUpdate):
    """Update a gig's budget or status"""
    for gig in gigs_db:
        if gig.id == gig_id:
            if gig_update.budget is not None:
                gig.budget = gig_update.budget
            if gig_update.status is not None:
                gig.status = gig_update.status
            return gig
    raise HTTPException(status_code=404, detail="Gig not found")

@app.delete("/gigs/{gig_id}")
def delete_gig(gig_id: int):
    """Delete a gig"""
    global gigs_db
    for i, gig in enumerate(gigs_db):
        if gig.id == gig_id:
            gigs_db.pop(i)
            return {"message": f"Gig {gig_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Gig not found")  
