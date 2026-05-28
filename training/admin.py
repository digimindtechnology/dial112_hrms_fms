from django.contrib import admin
from setup.models import TrainerType
from training.models import Trainer, TrainingStatus, TrainingType, TrainingProgram

admin.site.register(TrainerType)
admin.site.register(Trainer)

admin.site.register(TrainingStatus)
admin.site.register(TrainingType)
admin.site.register(TrainingProgram)
