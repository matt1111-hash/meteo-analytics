# Root Cause Report: Jules

## Investigation Summary
I traced the call chain for weather data fetching from the frontend all the way to the infrastructure layer to uncover architectural issues. The project uses Clean Architecture principles. However, there is a major issue with how the `WeatherClient` is initialized and managed. Specifically, there is a duplicated initialization path leading to multiple independent instances (singletons) of the weather client, which inherently breaks tracking of the "active provider".

### Call Chain
1. **Frontend Request Initiation**: `ControlPanel.analysis_requested` emits a signal which calls `AppController.handle_analysis_request`.
2. **Analysis Handler**: The request goes to `AnalysisHandler.handle_analysis_request`, which prepares the request and starts the worker `start_analysis_callback` (`AnalysisWorker.start_analysis`).
3. **Analysis Worker Initialization**: Inside `AnalysisWorker.start_analysis`, the component initializer `ComponentInitializer.initialize` is called.
4. **Dependency Injection**: The `ComponentInitializer._init_weather_client` method fetches the weather client port using the factory function `src.infrastructure.container.get_weather_client_port()`.

### The Problem
If we look at the DI container factory `src/infrastructure/container/factories.py`:

```python
def get_weather_client_port() -> "WeatherClientPort":
    from src.data.weather_client_extensions import WeatherClientExtensions
    return WeatherClientExtensions()
```

Every time `get_weather_client_port()` is called, it instantiates a **new** `WeatherClientExtensions` object. This class inherits from `WeatherClient` (`src/data/weather_client_core.py`), which manages the `current_provider` state.

Therefore, every single background analysis worker spawned gets a brand new, completely fresh `WeatherClient` instance!

Meanwhile, there are multiple areas in the GUI codebase that also directly call `get_weather_client_port()`:
- `src/api/routes/analytics.py`
- `src/presentation/gui/trend_analytics/trend_data_processor/core.py`
- `src/analytics/multi_city_engine_core.py`
- `src/presentation/gui/workers/analysis_worker/component_initializer.py`

Since every factory call returns a **new instance**, the GUI components (which might try to update or read the "active provider" status via another instance) and the actual worker fetching the weather data are using completely different objects.

This parallel instantiation of the core data-fetching mechanism means that:
1. Any fallback or provider switch triggered inside the worker happens on an isolated instance.
2. Provider usage statistics (`provider_usage_stats`) are reset or maintained individually per instance.
3. The UI has no way of reading the actual state of the provider used by the worker because it probably looks at a different instance of the `WeatherClient`.

### Solution Outline
The architecture requires the `WeatherClient` to act as a singleton across the application's lifecycle, or the dependency injection container must be refactored to cache and return the same instance of the `WeatherClientPort` rather than instantiating a new one on every call to `get_weather_client_port()`.

File involved: `src/infrastructure/container/factories.py`
Action needed: Implement a caching mechanism (e.g., a module-level variable `_weather_client_instance`) to ensure `get_weather_client_port()` returns a singleton.
