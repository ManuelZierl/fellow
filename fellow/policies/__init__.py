from typing import Dict, Tuple, Type

from fellow.policies.DenyIfFieldInBlacklist import (
    DenyIfFieldInBlacklist,
    DenyIfFieldInBlacklistConfig,
)
from fellow.policies.Policy import Policy, PolicyConfig
from fellow.policies.RequireUserConfirmation import (
    RequireUserConfirmation,
    RequireUserConfirmationConfig,
)

ALL_POLICIES: Dict[str, Tuple[Type[Policy], Type[PolicyConfig]]] = {
    "deny_if_field_in_blacklist": (
        DenyIfFieldInBlacklist,
        DenyIfFieldInBlacklistConfig,
    ),
    "require_user_confirmation": (
        RequireUserConfirmation,
        RequireUserConfirmationConfig,
    ),
    # Add other policies here
}
