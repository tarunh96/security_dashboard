from . import models, utils
from django import forms
from datetime import datetime
from datetime import timedelta
from . import service_layer_controller_logic as controller_logic


class CustomDateInput(forms.DateInput):
    input_type = 'date'


class CSVFileForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get("csv_file")
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError("The file is not a CSV")
        # if file is too large, return
        if csv_file.multiple_chunks():
            raise forms.ValidationError("Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),))

        return csv_file


class AssetCSVSettingForm(forms.ModelForm):

    setting_name = forms.CharField(required=True)
    asset_id = forms.CharField(required=False)
    name = forms.CharField(required=False)
    to_responsible = forms.CharField(required=False)
    toc_responsible = forms.CharField(required=False)
    to_organisation = forms.CharField(required=False)

    class Meta:
        model = models.AssetCSVSetting
        fields = '__all__'


class AppCSVSettingForm(AssetCSVSettingForm):

    class Meta:
        model = models.AppCSVSetting
        fields = '__all__'


class PlantCSVSettingForm(AssetCSVSettingForm):
    class Meta:
        model = models.PlantCSVSetting
        fields = '__all__'


class FindingCSVSettingForm(forms.ModelForm):

    setting_name = forms.CharField(required=True)
    short_description = forms.CharField(required=False)
    description = forms.CharField(required=False)
    responsible = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    create_date = forms.CharField(required=False)
    overdue_date = forms.CharField(required=False)
    status = forms.CharField(required=False)
    spm_id = forms.CharField(required=False)
    severity = forms.CharField(required=False)

    class Meta:
        model = models.FindingCSVSetting
        fields = '__all__'


class APPCSVSettingsForm(FindingCSVSettingForm):

    app = forms.CharField(required=False)

    class Meta:
        model = models.AppFindingCSVSetting
        fields = '__all__'


class EPACSVSettingsForm(APPCSVSettingsForm):

    ticket_id = forms.CharField(required=False)

    class Meta:
        model = models.EPACSVSetting
        fields = '__all__'


class SCASCSVSettingsForm(APPCSVSettingsForm):

    class Meta:
        model = models.SCASCSVSetting
        fields = '__all__'


class SPCSVSettingsForm(APPCSVSettingsForm):

    class Meta:
        model = models.SPCSVSetting
        fields = '__all__'


class PlantCSVSettingsForm(FindingCSVSettingForm):

    plant = forms.CharField(required=False)

    class Meta:
        model = models.PlantFindingCSVSetting
        fields = '__all__'


class LCSACSVSettingsForm(PlantCSVSettingsForm):

    ticket_id = forms.CharField(required=False)

    class Meta:
        model = models.LCSACSVSetting
        fields = '__all__'


class FindingUpdateForm(forms.ModelForm):

    class Meta:
        model = models.Finding
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FindingUpdateForm, self).__init__(*args, **kwargs)

        # these fields are either not updatable or automatic from code side
        self.fields['spm_id'].disabled = True
        self.fields['create_date'].disabled = True
        self.fields['severity'].disabled = True
        self.fields['overdue_date'].disabled = True

        self.fields['comment'].required = False


class AppUpdateForm(FindingUpdateForm):

    class Meta:
        model = models.AppFinding
        fields = '__all__'


class PlantUpdateForm(FindingUpdateForm):

    class Meta:
        model = models.PlantFinding
        fields = '__all__'


class LCSAUpdateForm(FindingUpdateForm):

    class Meta:
        model = models.LCSAFinding
        fields = '__all__'


class EPAUpdateForm(AppUpdateForm):

    class Meta:
        model = models.EPAFinding
        fields = '__all__'


class SCASUpdateForm(AppUpdateForm):

    class Meta:
        model = models.SCASFinding
        fields = '__all__'


class SPUpdateForm(AppUpdateForm):

    class Meta:
        model = models.SPFinding
        fields = '__all__'


class FindingCreateForm (forms.ModelForm):

    class Meta:
        model = models.Finding
        fields = '__all__'

    def __init__(self, input_to_organisation=None, *args, **kwargs):
        super(FindingCreateForm, self).__init__(*args, **kwargs)


        self.fields['create_date'] = forms.DateField(widget=CustomDateInput)
        self.fields['overdue_date'] = forms.DateField(widget=CustomDateInput)
        self.fields['overdue_date'].help_text = 'Overdue_date: If empty, it will be automatically calculated'
        self.fields['overdue_date'].required = False


        self.fields['comment'].required = False

        if input_to_organisation is not None:
            self.fields['']

    """
    clean methods provide a way to process each form attribute before validation
    """

    def clean_overdue_date(self):
        """
        We need to calculate the number of days for remediation to set the overdue date
        :return: the overdue date fo the vulnerability remediation
        """
        if self.cleaned_data['overdue_date']:
            # then overdue date is something
            return self.cleaned_data['overdue_date']
        remediation_days = utils.get_severity_remediation_timeline_in_days(self.cleaned_data['severity'].severity_name)
        return self.cleaned_data['create_date'] + timedelta(days=remediation_days)


class PlantFindingCreateForm(FindingCreateForm):
    class Meta:
        model = models.PlantFinding
        fields = '__all__'

    def __init__(self, input_to_organisation=None, *args, **kwargs):
        super(PlantFindingCreateForm, self).__init__(*args, **kwargs)

        if input_to_organisation is not None:
            self.fields['plant'].queryset = models.Plant.objects.filter(to_organisation__to_organisation_name__contains=input_to_organisation)


class AppFindingCreateForm(FindingCreateForm):
    class Meta:
        model = models.AppFinding
        fields = '__all__'

    def __init__(self, input_to_organisation=None, *args, **kwargs):
        super(AppFindingCreateForm, self).__init__(*args, **kwargs)

        if input_to_organisation is not None:
            self.fields['app'].queryset = models.App.objects.filter(to_organisation__to_organisation_name__contains=input_to_organisation)


class EPACreateForm(AppFindingCreateForm):

    class Meta:
        model = models.EPAFinding
        fields = '__all__'


class SCASCreateForm(AppFindingCreateForm):

    class Meta:
        model = models.SCASFinding
        fields = '__all__'


class SPCreateForm(AppFindingCreateForm):

    class Meta:
        model = models.SPFinding
        fields = '__all__'


class LCSACreateForm(PlantFindingCreateForm):

    class Meta:
        model = models.LCSAFinding
        fields = '__all__'


class FindingCSVForm(forms.ModelForm):

    class Meta:
        model = models.Finding
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FindingCSVForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
        self.fields['comment'].required = False
        self.fields['spm_id'].required = False

    def clean_status(self):
        if type(self.cleaned_data['status']) == str:
            # we expect to receive the string for the status. Return the object
            return models.FindingStatus.objects.get(status_name__exact=self.cleaned_data['status'])
        else:
            # the status field was not updated. Return it
            return self.cleaned_data['status']

    def clean_severity(self):

        if type(self.cleaned_data['severity']) == str:
            # we expect to receive the severity string. Return the object
            return models.FindingSeverity.objects.get(severity_name__exact=self.cleaned_data['severity'])
        else:
            # the severity field was not updated. Return it
            return self.cleaned_data['severity']


class AppFindingCSVForm(FindingCSVForm):

    class Meta:
        model = models.AppFinding
        fields = '__all__'

    def clean_app(self):

        if type(self.cleaned_data['app']) == str:
            # we expect to receive the id of the app. Return the app object
            return models.App.objects.get(app_id__exact=self.cleaned_data['app'])

        # in this case the app field was not updated, so we just return it
        return self.cleaned_data['app']


class EPACSVForm(AppFindingCSVForm):

    class Meta:
        model = models.EPAFinding
        fields = '__all__'


class SCASCSVForm(AppFindingCSVForm):

    class Meta:
        model = models.SCASFinding
        fields = '__all__'


class SPCSVForm(AppFindingCSVForm):

    class Meta:
        model = models.SPFinding
        fields = '__all__'


class PlantFindingCSVForm(FindingCSVForm):

    class Meta:
        model = models.AppFinding
        fields = '__all__'

    def clean_app(self):

        if type(self.cleaned_data['plant']) == str:
            # we expect to receive the id of the app. Return the app object
            return models.Plant.objects.get(plant_id__exact=self.cleaned_data['plant'])

        # in this case the app field was not updated, so we just return it
        return self.cleaned_data['plant']


class LCSACSVForm(PlantFindingCSVForm):

    class Meta:
        model = models.LCSAFinding
        fields = '__all__'


# asset forms


class AssetCreateForm(forms.ModelForm):

    class Meta:
        model = models.Asset
        fields = '__all__'

    def __init__(self, input_to_organisation=None, *args, **kwargs):
        super(AssetCreateForm, self).__init__(*args, **kwargs)

        if input_to_organisation is not None:
            self.fields['to_organisation'].queryset = models.ToOrganisation.objects.filter(to_organisation_name__contains=input_to_organisation)


class AppCreateForm(AssetCreateForm):
    class Meta:
        model = models.App
        fields = '__all__'


class PlantCreateForm(AssetCreateForm):
    class Meta:
        model = models.Plant
        fields = '__all__'


class AssetUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Asset
        fields = '__all__'

    def __init__(self, input_to_organisation=None, *args, **kwargs):
        super(AssetUpdateForm, self).__init__(*args, **kwargs)
        self.fields["id"].disabled = True
        self.fields["to_organisation"].disabled = True

class AppUpdateForm(AssetUpdateForm):
    class Meta:
        model = models.App
        fields = '__all__'


class PlantUpdateForm(AssetUpdateForm):
    class Meta:
        model = models.Plant
        fields = '__all__'