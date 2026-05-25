from datetime import date, timedelta


def get_week_start(d: date) -> date:
    """
    Devuelve el miércoles que inicia la semana que contiene la fecha dada.
    Las semanas van de miércoles a martes.
    """
    # weekday(): lunes=0, martes=1, miércoles=2, ...
    days_since_wednesday = (d.weekday() - 2) % 7
    return d - timedelta(days=days_since_wednesday)


def get_week_end(week_start: date) -> date:
    """Devuelve el martes que cierra la semana (week_start + 6 días)."""
    return week_start + timedelta(days=6)


def get_payment_date(week_start: date) -> date:
    """
    El pago es el viernes de la semana siguiente (week_start + 9 días).
    Ejemplo: semana inicia el mié 20/may → pago el vie 29/may.
    """
    return week_start + timedelta(days=9)
