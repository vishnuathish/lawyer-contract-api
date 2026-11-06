from fastapi import APIRouter, HTTPException
try:
    from ..config import GEMINI_API_KEY
    from ..database import contracts_collection, analysis_collection
    from ..service.gemini_analyze import analyze_contract
except ImportError:
    from config import GEMINI_API_KEY
    from database import contracts_collection, analysis_collection
    from service.gemini_analyze import analyze_contract
from bson import ObjectId
import uuid

router = APIRouter(
    prefix='/analysis',
    tags=['analysis']
)

@router.post('/analyse/{contract_id}')
@router.post('/analyze/{contract_id}')
async def analyse_contract(contract_id: str):
    """
    Analyze a contract using AI and return insights.
    """

    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail='AI API key is not configured')

    if ObjectId.is_valid(contract_id):
        contract = contracts_collection.find_one({
            "$or": [
                {"_id": ObjectId(contract_id)},
                {"contract_id": contract_id},
            ]
        })
    else:
        contract = contracts_collection.find_one({"contract_id": contract_id})

    if not contract:
        raise HTTPException(status_code=404, detail='Contract details not found')

    if not contract.get('text_content'):
        raise HTTPException(status_code=400, detail='Contract has no text content to analyze')

    contract_object_id = contract["_id"]
    stored_contract_id = contract.get("contract_id") or str(contract_object_id)

    contracts_collection.update_one(
        {"_id": contract_object_id},
        {"$set": {"analysis_status": "in_progress"}},
    )

    try:
        result = await analyze_contract(stored_contract_id, contract["text_content"])
    except Exception as exc:
        contracts_collection.update_one(
            {"_id": contract_object_id},
            {"$set": {"analysis_status": "failed"}},
        )
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {exc}",
        ) from exc

    result.analysis_id = uuid.uuid4().hex
    doc = result.model_dump()
    insert_result = analysis_collection.insert_one(doc)
    result.id = str(insert_result.inserted_id)

    contracts_collection.update_one(
        {"_id": contract_object_id},
        {"$set": {"analysis_status": "completed"}},
    )

    return {
        "message": "Contract analyzed successfully",
        "analysis": result.model_dump(),
        "id": result.id
    }