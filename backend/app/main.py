from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, products, sales, refunds, customers, suppliers, dashboard

# Creates tables on startup if they don't exist yet. Fine for this project's
# scale; a bigger app would use Alembic migrations instead so schema changes
# are tracked and reversible.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Boutique Manager Cloud API")

# Wide open for now since the app is used from a phone app / web app you
# control, not embedded on third-party sites. Tighten allow_origins to your
# actual app's domain once you have one, if you want to be stricter.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(refunds.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(dashboard.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "boutique-manager-cloud-api"}
