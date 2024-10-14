from fastapi import APIRouter

router = APIRouter()


@router.get('login-history/{user_id}')
def get_login_history():
    pass
