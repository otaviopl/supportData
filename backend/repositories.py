import sqlite3
from datetime import datetime
from typing import Optional
from backend.db import get_db
from backend.models import (
    TicketResponse,
    TicketUpdate,
    TicketStatus,
    TicketPriority,
    TicketChannel,
)


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def get_tickets(
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    channel: Optional[str] = None,
) -> tuple[list[TicketResponse], int]:
    with get_db() as conn:
        cursor = conn.cursor()
        where_clauses = []
        params = []
        
        if q:
            where_clauses.append("(subject LIKE ? OR customer_name LIKE ?)")
            search_term = f"%{q}%"
            params.extend([search_term, search_term])
        
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        
        if priority:
            where_clauses.append("priority = ?")
            params.append(priority)
        
        if channel:
            where_clauses.append("channel = ?")
            params.append(channel)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        count_sql = f"SELECT COUNT(*) as total FROM tickets WHERE {where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT id, created_at, updated_at, customer_name, channel, 
                   subject, description, status, priority
            FROM tickets
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query_sql, params + [page_size, offset])
        rows = cursor.fetchall()
        tickets = [TicketResponse(**row_to_dict(row)) for row in rows]
        return tickets, total


def get_ticket_by_id(ticket_id: int) -> Optional[TicketResponse]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, created_at, updated_at, customer_name, channel,
                   subject, description, status, priority
            FROM tickets
            WHERE id = ?
        """, (ticket_id,))
        row = cursor.fetchone()
        if row:
            return TicketResponse(**row_to_dict(row))
        return None


def update_ticket(ticket_id: int, update_data: TicketUpdate) -> Optional[TicketResponse]:
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        return None
    
    with get_db() as conn:
        cursor = conn.cursor()
        updates = []
        params = []
        
        if update_data.status is not None:
            updates.append("status = ?")
            params.append(update_data.status.value)
        
        if update_data.priority is not None:
            updates.append("priority = ?")
            params.append(update_data.priority.value)
        
        if not updates:
            return ticket
        
        updates.append("updated_at = ?")
        now = datetime.utcnow().isoformat() + "Z"
        params.append(now)
        params.append(ticket_id)
        update_sql = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(update_sql, params)
        conn.commit()
        return get_ticket_by_id(ticket_id)


def create_ticket(
    created_at: str,
    customer_name: str,
    channel: str,
    subject: str,
    description: Optional[str],
    status: str,
    priority: str,
) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        updated_at = now
        cursor.execute("""
            INSERT INTO tickets 
            (created_at, updated_at, customer_name, channel, subject, description, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (created_at, updated_at, customer_name, channel, subject, description, status, priority))
        conn.commit()
        return cursor.lastrowid

