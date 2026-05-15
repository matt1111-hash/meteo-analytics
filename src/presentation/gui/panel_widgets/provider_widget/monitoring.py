#!/usr/bin/env python3
# mypy: ignore-errors

"""
Provider Widget - Monitoring

📊 Usage monitoring és display frissítés

Képességek:
- Usage display frissítés
- Valós usage adat betöltés
- Warning ellenőrzés
- Details display frissítés

Fájl: src/presentation/gui/panel_widgets/provider_widget/monitoring.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def _update_usage_display(self) -> None:
    """
    🔧 CRITICAL: Usage display frissítése - OPEN-METEO OPTIMALIZÁLT!

    Args:
        self: ProviderWidget instance
    """
    try:
        if not self.usage_stats:
            _load_usage_stats(self)

        current_provider_stats = self.usage_stats.get(self.current_provider, {})

        if self.current_provider == "open-meteo":
            # 🌍 OPEN-METEO: Ingyenes, korlátlan - POZITÍV MEGJELENÍTÉS
            self.usage_progress.setValue(0)
            self.usage_label.setText("🌍 Ingyenes - Korlátlan használat ⭐")
            self.cost_label.setText("💰 Költség: $0.00/hó (INGYENES)")

            # Green progress bar for Open-Meteo
            self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #10b981; }")

        elif self.current_provider == "auto":
            # Auto routing - mixed stats
            total_requests = sum(stats.get("requests", 0) for stats in self.usage_stats.values())
            self.usage_progress.setValue(min(total_requests // 100, 100))  # Scale for display
            self.usage_label.setText(f"🤖 Összesen: {total_requests:,} kérés")

            total_cost = sum(stats.get("estimated_cost", 0) for stats in self.usage_stats.values())
            self.cost_label.setText(f"💰 Becsült költség: ${total_cost:.2f}/hó")

        else:
            # Premium provider stats
            requests = current_provider_stats.get("requests", 0)
            limit = current_provider_stats.get("limit", 10000)
            usage_percent = min((requests / limit) * 100, 100) if limit > 0 else 0

            self.usage_progress.setValue(int(usage_percent))
            self.usage_label.setText(f"💎 {requests:,}/{limit:,} kérés ({usage_percent:.1f}%)")

            estimated_cost = current_provider_stats.get("estimated_cost", 0)
            self.cost_label.setText(f"💰 Becsült költség: ${estimated_cost:.2f}/hó")

            # Warning checks
            _check_usage_warnings(self, usage_percent, estimated_cost)

        # Update details
        _update_details_display(self)

    except Exception as e:
        print(f"❌ DEBUG: Usage display update error: {e}")
        # Fallback display - OPEN-METEO alapértelmezett
        self.usage_label.setText("🌍 Open-Meteo - Ingyenes")
        self.cost_label.setText("💰 Költség: $0.00/hó")


def _load_usage_stats(self) -> None:
    """
    Usage adatok betöltése a perzisztált UsageTracker állapotból.

    Args:
        self: ProviderWidget instance
    """
    try:
        from src.config import APIConfig, build_usage_tracker  # noqa: PLC0415

        tracker = build_usage_tracker()
        summary = tracker.get_usage_summary()
        self.usage_stats = {
            "open-meteo": {
                "requests": summary.get("openmeteo_requests", 0),
                "limit": None,
                "estimated_cost": 0.0,
            },
            "meteostat": {
                "requests": summary.get("meteostat_requests", 0),
                "limit": summary.get("meteostat_limit", APIConfig.METEOSTAT_MONTHLY_LIMIT_RATE),
                "estimated_cost": summary.get("meteostat_cost", 0.0),
            },
        }
    except Exception as exc:
        print(f"❌ DEBUG: Usage stats load error: {exc}")
        self.usage_stats = {
            "open-meteo": {"requests": 0, "limit": None, "estimated_cost": 0.0},
            "meteostat": {"requests": 0, "limit": 10000, "estimated_cost": 0.0},
        }


def _check_usage_warnings(self, usage_percent: float, estimated_cost: float) -> None:
    """
    Usage warning ellenőrzések.

    Args:
        self: ProviderWidget instance
        usage_percent: Usage százalék
        estimated_cost: Becsült költség
    """
    # Usage warnings
    if usage_percent >= self.warning_thresholds["usage_critical"]:
        self.usage_warning.emit(self.current_provider, int(usage_percent))
        self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #dc2626; }")
    elif usage_percent >= self.warning_thresholds["usage_warning"]:
        self.usage_warning.emit(self.current_provider, int(usage_percent))
        self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #f59e0b; }")
    else:
        self.usage_progress.setStyleSheet("")  # Default styling

    # Cost warnings
    if estimated_cost >= self.warning_thresholds["cost_warning"]:
        self.cost_warning.emit(self.current_provider, estimated_cost)


def _update_details_display(self) -> None:
    """
    Details display frissítése - OPEN-METEO KIEMELÉS.

    Args:
        self: ProviderWidget instance
    """
    details = []

    for provider, stats in self.usage_stats.items():
        requests = stats.get("requests", 0)
        cost = stats.get("estimated_cost", 0)

        if provider == "open-meteo":
            # 🌍 OPEN-METEO POZITÍV KIEMELÉS
            details.append(f"🌍 Open-Meteo: {requests:,} kérés (INGYENES) ⭐")
        else:
            details.append(f"💎 {provider.title()}: {requests:,} kérés (${cost:.2f})")

    if not details:
        # Alapértelmezett üzenet OPEN-METEO-val
        details = ["🌍 Open-Meteo: Ingyenes, korlátlan, megbízható ⭐"]

    self.details_text.setText("\n".join(details))


def _refresh_usage_stats(self) -> None:
    """
    Usage statisztikák frissítése.

    Args:
        self: ProviderWidget instance
    """
    print("🔄 DEBUG: Refreshing usage statistics...")

    _load_usage_stats(self)
    _update_usage_display(self)

    print("✅ DEBUG: Usage statistics refreshed")


def _reset_usage_stats(self) -> None:
    """
    Usage statisztikák resetelése.

    Args:
        self: ProviderWidget instance
    """
    print("🗑️ DEBUG: Resetting usage statistics...")

    self.usage_stats.clear()

    # OPEN-METEO alapértelmezett megjelenítés reset után
    if self.current_provider == "open-meteo":
        self.usage_progress.setValue(0)
        self.usage_label.setText("🌍 Ingyenes - Korlátlan használat")
        self.cost_label.setText("💰 Költség: $0.00/hó")
        self.details_text.setText("🌍 Open-Meteo: Ingyenes, korlátlan, megbízható ⭐")
    else:
        self.usage_progress.setValue(0)
        self.usage_label.setText("💎 0/10,000 kérés (0%)")
        self.cost_label.setText("💰 Becsült költség: $0.00/hó")
        self.details_text.setText("📊 Statisztikák törölve")

    print("✅ DEBUG: Usage statistics reset")
