from backend.app.schemas import SaleCreate, RateCreate
import uvicorn

from backend.app.crud import *

from fastapi import FastAPI, APIRouter, HTTPException

app = FastAPI()


router = APIRouter(responses={404: {"message": "No encontrado."}})


@app.post("/rate")
def post_rate(rate_create: RateCreate):
    if rate_create.rate <= 0:
        raise HTTPException(
            status_code=400, detail="La tasa de cambio debe ser mayor a 0.")

    return create_daily_rate_in_db(rate_create.rate)


@app.get("/rate/today")
def get_today_rate():
    today_rate = get_daily_rate_from_db()
    if not today_rate:
        raise HTTPException(
            status_code=404, detail="No se ha definido la tasa de cambio para hoy.")
    return today_rate


@app.post("/sales")
def post_sale(sale_create: SaleCreate):
    today_rate = get_daily_rate_from_db()

    if not today_rate:
        raise HTTPException(
            status_code=404, detail="No se ha definido la tasa de cambio para hoy.")

    try:
        sale = create_complete_sale_in_db(
            sale_create=sale_create,
            rate_object=today_rate
        )

        return sale

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Error al procesar la venta: {e}")


@app.get("/report/today")
def get_report():
    report = get_daily_report_from_db()
    if not report:
        raise HTTPException(
            status_code=404, detail="El reporte de hoy no se encuentra disponible.")
    return report


@app.get('/history')
def get_history():
    history = get_history_from_db()
    if not history:
        raise HTTPException(
            status_code=404, detail="El historial no se encuentra disponible.")
    return history


app.include_router(router)


def run_fastapi():
    """Ejecuta el servidor FastAPI en un hilo separado."""
    import logging
    logging.getLogger("uvicorn").setLevel(logging.ERROR)
    config = uvicorn.Config(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="error",
        access_log=False
    )
    server = uvicorn.Server(config)
    server.run()
