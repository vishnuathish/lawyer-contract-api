from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from bson import ObjectId
try:
    from ..config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
    from ..service.document_parser import extract_text
    from ..models import Contact
    from ..database import contracts_collection
except ImportError:
    from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
    from service.document_parser import extract_text
    from models import Contact
    from database import contracts_collection
import uuid 

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a contract file (PDF or TXT) for analysis.
    """
    # Implement the logic to handle file upload and save it to the database

    ext = os.path.splitext(file.filename)[1].lower() 

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only" \
        " PDF and TXT files are allowed.")

    content = await file.read()

    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of {MAX_FILE_SIZE_MB}MB.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True) 
    unique_name = f"{uuid.uuid4().hex}{ext}"

    file_path = os.path.join(UPLOAD_DIR, unique_name) 

    with open(file_path, 'wb') as f:
        f.write(content)

    try:
        parsed = extract_text(file_path)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to process the uploaded PDF: {exc}",
        ) from exc

    contract_data = Contact(
        contract_id=uuid.uuid4().hex,
        filename=unique_name,
        original_name=file.filename,
        text_content=parsed['text'] if isinstance(parsed, dict) else parsed,
        page_count=int(parsed['page_count']) if isinstance(parsed, dict) else 0,
        word_count=int(parsed['word_count']) if isinstance(parsed, dict) else len(parsed.split()),
    )

    doc = contract_data.model_dump() #Ensure the model is initialized properly
    result = contracts_collection.insert_one(doc)
    contract_data.id = str(result.inserted_id)

    return {
        "message": "File uploaded and processed successfully",
        "contract": contract_data.model_dump(),
        "id": contract_data.id
    }

    # return {"message": "Contract uploaded successfully."}

@router.get('/')
async def list_contracts():
    """
    List all the contracts
    """
    contracts = []
    for doc in contracts_collection.find({},{"text_content":0}):
        contract = Contact(**doc)
        contract.id = str(doc['_id'])
        contracts.append(contract.model_dump())
    return {'contracts': contracts}


@router.get('/{contract_id}')
async def get_contract_by_id(contract_id: str):
    """
    Get a single contract by its contract_id or MongoDB _id.
    """
    contract_doc = contracts_collection.find_one({"contract_id": contract_id})

    if contract_doc is None and ObjectId.is_valid(contract_id):
        contract_doc = contracts_collection.find_one({"_id": ObjectId(contract_id)})

    if contract_doc is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    contract = Contact(**contract_doc)
    contract.id = str(contract_doc["_id"])
    return {"contract": contract.model_dump()}

