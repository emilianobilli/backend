from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()



class GirlForm(forms.Form):
    """Image upload form."""
    name  = forms.CharField()
    image = forms.ImageField()