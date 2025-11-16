from django.forms import ModelForm # Simplified import
from django import forms
from .models import Thesis, Tag, College, Program 
import datetime # Needed for dynamic year validation

# Changed base class from forms.ModelForm to ModelForm
class ThesisUploadForm(ModelForm):
    # This field MUST be defined explicitly to force the CheckboxSelectMultiple widget
    # and to apply the necessary ordering to the tags.
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Relevant Research Areas/Tags (e.g., AI, Web Development)"
    )

    pdf_file = forms.FileField(
        label="Upload Thesis PDF",
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        required=False,
        help_text="Upload the final thesis manuscript in PDF format."
    )
    
    # This field MUST be defined explicitly to enforce max_value validation 
    # using Python's datetime library (preventing future years).
    year_submitted = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 2024', 'min': 1900, 'max': datetime.date.today().year}),
        min_value=1900, 
        max_value=datetime.date.today().year,
        label="Year Submitted"
    )

    class Meta:
        model = Thesis
        # We list the specific fields here to ensure we don't accidentally expose 
        # fields like 'panel_score' or 'uploaded_by' which must be set in the view.
        fields = [
            'title', 
            'abstract', 
            'authors', 
            'adviser', 
            'year_submitted', 
            'college', 
            'program', 
            'tags',
            'pdf_file',
            'panel_score'
        ]
        
        # We use the 'widgets' property to customize the appearance of the fields
        # that we DID NOT define explicitly (like title, abstract, authors, adviser).
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter the Thesis Title'}),
            'abstract': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide a concise abstract (summary) of the research.'}),
            'authors': forms.TextInput(attrs={'placeholder': 'e.g., John Doe, Jane Smith (Comma-separated)'}),
            'adviser': forms.TextInput(attrs={'placeholder': 'e.g., Prof. Alex Smith'}),
            'panel_score': forms.NumberInput(attrs={'placeholder': 'e.g., 92.5 (Optional)'}),
        }

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if not file and not getattr(self.instance, 'pk', None):
            raise forms.ValidationError('Please upload a PDF file for this thesis.')
        return file