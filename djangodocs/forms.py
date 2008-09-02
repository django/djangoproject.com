from django import newforms as forms

AS_Q_CHOICES = (
    ('more:dev_docs', 'Latest'),
    ('more:1.0_docs', '1.0'),
    ('more:0.96_docs', '0.96'),
    ('more:all_docs', 'All'),
)

class SearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput({'class': 'query'}))
    as_q = forms.ChoiceField(choices=AS_Q_CHOICES, widget=forms.RadioSelect, initial='more:dev_docs')
    