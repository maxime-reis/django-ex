#####
# Django includes
###
from django import forms

#####
# Third-Party includes
###
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Hidden, Field

#####
# Project includes
###
from SSD.models import SSD
from software_configuration.models import OS, LinuxKernel
from hardware_configuration.models import CPU


class ImportSSDBenchmarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()

        self.helper.form_method = 'post'
        self.helper.form_action = '/benchmarks/import_benchmarks/'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.form_id = 'import_ssd_benchmark_form'
        self.helper.add_input(Submit('submit', 'Submit'))

        super(ImportSSDBenchmarkForm, self).__init__(*args, **kwargs)

    # Mandatory Fields
    ssd = forms.ModelChoiceField(SSD.objects.all())
    benchmark_type = forms.ChoiceField((
        ('l2', 'l2'),
        ('l3', 'l3'),
        ('stability', 'l2 stability'),
    ))

    # Optional Fields
    os = forms.ModelChoiceField(OS.objects.all(), required=False)
    kernel = forms.ModelChoiceField(LinuxKernel.objects.all(), required=False)
    cpu = forms.ModelChoiceField(CPU.objects.all(), required=False)
    file = forms.FileField()
