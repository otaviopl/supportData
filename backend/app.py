import json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.seed import load_seed_data
from backend.models import (
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
    TicketUpdateResponse,
    TicketStatus,
    TicketPriority,
    TicketChannel,
)
from backend.repositories import get_tickets, get_ticket_by_id, update_ticket

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_seed_data()
    yield

app = FastAPI(
    title="Support Ticket API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Support Ticket API",
        "version": "1.0.0",
        "endpoints": ["GET /tickets", "PATCH /tickets/{id}", "GET /metrics"]
    }


@app.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None),
    status: Optional[TicketStatus] = Query(None),
    priority: Optional[TicketPriority] = Query(None),
    channel: Optional[TicketChannel] = Query(None),
):
    tickets, total = get_tickets(
        page=page,
        page_size=page_size,
        q=q,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        channel=channel.value if channel else None,
    )
    
    return TicketListResponse(
        items=tickets,
        page=page,
        page_size=page_size,
        total=total,
    )


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=TicketUpdateResponse)
async def patch_ticket(ticket_id: int, update_data: TicketUpdate):
    if update_data.status is None and update_data.priority is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (status or priority) must be provided"
        )
    
    updated_ticket = update_ticket(ticket_id, update_data)
    if not updated_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    return TicketUpdateResponse(
        id=updated_ticket.id,
        status=updated_ticket.status,
        priority=updated_ticket.priority,
        updated_at=updated_ticket.updated_at,
    )


@app.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    metrics_file = Path(__file__).parent.parent / "data" / "processed" / "metrics.json"
    
    if not metrics_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Métricas não encontradas. Execute: python data/etl_support.py"
        )
    
    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    
    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

