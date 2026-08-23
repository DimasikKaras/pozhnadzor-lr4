from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import Inspector
from ..schemas import InspectorOut

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=InspectorOut)
def me(current_user: Inspector = Depends(get_current_user)):
    return current_user
