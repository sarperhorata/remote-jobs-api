# Re-export all models from the models package for backward compatibility
from .models.models import *
from .models.job import *
from .models.user import *

# This file exists to satisfy test requirements that expect models.py in the root 