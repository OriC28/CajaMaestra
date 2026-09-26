from backend.app.models import DailyRate, Sale, Pay
from backend.app.schemas import SaleCreate, DailyReport, History

from sqlalchemy.sql.functions import coalesce
from datetime import datetime, date, time
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import func, select
from backend.app.database import session


def create_daily_rate_in_db(rate: float):
    today = datetime.now().date()

    daily_rate = session.query(DailyRate).filter(
        func.date(DailyRate.date) == today).first()

    if daily_rate:
        daily_rate.rate = rate

    else:
        daily_rate = DailyRate(date=datetime.now(), rate=rate)
        session.add(daily_rate)

    session.commit()
    session.refresh(daily_rate)
    return daily_rate


def create_sale_in_db(total_usd: float, rate_used: float):
    date_hour: str = datetime.now().isoformat()
    sale = Sale(date_hour=date_hour,
                total_usd=total_usd, rate_used=rate_used)

    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale


def create_complete_sale_in_db(sale_create: SaleCreate, rate_object: DailyRate):
    try:
        sale = Sale(date_hour=datetime.now(),
                    total_usd=sale_create.total_usd,
                    rate_used=rate_object.rate)
        session.add(sale)

        for payment_in in sale_create.payments:
            equivalent_usd_amount = 0.0

            if payment_in.method in ['zelle', "usd_efectivo", "binance_pay"]:
                equivalent_usd_amount = payment_in.native_amount

            elif payment_in.method in ['pago_movil', 'punto_venta', 'bs_efectivo']:
                if rate_object.rate > 0:
                    equivalent_usd_amount = payment_in.native_amount / rate_object.rate
                else:
                    raise ValueError("La tasa de cambio no puede ser cero.")
            else:
                raise ValueError(
                    f"Método de pago '{payment_in.method}' no reconocido.")

            db_payment = Pay(
                method=payment_in.method,
                native_amount=payment_in.native_amount,
                equivalent_usd_amount=round(
                    equivalent_usd_amount, 2)
            )

            db_payment.sale = sale
            session.add(db_payment)

        session.commit()
        session.refresh(sale)

        return sale

    except Exception as e:
        session.rollback()
        raise e


def get_daily_rate_from_db():
    return session.query(DailyRate).order_by(DailyRate.date.desc()).first()


def get_sale_from_db():
    return session.query(Sale).order_by(Sale.date_hour.desc()).first()


def get_daily_report_from_db():
    today_date = date.today()
    start_date = datetime.combine(today_date, time.min)
    end_date = datetime.combine(today_date, time.max)

    totals = {
        'total_sale_usd': 0.0,
        'sale_count': 0,
        'total_zelle': 0.0,
        'total_usd': 0.0,
        'total_binance_pay': 0.0,
        'total_bs': 0.0,
        'total_bs_efectivo': 0.0,
        'total_mobile_payment_bs': 0.0,
        'total_point_of_sale_bs': 0.0
    }

    statement = (
        select(Sale)
        .where(Sale.date_hour >= start_date, Sale.date_hour <= end_date)
        .options(selectinload(Sale.payments)))

    sales_today = session.execute(statement).scalars().unique().all()

    totals['sale_count'] = len(sales_today)
    for sale in sales_today:
        totals['total_sale_usd'] += sale.total_usd
        totals['total_bs'] += sale.total_usd * sale.rate_used
        for payment in sale.payments:
            if payment.method == 'zelle':
                totals['total_zelle'] += payment.equivalent_usd_amount
            elif payment.method == 'usd_efectivo':
                totals['total_usd'] += payment.equivalent_usd_amount
            elif payment.method == 'binance_pay':
                totals['total_binance_pay'] += payment.equivalent_usd_amount
            elif payment.method == 'bs_efectivo':
                totals['total_bs_efectivo'] += round(payment.native_amount)
            elif payment.method == 'pago_movil':
                totals['total_mobile_payment_bs'] += round(
                    payment.native_amount, 2)
            elif payment.method == 'punto_venta':
                totals['total_point_of_sale_bs'] += round(
                    payment.native_amount, 2)

    return DailyReport(**totals)


def get_history_from_db() -> list[History]:

    SaleOuter = aliased(Sale)

    subquery_rate = (
        select(Sale.rate_used)
        .where(func.date(Sale.date_hour) == func.date(SaleOuter.date_hour))
        .order_by(Sale.date_hour.desc())
        .limit(1)
        .scalar_subquery()
    )

    statement = (
        select(
            func.date(SaleOuter.date_hour).label('date'),

            coalesce(func.min(SaleOuter.date_hour),
                     datetime.now()).label('first_sale_date'),

            coalesce(func.max(SaleOuter.date_hour),
                     datetime.now()).label('last_sale_date'),

            func.count(SaleOuter.id).label('total_sales'),

            coalesce(func.sum(SaleOuter.total_usd), 0.0).label('total_amount'),

            coalesce(subquery_rate, 0.0).label('last_rate_used')
        )
        .group_by(func.date(SaleOuter.date_hour))
        .order_by(func.date(SaleOuter.date_hour).desc())
    )

    results = session.execute(statement).mappings().all()
    history = [History.model_validate(row) for row in results]

    return history
