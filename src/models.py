from django.db import models
from simple_history.models import HistoricalRecords
from . import constants


class VariablesSettings(models.Model):
    variable_name = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None)
    variable_value = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None)


class ToOrganisation(models.Model):
    to_organisation_id = models.IntegerField(primary_key=True, default=1)
    to_organisation_name = models.CharField(max_length=constants.MAX_STRING_LENGTH,
                                            choices=constants.TO_ORGANISATION_NAME_CHOICES,
                                            default=constants.DEFAULT_TO_ORGANISATION)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.to_organisation_name


class FindingStatus(models.Model):
    status_id = models.IntegerField(primary_key=True, default=1)
    status_name = models.CharField(max_length=constants.MAX_STRING_LENGTH,
                                   choices=constants.FINDING_STATUS_CHOICES,
                                   default=constants.DEFAULT_STATUS)

    def __str__(self):
        return self.status_name


class FindingSeverity(models.Model):
    severity_id = models.IntegerField(primary_key=True, default=1)
    severity_name = models.CharField(max_length=constants.MAX_STRING_LENGTH,
                                     choices=constants.FINDING_SEVERITY_CHOICES,
                                     default=constants.DEFAULT_SEVERITY)

    def __str__(self):
        return self.severity_name


class FindingTypes(models.Model):
    type_id = models.IntegerField(primary_key=True, default=1)
    type_name = models.CharField(max_length=constants.MAX_STRING_LENGTH,
                                 choices=constants.FINDING_TYPE_CHOICES,
                                 default=constants.DEFAULT_FINDING_TYPE)
    type_url = models.CharField(max_length=constants.MAX_STRING_LENGTH, default='home')

    def __str__(self):
        return self.type_name


class Asset(models.Model):
    id = models.IntegerField(primary_key=True, default=0)
    name = models.CharField(max_length=constants.MAX_STRING_LENGTH)
    to_organisation = models.ForeignKey(ToOrganisation, on_delete=models.CASCADE)
    to_responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    toc_responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    history = HistoricalRecords(inherit=True, cascade_delete_history=True)

    def __str__(self):
        return self.get_asset_type + "-" + str(self.id)

    @property
    def get_asset_type(self):
        return constants.GENERIC_ASSET_NAME

    @property
    def asset_id(self):
        return str(self.id)

    @property
    def asset_id_human(self):
        return self.get_asset_type + "-" + str(self.id)

    @property
    def asset_id_title(self):
        return self.get_asset_type + "_ID"

    @property
    def asset_name_title(self):
        return self.get_asset_type + "_NAME"

    class Meta:
        abstract = True


class App(Asset):
    """this class is intended to store information about an application"""

    @property
    def get_asset_type(self):
        return constants.APP_ASSET_NAME


class Plant(Asset):
    """this class is intended to store information about a plant"""

    @property
    def get_asset_type(self):
        return constants.PLANT_ASSET_NAME


# finding definition
class Finding(models.Model):
    """this class is intended to store information about a finding and be able to relate it to an app"""

    spm_id = models.IntegerField(unique=True, default=0)
    short_description = models.CharField(max_length=constants.MAX_STRING_LENGTH)
    description = models.CharField(max_length=constants.MAX_STRING_LENGTH)
    status = models.ForeignKey(FindingStatus, on_delete=models.CASCADE, default=None)
    severity = models.ForeignKey(FindingSeverity, on_delete=models.CASCADE, default=None)
    responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH)
    comment = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    create_date = models.DateField(default=None)
    overdue_date = models.DateField(default=None)
    history = HistoricalRecords(inherit=True, cascade_delete_history=True)

    @property
    def finding_type_name(self):
        return constants.GENERIC_FIDNING_NAME

    def __str__(self):
        return "ID: " + str(self.id) + " - " + self.short_description

    class Meta:
        abstract = True


class AppFinding(Finding):
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def get_asset_id(self):
        return str(self.app)

    @property
    def get_asset_object(self):
        return self.app


class PlantFinding(Finding):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def get_asset_id(self):
        return str(self.plant)

    @property
    def get_asset_object(self):
        return self.plant


class TicketFinding(models.Model):
    ticket_id = models.IntegerField(unique=True, default=None)

    class Meta:
        abstract = True


class NonTicketFinding(models.Model):

    class Meta:
        abstract = True


class LCSAFinding(PlantFinding, TicketFinding):

    @property
    def finding_type_name(self):
        return constants.LCSA_FINDING_NAME


class EPAFinding(AppFinding, TicketFinding):

    @property
    def finding_type_name(self):
        return constants.EPA_FINDING_NAME


class SCASFinding(AppFinding, NonTicketFinding):

    @property
    def finding_type_name(self):
        return constants.SCAS_FIDNING_NAME


class SPFinding(AppFinding, NonTicketFinding):

    @property
    def finding_type_name(self):
        return constants.SP_FINDING_NAME


class AssetCSVSetting(models.Model):
    setting_name = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, unique=True)
    # asset_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    name = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    to_responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    toc_responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)
    to_organisation = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)

    class Meta:
        abstract = True


# settings definition
class AppCSVSetting(AssetCSVSetting):
    """this class is intended to store csv information about an application"""
    app_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)


class PlantCSVSetting(AssetCSVSetting):
    """this class is intended to store csv information about a plant"""
    plant_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, null=True)


class FindingCSVSetting(models.Model):
    """
    keep in mind that we need to check this model in case any of the findings models fields are changed.
    In that case, please double check all fields in parent and child classes are the same.
    """
    setting_name = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, unique=True)
    spm_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    short_description = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    description = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    responsible = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    comment = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    create_date = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    overdue_date = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    status = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
    severity = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)

    def __str__(self):
        return str(self.id) + ':' + self.setting_name

    class Meta:
        abstract = True


class AppFindingCSVSetting(FindingCSVSetting):
    app = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)

    class Meta:
        abstract = True


class PlantFindingCSVSetting(FindingCSVSetting):
    plant = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)

    class Meta:
        abstract = True


class TicketFindingCSVSetting(models.Model):
    ticket_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)

    class Meta:
        abstract = True


class EPACSVSetting(AppFindingCSVSetting, TicketFindingCSVSetting):
    """
    this model is in charge of storing csv columns settings for EPA imports
    """
    ticket_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)


class SCASCSVSetting(AppFindingCSVSetting):
    pass


class SPCSVSetting(AppFindingCSVSetting):
    pass


class LCSACSVSetting(PlantFindingCSVSetting, TicketFindingCSVSetting):
    ticket_id = models.CharField(max_length=constants.MAX_STRING_LENGTH, default=None, null=True)
