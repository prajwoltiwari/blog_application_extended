from django import forms 

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('admitted','date_posted', 'author')
       