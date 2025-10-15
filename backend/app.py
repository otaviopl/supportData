import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.seed import load_seed_data
from backend.db import init_db
from backend.models import (
    TicketListResponse,
    TicketResponse,
    TicketCreate,
    TicketUpdate,
    TicketUpdateResponse,
    TicketStatus,
    TicketPriority,
    TicketChannel,
)
from backend.repositories import get_tickets, get_ticket_by_id, update_ticket, create_ticket
import urllib.request
import urllib.error
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_on_start = os.getenv("SEED_ON_START", "true").lower() == "true"
    if seed_on_start:
        load_seed_data()
    else:
        # Ensure DB schema exists even without seeding
        init_db()
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
async def patch_ticket(ticket_id: int, update_data: TicketUpdate, background_tasks: BackgroundTasks):
    if update_data.status is None and update_data.priority is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (status or priority) must be provided"
        )
    
    updated_ticket = update_ticket(ticket_id, update_data)
    if not updated_ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    response = TicketUpdateResponse(
        id=updated_ticket.id,
        status=updated_ticket.status,
        priority=updated_ticket.priority,
        updated_at=updated_ticket.updated_at,
    )
    # Trigger webhook if needed
    _maybe_enqueue_webhook(background_tasks, updated_ticket)
    return response


def _should_trigger_webhook(status: str, priority: str) -> bool:
    print(f"status: {status}, priority: {priority}")
    return status == TicketStatus.CLOSED.value or priority == TicketPriority.HIGH.value


def _post_webhook(url: str, payload: dict[str, Any]) -> None:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as e:
        print(f"⚠ Failed to POST webhook to {url}: {e}")


def _maybe_enqueue_webhook(background_tasks: BackgroundTasks, ticket: TicketResponse) -> None:
    url = os.getenv("n8n_webhook_url") or os.getenv("N8N_WEBHOOK_URL")
    if not url:
        print("⚠ N8N_WEBHOOK_URL not set; skipping webhook")
        return
    # Normalize possible Enum values to strings
    status_value = ticket.status.value if hasattr(ticket.status, "value") else ticket.status
    priority_value = ticket.priority.value if hasattr(ticket.priority, "value") else ticket.priority
    if _should_trigger_webhook(status_value, priority_value):
        payload = {
            "id": ticket.id,
            "status": status_value,
            "priority": priority_value,
            "customer_name": ticket.customer_name,
            "subject": ticket.subject,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }
        print(f"↗ Queuing webhook to {url}")
        background_tasks.add_task(_post_webhook, url, payload)
    else:
        print("ℹ Webhook not queued: condition not met")


@app.post("/tickets", response_model=TicketResponse, status_code=201)
async def post_ticket(new_ticket: TicketCreate, background_tasks: BackgroundTasks):
    # Ensure DB schema exists
    init_db()

    created_at = new_ticket.created_at or (Path(".") and "")
    # Generate ISO timestamp if not provided
    if not created_at:
        from datetime import datetime
        created_at = datetime.utcnow().isoformat() + "Z"

    ticket_id = create_ticket(
        created_at=created_at,
        customer_name=new_ticket.customer_name,
        channel=new_ticket.channel.value,
        subject=new_ticket.subject,
        description=new_ticket.description,
        status=new_ticket.status.value,
        priority=new_ticket.priority.value,
    )
    created = get_ticket_by_id(ticket_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create ticket")
    _maybe_enqueue_webhook(background_tasks, created)
    return created


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

