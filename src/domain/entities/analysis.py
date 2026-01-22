from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import date, datetime
from enum import Enum

# Temporary imports
from src.data.enums import RegionScope, AnalyticsMetric, QuestionType, DataSource, AnomalySeverity
from src.domain.entities.location import UniversalLocation, LocationType
from src.domain.entities.weather import CityWeatherResult, AnomalyResult

class TimeGranularity(Enum):
    """⏰ Időbeli granularitás - USER IDŐSZABADSÁG"""
    DAILY = "daily"                      # Napi szint
    WEEKLY = "weekly"                    # Heti szint
    MONTHLY = "monthly"                  # Havi szint
    YEARLY = "yearly"                    # Éves szint
    SEASONAL = "seasonal"                # Szezonális
    CUSTOM_INTERVAL = "custom_interval"  # User-definiált intervallum
    MULTI_YEAR = "multi_year"           # Évtizedes (1980-2024)


class AnalysisType(Enum):
    """🔬 Elemzési típusok - USER ANALYTICS SZABADSÁG"""
    CURRENT_CONDITIONS = "current_conditions"    # Jelenlegi állapot
    TREND_ANALYSIS = "trend_analysis"           # Trend elemzés
    ANOMALY_DETECTION = "anomaly_detection"     # Anomália detektálás
    COMPARATIVE = "comparative"                 # Összehasonlító elemzés
    STATISTICAL = "statistical"                # Statisztikai elemzés
    PATTERN_RECOGNITION = "pattern_recognition" # Minta felismerés
    FORECAST = "forecast"                      # Előrejelzés
    CUSTOM = "custom"                          # User-definiált elemzés

@dataclass
class UniversalTimeRange:
    """
    ⏰ Univerzális időtartomány modell - TELJES IDŐSZABADSÁG
    """
    start_date: date
    end_date: date
    granularity: TimeGranularity
    
    # Leíró információk
    description: str = ""
    
    # Speciális beállítások
    include_partial_periods: bool = True      # Részleges időszakok belefoglalása
    exclude_weekends: bool = False            # Hétvégék kizárása
    seasonal_filter: Optional[List[str]] = None # Szezonális szűrő ['summer', 'winter']
    
    # Metadata
    total_days: int = field(init=False)
    is_historical: bool = field(init=False)
    is_future: bool = field(init=False)
    
    def __post_init__(self):
        """Post-init számítások."""
        self.total_days = (self.end_date - self.start_date).days + 1
        today = date.today()
        self.is_historical = self.end_date < today
        self.is_future = self.start_date > today
        
        # Automatikus leírás generálás ha üres
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Automatikus leírás generálás."""
        if self.total_days == 1:
            return f"Egy nap ({self.start_date})"
        elif self.total_days <= 7:
            return f"{self.total_days} nap ({self.start_date} - {self.end_date})"
        elif self.total_days <= 31:
            return f"~{self.total_days // 7} hét ({self.start_date} - {self.end_date})"
        elif self.total_days <= 365:
            return f"~{self.total_days // 30} hónap ({self.start_date} - {self.end_date})"
        else:
            years = self.total_days // 365
            return f"~{years} év ({self.start_date} - {self.end_date})"
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.description} [{self.granularity.value}]"
    
    def overlaps_with(self, other: 'UniversalTimeRange') -> bool:
        """Átfed-e másik időtartománnyal."""
        return not (self.end_date < other.start_date or self.start_date > other.end_date)
    
    def contains_date(self, check_date: date) -> bool:
        """Tartalmazza-e a megadott dátumot."""
        return self.start_date <= check_date <= self.end_date
    
    def get_months_list(self) -> List[str]:
        """Érintett hónapok listája (YYYY-MM formátumban)."""
        months = []
        current = self.start_date.replace(day=1)  # Hónap eleje
        
        while current <= self.end_date:
            months.append(current.strftime('%Y-%m'))
            # Következő hónap
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    def get_years_list(self) -> List[int]:
        """Érintett évek listája."""
        return list(range(self.start_date.year, self.end_date.year + 1))
    
    def split_by_years(self) -> List['UniversalTimeRange']:
        """Évenkénti bontás."""
        if self.start_date.year == self.end_date.year:
            return [self]
        
        yearly_ranges = []
        for year in self.get_years_list():
            year_start = max(self.start_date, date(year, 1, 1))
            year_end = min(self.end_date, date(year, 12, 31))
            
            yearly_range = UniversalTimeRange(
                start_date=year_start,
                end_date=year_end,
                granularity=TimeGranularity.YEARLY,
                description=f"{year} év részlet"
            )
            yearly_ranges.append(yearly_range)
        
        return yearly_ranges
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'granularity': self.granularity.value,
            'description': self.description,
            'total_days': self.total_days,
            'is_historical': self.is_historical,
            'is_future': self.is_future,
            'include_partial_periods': self.include_partial_periods,
            'exclude_weekends': self.exclude_weekends,
            'seasonal_filter': self.seasonal_filter
        }

@dataclass
class UniversalQuery:
    """
    🎯 UNIVERZÁLIS LEKÉRDEZÉS MODELL - USER-CENTRIC PARADIGMA
    """
    # Alapvető query komponensek
    locations: List[UniversalLocation]
    time_range: UniversalTimeRange
    parameters: List[str]                   # Weather paraméterek (temperature_2m_max, stb.)
    analysis_type: AnalysisType
    
    # Query metaadatok
    query_id: str = field(default_factory=lambda: f"universal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    user_description: str = ""              # User-friendly leírás
    
    # Végrehajtási beállítások
    data_sources: List[DataSource] = field(default_factory=list)  # Preferred APIs
    quality_threshold: float = 0.8          # Minimum adat minőség
    max_results_per_location: int = 1000    # Performance limit
    
    # Szűrési opciók
    anomaly_detection: bool = False         # Anomália detektálás bekapcsolása
    statistical_analysis: bool = True       # Statisztikai elemzés
    trend_analysis: bool = False           # Trend elemzés
    comparative_mode: bool = False         # Összehasonlító mód
    
    # Anomália specifikus beállítások (ha anomaly_detection=True)
    anomaly_severity_filter: List[AnomalySeverity] = field(default_factory=list)
    anomaly_threshold_override: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Végrehajtási státusz
    is_executed: bool = False
    execution_time: Optional[float] = None
    total_data_points: int = 0
    
    def __post_init__(self):
        """Post-init validáció és automatikus beállítások."""
        # Automatikus leírás generálás ha üres
        if not self.user_description:
            self.user_description = self._generate_description()
        
        # Automatikus comparative mode detektálás
        if len(self.locations) > 1:
            self.comparative_mode = True
        
        # Data sources validáció
        if not self.data_sources:
            self.data_sources = [DataSource.AUTO]  # Default auto selection
    
    def _generate_description(self) -> str:
        """Automatikus user-friendly leírás generálás."""
        # Lokációk
        if len(self.locations) == 1:
            location_desc = self.locations[0].display_name
        elif len(self.locations) <= 3:
            location_desc = " vs ".join([loc.display_name for loc in self.locations])
        else:
            location_desc = f"{len(self.locations)} lokáció"
        
        # Paraméterek
        if len(self.parameters) == 1:
            param_desc = self.parameters[0].replace('_', ' ')
        elif len(self.parameters) <= 3:
            param_desc = ", ".join([p.replace('_', ' ') for p in self.parameters])
        else:
            param_desc = f"{len(self.parameters)} paraméter"
        
        # Időtartam
        time_desc = self.time_range.description
        
        # Elemzés típus
        analysis_desc = self.analysis_type.value.replace('_', ' ')
        
        return f"{location_desc}: {param_desc} {analysis_desc} ({time_desc})"
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"UniversalQuery[{self.query_id}]: {self.user_description}"
    
    def get_total_locations(self) -> int:
        """Összes lokáció száma (hierarchikus bontással)."""
        total = 0
        for location in self.locations:
            if location.type == LocationType.MULTIPLE:
                total += len(location.child_locations)
            else:
                total += 1
        return total
    
    def get_all_coordinates(self) -> List[Tuple[float, float]]:
        """Összes koordináta a query-ből."""
        all_coords = []
        for location in self.locations:
            all_coords.extend(location.get_coordinates_list())
        return all_coords
    
    def is_multi_location_query(self) -> bool:
        """Multi-lokáció query-e."""
        return len(self.locations) > 1 or any(
            loc.type == LocationType.MULTIPLE for loc in self.locations
        )
    
    def is_long_term_analysis(self) -> bool:
        """Hosszú távú elemzés-e (>1 év)."""
        return self.time_range.total_days > 365
    
    def is_historical_query(self) -> bool:
        """Historikus query-e."""
        return self.time_range.is_historical
    
    def get_estimated_complexity(self) -> str:
        """Becsült query komplexitás."""
        score = 0
        
        # Lokációk száma
        score += self.get_total_locations() * 2
        
        # Paraméterek száma
        score += len(self.parameters) * 3
        
        # Időtartam
        score += min(self.time_range.total_days // 30, 50)  # Max 50 pont
        
        # Elemzés típus bonyolultsága
        if self.analysis_type in [AnalysisType.TREND_ANALYSIS, AnalysisType.ANOMALY_DETECTION]:
            score += 20
        elif self.analysis_type in [AnalysisType.PATTERN_RECOGNITION, AnalysisType.FORECAST]:
            score += 30
        
        # Comparative mode
        if self.comparative_mode:
            score += 15
        
        # Kategorizálás
        if score < 20:
            return "simple"
        elif score < 50:
            return "medium"
        elif score < 100:
            return "complex"
        else:
            return "very_complex"
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Query validáció.
        
        Returns:
            (valid: bool, error_messages: List[str])
        """
        errors = []
        
        # Lokációk validáció
        if not self.locations:
            errors.append("Legalább egy lokáció megadása kötelező!")
        
        # Paraméterek validáció  
        if not self.parameters:
            errors.append("Legalább egy paraméter megadása kötelező!")
        
        # Időtartam validáció
        if self.time_range.start_date > self.time_range.end_date:
            errors.append("A kezdő dátum nem lehet későbbi a záró dátumnál!")
        
        # Performance validáció
        estimated_complexity = self.get_estimated_complexity()
        if estimated_complexity == "very_complex" and self.max_results_per_location < 100:
            errors.append("Nagyon komplex query esetén növelje a max_results_per_location értékét!")
        
        # Anomália beállítások validáció
        if self.anomaly_detection:
            if self.anomaly_threshold_override and self.anomaly_threshold_override <= 0:
                errors.append("Anomália küszöb pozitív szám kell legyen!")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'query_id': self.query_id,
            'user_description': self.user_description,
            'locations': [loc.to_dict() for loc in self.locations],
            'time_range': self.time_range.to_dict(),
            'parameters': self.parameters,
            'analysis_type': self.analysis_type.value,
            'data_sources': [ds.value for ds in self.data_sources],
            'quality_threshold': self.quality_threshold,
            'max_results_per_location': self.max_results_per_location,
            'anomaly_detection': self.anomaly_detection,
            'statistical_analysis': self.statistical_analysis,
            'trend_analysis': self.trend_analysis,
            'comparative_mode': self.comparative_mode,
            'estimated_complexity': self.get_estimated_complexity(),
            'total_locations': self.get_total_locations(),
            'is_multi_location': self.is_multi_location_query(),
            'is_long_term': self.is_long_term_analysis(),
            'is_historical': self.is_historical_query(),
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags
        }

@dataclass
class AnalyticsQuestion:
    """
    Analytics kérdés definíció.
    
    Multi-city analytics kérdések specifikációja.
    """
    question_text: str
    question_type: QuestionType
    region_scope: RegionScope
    metric: AnalyticsMetric
    
    # Query parameters
    region_value: Optional[str] = None      # Konkrét régió (pl. "HU", "Europe")
    date_filter: Optional[str] = None       # Dátum szűrő
    ascending_order: bool = False           # Rendezési irány
    max_cities: int = 50                    # Maximum városok száma
    
    # Additional filters
    min_population: Optional[int] = None    # Minimum népesség
    include_capitals_only: bool = False     # Csak fővárosok
    exclude_islands: bool = False           # Szigetek kizárása
    climate_zones: Optional[List[str]] = None # Éghajlati zónák
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return self.question_text
    
    def get_region_display(self) -> str:
        """Régió display név."""
        if self.region_value:
            return f"{self.region_scope.value}: {self.region_value}"
        return self.region_scope.value
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Kérdés validálása.
        
        Returns:
            (valid, error_messages)
        """
        errors = []
        
        if not self.question_text.strip():
            errors.append("Kérdés szövege nem lehet üres")
        
        if self.max_cities <= 0:
            errors.append("Maximum városok száma pozitív kell legyen")
        
        if self.max_cities > 1000:
            errors.append("Maximum városok száma nem lehet 1000-nél több")
        
        if self.region_scope in [RegionScope.COUNTRY, RegionScope.REGION] and not self.region_value:
            errors.append(f"{self.region_scope.value} scope esetén region_value kötelező")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'question_text': self.question_text,
            'question_type': self.question_type.value,
            'region_scope': self.region_scope.value,
            'metric': self.metric.value,
            'region_value': self.region_value,
            'date_filter': self.date_filter,
            'ascending_order': self.ascending_order,
            'max_cities': self.max_cities,
            'min_population': self.min_population,
            'include_capitals_only': self.include_capitals_only,
            'exclude_islands': self.exclude_islands,
            'climate_zones': self.climate_zones,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags
        }

@dataclass
class AnalyticsResult:
    """
    Multi-city analytics eredmény.
    
    Teljes analytics lekérdezés eredménye.
    """
    question: AnalyticsQuestion
    city_results: List[CityWeatherResult]
    
    # Execution metadata
    execution_time: float                   # Végrehajtási idő (sec)
    total_cities_found: int                 # Találatok összes száma
    data_sources_used: List[DataSource]     # Használt adatforrások
    
    # Statistics
    statistics: Dict[str, float] = field(default_factory=dict)
    
    # Provider statistics
    provider_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    average_quality_score: float = 1.0
    average_confidence: float = 1.0
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    def __len__(self) -> int:
        """Eredmények száma."""
        return len(self.city_results)
    
    def get_top_results(self, n: int = 10) -> List[CityWeatherResult]:
        """Top N eredmény lekérdezése."""
        return self.city_results[:n]
    
    def get_bottom_results(self, n: int = 10) -> List[CityWeatherResult]:
        """Bottom N eredmény lekérdezése."""
        return self.city_results[-n:]
    
    def get_results_by_country(self, country_code: str) -> List[CityWeatherResult]:
        """Ország szerinti szűrés."""
        return [r for r in self.city_results if r.country_code == country_code]
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Statisztikai összefoglaló."""
        if not self.city_results:
            return {}
        
        values = [r.value for r in self.city_results]
        
        import statistics
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'range': max(values) - min(values)
        }
    
    def get_countries_represented(self) -> List[str]:
        """Képviselt országok listája."""
        return list(set(r.country_code for r in self.city_results))
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'question': self.question.to_dict(),
            'city_results': [r.to_dict() for r in self.city_results],
            'execution_time': self.execution_time,
            'total_cities_found': self.total_cities_found,
            'data_sources_used': [ds.value for ds in self.data_sources_used],
            'statistics': self.statistics,
            'provider_statistics': self.provider_statistics,
            'average_quality_score': self.average_quality_score,
            'average_confidence': self.average_confidence,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class QueryResults:
    """
    Parameter-based query eredmények.
    
    ParameterSelectorWidget query eredményeinek tárolása.
    """
    query_parameters: Dict[str, Any]
    anomalies: Dict[str, List[AnomalyResult]]  # parameter_name -> anomalies
    
    # Execution metadata
    execution_time: float
    total_records_analyzed: int
    date_range: tuple[date, date]
    
    # Statistics
    anomaly_summary: Dict[str, int] = field(default_factory=dict)
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_anomalies(self) -> int:
        """Összes anomália száma."""
        return sum(len(anomaly_list) for anomaly_list in self.anomalies.values())
    
    def get_anomalies_by_severity(self) -> Dict[str, int]:
        """Anomáliák súlyosság szerint."""
        severity_counts = {}
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                severity = anomaly.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
    
    def get_most_active_days(self, n: int = 10) -> List[tuple[date, int]]:
        """Legaktívabb napok anomália szempontjából."""
        day_counts = {}
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                day = anomaly.date
                day_counts[day] = day_counts.get(day, 0) + 1
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_days[:n]
    
    def get_anomalies_for_parameter(self, parameter: str) -> List[AnomalyResult]:
        """Paraméter-specifikus anomáliák."""
        return self.anomalies.get(parameter, [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'query_parameters': self.query_parameters,
            'anomalies': {
                param: [a.to_dict() for a in anomalies] 
                for param, anomalies in self.anomalies.items()
            },
            'execution_time': self.execution_time,
            'total_records_analyzed': self.total_records_analyzed,
            'date_range': [self.date_range[0].isoformat(), self.date_range[1].isoformat()],
            'anomaly_summary': self.anomaly_summary,
            'created_at': self.created_at.isoformat()
        }

def create_universal_time_range(
    start_date: Union[str, date],
    end_date: Union[str, date],
    granularity: Union[TimeGranularity, str] = TimeGranularity.DAILY,
    **kwargs
) -> UniversalTimeRange:
    """
    ⏰ UniversalTimeRange factory - USER-FRIENDLY
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if isinstance(granularity, str):
        granularity = TimeGranularity(granularity.lower())
    
    return UniversalTimeRange(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        **kwargs
    )

def create_universal_query(
    locations: List[UniversalLocation],
    time_range: UniversalTimeRange,
    parameters: List[str],
    analysis_type: Union[AnalysisType, str] = AnalysisType.CURRENT_CONDITIONS,
    **kwargs
) -> UniversalQuery:
    """
    🎯 UniversalQuery factory - USER-FRIENDLY
    """
    if isinstance(analysis_type, str):
        analysis_type = AnalysisType(analysis_type.lower())
    
    return UniversalQuery(
        locations=locations,
        time_range=time_range,
        parameters=parameters,
        analysis_type=analysis_type,
        **kwargs
    )

def create_analytics_question(
    question_text: str,
    question_type: QuestionType,
    region_scope: RegionScope, 
    metric: AnalyticsMetric,
    **kwargs
) -> AnalyticsQuestion:
    """
    AnalyticsQuestion factory function.
    """
    return AnalyticsQuestion(
        question_text=question_text,
        question_type=question_type,
        region_scope=region_scope,
        metric=metric,
        **kwargs
    )
