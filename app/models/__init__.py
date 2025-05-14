# Import your models here so they're available when importing from the models package
from app.models.user import User, UserConnection
from app.models.upload import UploadedText
from app.models.share import SharedAnalysis, AnalysisResult

# Export all models that should be available when importing from app.models
__all__ = ['User', 'UploadedText', 'SharedAnalysis', 'AnalysisResult', 'UserConnection']