#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ HTML Generator - Térkép legend HTML generátorok.

FÁJL: src/presentation/gui/map/html_generator.py
"""


def create_temperature_legend() -> str:
    """🌡️ Hőmérséklet specifikus legend HTML."""
    return """
    <div style="position: fixed;
                top: 80px; right: 20px; width: 200px; height: auto;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid grey; z-index:9999;
                font-size: 12px; padding: 10px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
    <h4 style="margin-top: 0; color: #2E4057;">🌡️ Hőmérséklet</h4>

    <div style="background: linear-gradient(to right, #0000FF, #00FFFF, #00FF00, #FFFF00, #FF8000, #FF0000);
                height: 15px; margin: 5px 0;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 10px;">
        <span>-20°C</span><span>+40°C</span>
    </div>

    <p style="margin-top: 10px; font-size: 10px;">
        <b>Színskála:</b> Kék (hideg) → Piros (meleg)<br>
        <b>Adatok:</b> Napi maximum hőmérséklet
    </p>
    </div>
    """


def create_wind_legend() -> str:
    """💨 Szél specifikus legend HTML."""
    return """
    <div style="position: fixed;
                top: 80px; right: 20px; width: 200px; height: auto;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid grey; z-index:9999;
                font-size: 12px; padding: 10px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
    <h4 style="margin-top: 0; color: #2E4057;">💨 Szélsebesség</h4>

    <div style="background: linear-gradient(to right, #F0FFF0, #90EE90, #32CD32, #228B22, #006400);
                height: 15px; margin: 5px 0;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 10px;">
        <span>0 km/h</span><span>60+ km/h</span>
    </div>

    <p style="margin-top: 10px; font-size: 10px;">
        <div>🟢 < 12 km/h - Enyhe szél</div>
        <div>🟡 12-20 km/h - Gyenge szél</div>
        <div>🟠 20-39 km/h - Mérsékelt szél</div>
        <div>🔴 > 50 km/h - Erős szél</div>
    </p>
    </div>
    """


def create_precipitation_legend() -> str:
    """🌧️ Csapadék specifikus legend HTML."""
    return """
    <div style="position: fixed;
                top: 80px; right: 20px; width: 200px; height: auto;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid grey; z-index:9999;
                font-size: 12px; padding: 10px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
    <h4 style="margin-top: 0; color: #2E4057;">🌧️ Csapadék</h4>

    <div style="background: linear-gradient(to right, #F0F8FF, #B3D9FF, #4D94FF, #0066CC, #003366);
                height: 15px; margin: 5px 0;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 10px;">
        <span>0 mm</span><span>50+ mm</span>
    </div>

    <p style="margin-top: 10px; font-size: 10px;">
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 10px; height: 10px; background: #E8F4FD; border-radius: 50%; margin-right: 5px;"></div>
            <span>< 1 mm</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 15px; height: 15px; background: #80D0FF; border-radius: 50%; margin-right: 5px;"></div>
            <span>5-10 mm</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: #0080FF; border-radius: 50%; margin-right: 5px;"></div>
            <span>> 25 mm</span>
        </div>
    </p>
    </div>
    """


def create_general_legend() -> str:
    """🌤️ Általános weather legend HTML."""
    return """
    <div style="position: fixed;
                top: 80px; right: 20px; width: 200px; height: auto;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid grey; z-index:9999;
                font-size: 12px; padding: 10px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
    <h4 style="margin-top: 0; color: #2E4057;">🌤️ Időjárási Overlay</h4>

    <p><b>🌡️ Hőmérséklet:</b></p>
    <div style="background: linear-gradient(to right, #0000FF, #00FFFF, #00FF00, #FFFF00, #FF8000, #FF0000);
                height: 15px; margin: 5px 0;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 10px;">
        <span>-20°C</span><span>+40°C</span>
    </div>

    <p style="margin-top: 15px;"><b>🌧️ Csapadék:</b></p>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <div style="width: 10px; height: 10px; background: #E8F4FD; border-radius: 50%; margin-right: 5px;"></div>
        <span style="font-size: 10px;">< 1 mm</span>
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <div style="width: 15px; height: 15px; background: #80D0FF; border-radius: 50%; margin-right: 5px;"></div>
        <span style="font-size: 10px;">5-10 mm</span>
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <div style="width: 20px; height: 20px; background: #0080FF; border-radius: 50%; margin-right: 5px;"></div>
        <span style="font-size: 10px;">> 25 mm</span>
    </div>

    <p style="margin-top: 15px;"><b>💨 Szél:</b></p>
    <div style="font-size: 10px;">
        <div>🟢 < 12 km/h - Enyhe</div>
        <div>🟡 12-20 km/h - Gyenge</div>
        <div>🟠 20-39 km/h - Mérsékelt</div>
        <div>🔴 > 50 km/h - Erős</div>
    </div>
    </div>
    """


# Export
__all__ = [
    "create_general_legend",
    "create_precipitation_legend",
    "create_temperature_legend",
    "create_wind_legend",
]
