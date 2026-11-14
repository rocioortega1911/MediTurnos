from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.models.models import UsuarioModel
from app.schemas.schemas import UsuarioCreate, UsuarioResponse, Token
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Autenticación y Seguridad (JWT)"])

# 1. Registrar un nuevo usuario (guarda hashed_password en la tabla usuarios)
@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioModel).where(
            or_(
                UsuarioModel.username == usuario.username,
                UsuarioModel.email == usuario.email
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username o email ya está registrado"
        )

    nuevo_usuario = UsuarioModel(
        username=usuario.username,
        email=usuario.email,
        hashed_password=get_password_hash(usuario.password),
        rol=usuario.rol,
        activo=True
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario

# 2. Login de usuario (Devuelve el JSON Web Token)
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Permite loguearse tanto con username como con email
    result = await db.execute(
        select(UsuarioModel).where(
            or_(
                UsuarioModel.username == form_data.username,
                UsuarioModel.email == form_data.username
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de usuario está desactivada"
        )

    # Generar el token incluyendo sub (username), id y rol en el payload
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "rol": user.rol}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": user.rol,
        "username": user.username
    }

# 3. Verificar sesión activa a partir del JWT enviado en el header Authorization
@router.get("/me", response_model=UsuarioResponse)
async def obtener_perfil_actual(current_user: UsuarioModel = Depends(get_current_user)):
    return current_user