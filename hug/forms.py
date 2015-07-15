from django.forms import ModelForm
from .models import BonusData

class SettingsForm(ModelForm):
    def clean_twitter(self):
        data = self.cleaned_data['twitter'].strip()
        if len(data)>0:
            if data[0] != "@":
                return "@"+data
        return data
    class Meta:
        model = BonusData
        fields = ['user', 'twitter']
        help_texts = {
            'twitter': "Must begin with @",
        }
