from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
import io
import uuid

from app.database.connection import get_db
from app.database.models import User, Document, AuditLog
from app.api import schemas
from app.security import auth
from app.excel.generator import generate_bank_excel

router = APIRouter()

@router.post("/")
def export_document_to_excel(
    payload: schemas.ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """
    Takes reviewed/edited bank statement data and generates the binary styled 
    Microsoft Excel worksheet stream.
    """
    # 1. Fetch document and verify ownership
    doc = db.query(Document).filter(
        Document.id == payload.document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # 2. Build the Excel binary
    try:
        excel_bytes = generate_bank_excel(payload.edited_data)
        
        # Audit logging
        log_entry = AuditLog(
            user_id=current_user.id,
            action="export_excel",
            details=f"Exported '{doc.filename}' transactions spreadsheet to Excel"
        )
        db.add(log_entry)
        db.commit()
        
        # Prepare streaming response
        file_stream = io.BytesIO(excel_bytes)
        safe_name = doc.filename.rsplit(".", 1)[0] + ".xlsx"
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={safe_name}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Spreadsheet generation failed: {str(e)}"
        )
