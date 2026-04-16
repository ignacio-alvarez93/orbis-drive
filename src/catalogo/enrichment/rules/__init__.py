from .boot_rules import derive_boot_capacity_range
from .gearbox_rules import derive_gearbox_type
from .generation_rules import derive_is_current_generation
from .trim_rules import derive_trim_from_version_name

from .performance_conversion_rules import (
    derive_max_power_kw,
    derive_specific_output_kw_l,
    derive_top_speed_mph,
)
from .weight_rules import (
    derive_power_to_weight_cv_ton,
    derive_power_to_weight_kw_ton,
)
from .efficiency_rules import (
    derive_fuel_consumption_combined_mpg_uk,
    derive_fuel_consumption_combined_mpg_us,
)

__all__ = [
    "derive_gearbox_type",
    "derive_boot_capacity_range",
    "derive_trim_from_version_name",
    "derive_is_current_generation",
    "derive_max_power_kw",
    "derive_specific_output_kw_l",
    "derive_top_speed_mph",
    "derive_power_to_weight_cv_ton",
    "derive_power_to_weight_kw_ton",
    "derive_fuel_consumption_combined_mpg_uk",
    "derive_fuel_consumption_combined_mpg_us",
]
