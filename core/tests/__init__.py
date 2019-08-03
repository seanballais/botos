from .admin_forms import (
    ElectionSettingsCurrentTemplateFormTest,
    ElectionSettingsElectionStateFormTest,
    ElectionSettingsPubPrivKeysFormTest
)
from .admin_view import (
    ElectionSettingsViewTest, ElectionSettingsCurrentTemplateViewTest,
    ElectionSettingsElectionsStateViewTest, ElectionSettingsPubPrivKeysViewTest
)
from .auth_views import (
    LoginViewTest, LogoutViewTest
)
from .base_model import (
    BaseModelTest
)
from .context_processors import TemplateContextProcessorTest
from .election_models import (
    CandidateTest, CandidatePartyTest, CandidatePositionTest
)
from .index_views import (
    LoginSubviewTest, VotingSubviewTest, VotedSubviewTest
)
from .management import CreateSuperUserTest
from .results_view import ResultsViewTest
from .settings_model import SettingTest
from .user_models import (
    UserModelTest, BatchModelTest, SectionModelTest
)
from .utils import AppSettingsTest
from .vote_view import VoteProcessingView

__all__ = [
    # User Models
    'UserModelTest', 'BatchModelTest', 'SectionModelTest',
    'Candidate', 'CandidateParty', 'CandidatePosition',
    'AppSettingsTest', 'BaseModelTest',
    # Index Views
    'LoginSubviewTest', 'VotingSubviewTest', 'VotedSubviewTest',
    # Results View
    'ResultsViewTest',
    # Vote Views
    'VoteProcessingView',
    # Admin Elections Settings Forms
    'ElectionSettingsCurrentTemplateFormTest',
    'ElectionSettingsElectionStateFormTest',
    'ElectionSettingsPubPrivKeysFormTest',
    # Admin Elections Settings Views
    'ElectionSettingsViewTest',
    'ElectionSettingsCurrentTemplateViewTest',
    'ElectionSettingsElectionsStateViewTest',
    'ElectionSettingsPubPrivKeysViewTest',
    # Auth Views
    'LoginViewTest', 'LogoutViewTest',
    # Context Processors
    'TemplateContextProcessorTest'
]
