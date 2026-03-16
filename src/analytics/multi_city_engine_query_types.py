"""Query type definitions for the multi-city engine."""

from __future__ import annotations

from src.domain.value_objects.enums import AnalyticsMetric

QUERY_TYPES = {
    "hottest_today": {
        "name": "Legmelegebb ma",
        "metric": "temperature_2m_max",
        "unit": "°C",
        "sort_desc": True,
        "question_template": "Hol volt ma a legmelegebb {region}ban?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MAX,
    },
    "coldest_today": {
        "name": "Leghidegebb ma",
        "metric": "temperature_2m_min",
        "unit": "°C",
        "sort_desc": False,
        "question_template": "Hol volt ma a leghidegebb {region}ban?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MIN,
    },
    "temperature_mean": {
        "name": "Átlag hőmérséklet",
        "metric": "temperature_2m_mean",
        "unit": "°C",
        "sort_desc": True,
        "question_template": "Hol volt ma a legmagasabb átlaghőmérséklet {region}ban?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_2M_MEAN,
    },
    "wettest_today": {
        "name": "Legcsapadékosabb ma",
        "metric": "precipitation_sum",
        "unit": "mm",
        "sort_desc": True,
        "question_template": "Hol esett ma a legtöbb csapadék {region}ban?",
        "metric_enum": AnalyticsMetric.PRECIPITATION_SUM,
    },
    "windiest_today": {
        "name": "Legszelesebb ma",
        "metric": "windspeed_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb szél {region}ban?",
        "metric_enum": AnalyticsMetric.WINDSPEED_10M_MAX,
    },
    "wind_gusts": {
        "name": "Legerősebb széllökés",
        "metric": "windgusts_10m_max",
        "unit": "km/h",
        "sort_desc": True,
        "question_template": "Hol fújt ma a legerősebb széllökés {region}ban?",
        "metric_enum": AnalyticsMetric.WINDGUSTS_10M_MAX,
    },
    "temperature_range": {
        "name": "Legnagyobb hőingás",
        "metric": "temperature_range",
        "unit": "°C",
        "sort_desc": True,
        "question_template": "Hol volt ma a legnagyobb hőingás {region}ban?",
        "metric_enum": AnalyticsMetric.TEMPERATURE_RANGE,
    },
}
