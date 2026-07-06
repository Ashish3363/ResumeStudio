"""
app/main.py
===========

Composition root for the ResumeStudio API. Creates the FastAPI app, applies
cross-cutting setup (CORS, lifespan, exception handlers), and mounts each
feature router. A feature only becomes reachable once its router is included
here.
"""


from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.shared.exceptions import register_exception_handlers

@asynccontextmanager  # manage resources that need to be created when the application starts and cleaned up when it shuts down
async def lifespan(app: FastAPI):
    #---startup-----#
    #(optional) verify DB connectiviity, warm the AI client, etc .
    yield
    #----shutdown----#
    #dispose the SQL Alchemy engine/ close external client here
    
app=FastAPI(
    title="ResumeStudio API",
    version="0.1.0",
    lifespan=lifespan,
)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, #eg-["http://localhost:5173", "https://yourapp.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

# Turn typed AppErrors (InvalidToken, EmailAlreadyExists, ...) into structured
# JSON responses. Must be registered before requests are served.
register_exception_handlers(app)


@app.get("/health", tags=["meta"])
def health():
    return{"status":"ok"}


# --- Routers: uncomment each line as you build that module ---
from app.auth.router import router as auth_router
# from app.users.router import router as users_router
# from app.jd.router import router as jd_router
# from app.matching.router import router as matching_router
# from app.generator.router import router as generator_router
# from app.resumes.router import router as resumes_router

app.include_router(auth_router,       prefix="/api/auth",     tags=["auth"])
# app.include_router(users_router,      prefix="/api",          tags=["profile"])
# app.include_router(jd_router,         prefix="/api/jd",       tags=["jd"])
# app.include_router(matching_router,   prefix="/api",          tags=["matching"])
# app.include_router(generator_router,  prefix="/api",          tags=["generator"])
# app.include_router(resumes_router,    prefix="/api/resumes",  tags=["resumes"])