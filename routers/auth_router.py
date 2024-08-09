from datetime import datetime, timedelta, timezone
from pydantic import parse_obj_as
from services.email_service.email_sender import EmailSender
from services.email_service.message import Message
import bcrypt
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from services.token_service import generate_access_token, generate_refresh_token, get_password_hash, verify_password, validate_access_token, decode_token
from models.app_user import AppUser
from schemas.login_schema import LoginSchema
from schemas.token_schema import TokenModel
from schemas.response_model import ResponseModel
import os
import uuid
import random
from schemas.user_schema import UserCreateParameters, UserSchema
from schemas.confirm_email_schema import ConfirmEmailSchema
from schemas.send_code_schema import SendCodeSchema
from schemas.reset_password_schema import ChangePasswordSchema, ResetPasswordSchema
from services.email_service.email_sender import EmailSender
from core.dependencies import get_repository_wrapper
from repositories.repository_wrapper import RepositoryWrapper
from core.logger import get_logger
from core.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)
logger = get_logger()

@router.post("/login", name="Login", response_model=ResponseModel)
async def login(logged_user: LoginSchema,
                repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        user = await repositories.user.get_user_active_or_not(logged_user.login)
        if not user:
            logger.error(f"User {logged_user.login} not found")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=jsonable_encoder(ResponseModel(success=False, message= f"User {logged_user.login} not found"))
            )
        if not user.is_confirmed:
            logger.error(f"This account {logged_user.login} is not yet activated!")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=jsonable_encoder(
                    ResponseModel(
                        success=False, 
                        message= "This account is not yet activated!", 
                        data="account not activated"))
            )
        if not verify_password(logged_user.password, user.password):
            logger.error("Password is incorrect!")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=jsonable_encoder(
                    ResponseModel(success=False, message= "Password is incorrect!", 
                                    data="Password is incorrect"))
            )
        
        access_token = generate_access_token(data={"sub": logged_user.login})
        refresh_token = generate_refresh_token()
        user.refresh_token = refresh_token
        user.refresh_token_expiry_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await repositories.user.update(user)
        
        token_model = TokenModel(token=access_token, refresh_token=refresh_token)
        logger.info(f"Connection completed successfully!")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseModel(success=True, message="Connection completed successfully!", 
                                    data=token_model))
        )
    except Exception as ex:
        logger.error(f"Something went wrong inside Login action: {str(ex)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error"))
        )

@router.post("/register", response_model=ResponseModel)
async def register(user_create_parameters: UserCreateParameters,
                   repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    user = await repositories.user.get_user_by_email(user_create_parameters.email)
    if user:
        logger.error(f"The email : {user_create_parameters.email} already exists")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message=f"The email : {user_create_parameters.email} already exists"))
        )
    user = await repositories.user.get_user_by_user_name(user_create_parameters.user_name)
    if user:
        logger.error(f"The user name : {user_create_parameters.user_name} already exists")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message=f"The user name : {user_create_parameters.user_name} already exists"))
        )
    
    hashed_password = get_password_hash(user_create_parameters.password)
    folder = str(uuid.uuid4())
    activation_code = random.randint(100000, 999999)
    
    user_to_save = AppUser(
        name=user_create_parameters.name,
        email=user_create_parameters.email,
        user_name=user_create_parameters.user_name,
        country_id=user_create_parameters.country_id,
        password=hashed_password,
        folder=folder,
        photo="assets/images/profil.png",
        code_confirmation=str(activation_code),
        code_confirmation_date=datetime.now(timezone.utc) + timedelta(days=3),
        created_at=datetime.now(timezone.utc)
    )
    user_created = await repositories.user.create_user(user_to_save)
    user = await repositories.user.get_user_by_id(user_created.id)
    
    # send email
    email_sender = EmailSender()
    message = Message(
        to=[user_create_parameters.email],
        subject="Account Activation",
        content=f"<h2>{activation_code}</h2>: Please use this code to activate your account."
    )
    email_sender.send_email(message)
    
    os.makedirs(f"assets/post/{folder}/image", exist_ok=True)

    response = jsonable_encoder(ResponseModel(
        success=True,
        message="A confirmation code has been sent to you by email. Please check your email to activate your account!",
        data=UserSchema.from_orm(user)
    ))
    return response

@router.post("/confirmEmail", response_model=ResponseModel)
async def confirm_email(confirm_email_schema: ConfirmEmailSchema,
                        repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    if confirm_email_schema is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(ResponseModel(success=False, message="Please fill in the email and code!"))
        )

    if confirm_email_schema.email is None or confirm_email_schema.code is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(ResponseModel(success=False, message="Please fill in the email and code!"))
        )
    user = await repositories.user.get_user_active_or_not(confirm_email_schema.email)
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message=f"The email {confirm_email_schema.email} does not exist!"))
        )
    if user.is_confirmed:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseModel(
            success=False, 
            message="Your account has already been confirmed. You can log in."))
        )

    if confirm_email_schema.code != user.code_confirmation:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(success=False, message="The code entered is not correct!"))
        )
    if user.code_confirmation_date.tzinfo is None:
        user.code_confirmation_date = user.code_confirmation_date.replace(tzinfo=timezone.utc)
    if user.code_confirmation_date < datetime.now(timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message="The code has expired. Please resend another confirmation code request!"))
        )
    
    user.is_confirmed = True
    user.is_active = True
    await repositories.user.update_user(user)
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseModel(
                success=True, 
                message="Your email has been successfully confirmed.!", data=confirm_email_schema.email))
    )

@router.post("/sendCode", response_model=ResponseModel)
async def send_code(send_code_schema: SendCodeSchema, 
                    repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    send_code_schema = jsonable_encoder(send_code_schema)
    if send_code_schema is None or not send_code_schema['email']:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Please fill in the email!"))
        )

    user = await repositories.user.get_user_active_or_not(send_code_schema['email'])
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message=f"Email {send_code_schema['email']} does not exist.")
            )
        )

    if send_code_schema['reason'] == "registration" and user.is_confirmed:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message="Your account has already been confirmed. You can log in."))
        )

    if send_code_schema['reason'] == "reset" and not user.is_confirmed:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, message="This account is not yet confirmed."))
        )

    activation_code = random.randint(100000, 999999)
    user.code_confirmation = str(activation_code)
    user.code_confirmation_date = datetime.now(timezone.utc) + timedelta(days=3)
    await repositories.user.update_user(user)

    # send email
    email_sender = EmailSender()
    message = Message(
        to=[user.email],
        subject="Account Activation",
        content=f"<h2>{activation_code}</h2>: Please use this code to activate your account."
    )
    email_sender.send_email(message)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(
            success=True, 
            message="Confirmation code returned successfully!", 
            data=send_code_schema['email']))
    )

@router.post("/confirmCode", response_model=ResponseModel)
async def confirm_code(confirm_email_schema: ConfirmEmailSchema, 
                       repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    if confirm_email_schema is None or not confirm_email_schema.email or not confirm_email_schema.code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Please fill in the email and code!"))
        )
    user = await repositories.user.get_user_by_email(confirm_email_schema.email)
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message=f"Email {confirm_email_schema.email} does not exist!"))
        )

    if confirm_email_schema.code != user.code_confirmation:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ResponseModel(success=False, message="The code entered is not correct!"))
        )
    if user.code_confirmation_date.tzinfo is None:
        user.code_confirmation_date = user.code_confirmation_date.replace(tzinfo=timezone.utc)
    if user.code_confirmation_date < datetime.now(timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message="The code has expired. Please resend another confirmation code request!"))
        )

    token = generate_access_token(data={"sub": confirm_email_schema.email})
    user.remember_token = token
    await repositories.user.update_user(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(
            success=True, message="Verification completed successfully.", data=token))
    )

@router.post("/resetPassword", response_model=ResponseModel)
async def reset_password(reset_password_schema: ResetPasswordSchema,
                         repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    reset_password_schema = jsonable_encoder(reset_password_schema)
    reset_password_schema = parse_obj_as(ResetPasswordSchema, reset_password_schema)
    if reset_password_schema is None or not reset_password_schema.token:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(ResponseModel(success=False, message="Please fill in the token!"))
        )
    
    token_valid = validate_access_token(reset_password_schema.token)
    if not token_valid:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(
                success=False, 
                message="The reset time has passed. Please resume the process!"))
        )

    email = decode_token(reset_password_schema.token).get("sub")
    user = await repositories.user.get_user_by_email(email)
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Email {email} does not exist!"))
        )

    hashed_password = bcrypt.hashpw(reset_password_schema.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    await repositories.user.update_user(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(success=True, message="Password has been reset successfully."))
    )

@router.post("/changePassword", response_model=ResponseModel)
async def change_password(change_password_schema: ChangePasswordSchema,
                         repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    change_password_schema = jsonable_encoder(change_password_schema)
    change_password_schema = parse_obj_as(ChangePasswordSchema, change_password_schema)
    if change_password_schema is None or not change_password_schema.email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(ResponseModel(success=False, message="Please fill in the email!"))
        )

    user = await repositories.user.get_user_by_email(change_password_schema.email)
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Email {change_password_schema.email} does not exist!"))
        )

    if not bcrypt.checkpw(change_password_schema.old_password.encode('utf-8'), user.password.encode('utf-8')):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(ResponseModel(success=False, message="The old password is not correct"))
        )

    hashed_password = bcrypt.hashpw(change_password_schema.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    await repositories.user.update_user(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(success=True, message="Password has been reset successfully."))
    )

@router.get("/user", response_model=ResponseModel)
async def get_logged_user(request: Request, repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    token_with_bearer = request.headers.get("Authorization")
    if not token_with_bearer:
        return jsonable_encoder(JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Please login!"))
        ))

    token = token_with_bearer.replace("Bearer ", "")
    email = decode_token(token).get("sub")
    user = await repositories.user.get_user_by_email(email)
    if user is None:
        return jsonable_encoder(JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(ResponseModel(success=False, message="This user does not exist!"))
        ))

    user_result = UserSchema.from_orm(user)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(success=True, data=user_result))
    )
