import calendar
import datetime


# models foreign key choices
"""
possible markets for the to - organisation in appsinfo table
"""
TO_ORGANISATION_NAME_CHOICES = [
    ('ITS/E', "ITS/E"),
    ('ITS/EM', "ITS/EM"),
    ('ITS/EM ES', "ITS/EM ES"),
    ('ITS/EM CH', "ITS/EM CH"),
    ('ITS/EU', "ITS/EU"),
    ('ITS/EM IT', "ITS/EM IT"),
    ('ITS/EG', "ITS/EG"),
    ('ITS/EM SEDK', "ITS/EM SEDK"),
    ('ITS/EM FR', "ITS/EM FR"),
    ('ITS/EM BE', "ITS/EM BE"),
    ('ITS/EM NE', "ITS/EM NE"),
    ('ITS/EM LU', "ITS/EM LU"),
    ('ITS/EM HU', "ITS/EM HU"),
    ('ITS/EU', "ITS/EU")
]

"""
possible finding status for the findings table
"""
FINDING_STATUS_CHOICES = [
    ('SOLVED', 'SOLVED'),
    ('PLANNED', 'PLANNED'),
    ('NOT_PLANNED', 'NOT_PLANNED'),
    ('WIP', 'WIP'),
    ('CLOSED', 'CLOSED')
]
DEFAULT_STATUS = "NOT_PLANNED"

"""
possible finding severities for the findings table
"""
FINDING_SEVERITY_CHOICES = [
    ('LOW', 'LOW'),
    ('MEDIUM', 'MEDIUM'),
    ('HIGH', 'HIGH'),
    ('CRITICAL', 'CRITICAL')
]
DEFAULT_SEVERITY = "UNKNOWN"


"""
possible finding status for the findings table
"""
FINDING_TYPE_CHOICES = [
    ('EPA', 'ENHANCED_PROTECTION_ANALYSIS'),
    ('SCAS', 'SOURCE_CODE_ANALYSIS'),
    ('SSL', 'SSL'),
    ('CIVA', 'CIVA-I'),
    ('LCSA', 'LCSA'),
    ('SP', 'SP')
]

OK_STATUS = 0
SIMPLE_ERROR_STATUS = 1

DEFAULT_FINDING_TYPE = "UNKNOWN"

DEFAULT_TO_ORGANISATION = "ITS/E"

MAX_STRING_LENGTH = 255

GENERIC_ASSET_NAME = "ASSET"
APP_ASSET_NAME = "APP"
PLANT_ASSET_NAME = "PLANT"

GENERIC_FINDING_NAME = "FINDING"
APP_FINDING_NAME = "APP_FINDING"
PLANT_FINDING_NAME = "PLANT_FINDING"
EPA_FINDING_NAME = "EPA"
LCSA_FINDING_NAME = "LCSA"
SP_FINDING_NAME = "SP"
SCAS_FIDNING_NAME = "SCAS"


DAO_GENERIC_TYPE = "GENERIC_DAO"
DAO_ASSET_TYPE = "ASSET_DAO"
DAO_FINDING_TYPE = "FINDING_DAO"

LAST_MONTH_OF_YEAR = 12
FIRST_MONTH_OF_YEAR = 1

MONTH_DICT = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}