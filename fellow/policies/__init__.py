from typing import Dict, Tuple, Type

from fellow.policies.DenyIfFieldInBlacklist import (
    DenyIfFieldInBlacklist,
    DenyIfFieldInBlacklistConfig,
)
from fellow.policies.Policy import Policy, PolicyConfig

ALL_POLICIES: Dict[str, Tuple[Type[Policy], Type[PolicyConfig]]] = {
    "deny_if_field_in_blacklist": (
        DenyIfFieldInBlacklist,
        DenyIfFieldInBlacklistConfig,
    ),
    # Add other policies here
}
