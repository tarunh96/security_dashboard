from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, F, Count, Min
from django.http import Http404

from . import models
from . import constants
from . import utils
from . import forms as our_forms
from . import views


class CSVParser(object):
    """
    This class is intended to provide all methods needed to process the csv uploading
    """

    def __init__(self):
        self.headers_data = []
        self.lines_data = []

    def parse_csv(self, csv_lines):
        """
        this method will receive a csv file data and will process this data into a matrix
        :param csv_lines: the csv data
        """

        # reset variables
        self.lines_data = []
        self.headers_data = []

        # loop over the lines and save them in db. If error , store as string and then display
        for line in csv_lines.split("\n"):
            if len(line) > 0:
                fields = line.split(",")
                for field_item_index, field_item_value in enumerate(fields):
                    fields[field_item_index] = field_item_value.strip()
                self.lines_data.append(fields)

        self.headers_data = self.lines_data.pop(0)


class DAO(object):
    feature = constants.DAO_GENERIC_TYPE

    def __new__(cls, input_feature: str = None):
        # we override the new method to implement to factory pattern.
        # Depending on the feature argument, we wil instantiate the correct subclass
        input_feature = input_feature.upper()

        if input_feature is not None and input_feature == cls.feature:
            return super(DAO, cls).__new__(cls)
        else:
            subclass_map = {subclass.feature: subclass for subclass in cls.__subclasses__()}
            # if it is a subclass
            if input_feature is not None and input_feature in subclass_map:
                input_feature = input_feature.upper()
                # if we found the subclass
                subclass = subclass_map[input_feature]
                return super(DAO, subclass).__new__(subclass)
        raise Http404(input_feature + " of class " + str(cls.feature) + " type does not exist")
        # in any other case

    @classmethod
    def get_subclasses_map(cls):
        """
        This functions wil return a map of subclass with feature as key
        :return:
        """

        # add yourself
        class_type_list = {}
        class_type_list[cls.feature] = cls

        if len(cls.__subclasses__()) > 0:
            for subclass_dao in cls.__subclasses__():
                class_type_list.update(subclass_dao.get_subclasses_map())

        return class_type_list

    @classmethod
    def get_all_leaf_subclasses_name(cls) -> list:
        """
        :return: all finding subclasses names (only leaf classes)
        """
        class_type_list = []
        if len(cls.__subclasses__()) > 0:
            for subclass_dao in cls.__subclasses__():
                class_type_list += subclass_dao.get_all_leaf_subclasses_name()
        else:
            class_type_list.append(cls.feature)

        return list(set(class_type_list))


class AssetDAO(DAO):
    feature = constants.DAO_ASSET_TYPE
    create_template_name = 'asset-create.html'
    update_template_name = 'asset-update.html'
    delete_template_name = 'asset-delete.html'
    list_template_name = 'asset-list.html'
    create_form_class = our_forms.AssetCreateForm
    update_form_class = our_forms.AssetUpdateForm
    model = None

    def update_model_instance(self, update_dict):
        """
        this method will receive the dict and update each of its fields to the corresponding model instance.
        If it is not possible to retrieve the existing instance, a new one will be created
        """

        corrected_update_dict = self.parse_update_dict(update_dict)

        if len(corrected_update_dict['errors']) > 0:
            # if the errors list is not empty, something was not okay
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Some field was not correct",
                                            str(corrected_update_dict['errors']))
        try:
            corrected_update_dict.pop('errors', None)
            if ('id' in corrected_update_dict) and (type(int(corrected_update_dict['id'])) == int):

                update_instance = self.model.objects.filter(id=int(corrected_update_dict['id'])).first()

                # we can identify the asset with the id. Just update it
                # we now have an instance to update
                if update_instance is not None:
                    update_instance.__dict__.update(**corrected_update_dict)
                    update_instance.save()

                    return utils.create_result_dict(constants.OK_STATUS,
                                                    "Updated instance id: " + corrected_update_dict['id'],
                                                    None)

            # we could not identify the instance. Create new
            create_instance = self.model(**corrected_update_dict)
            create_instance.save()

            return utils.create_result_dict(constants.OK_STATUS,
                                            "Created new instance",
                                            None)

        except Exception as e:
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Not created nor updated",
                                            str(e))

    def get_all_too_assets(self, to_organisation_db):
        """
        Get the list of assets related to the given too
        :param to_organisation_db:
        :return:
        """
        queryset = {}
        if len(self.__class__.__subclasses__()) > 0:
            # if there is any subclass, query subclass
            for subclass_dao in self.__class__.__subclasses__():
                subclass_instance = subclass_dao()
                queryset[subclass_instance.feature] = subclass_instance.get_all_too_assets(to_organisation_db)
        else:
            # if it is a leaf class, return the queryset
            queryset = self.model.objects.filter(
                to_organisation_name__contains=to_organisation_db)
        return queryset


class AppDAO(AssetDAO):
    feature = constants.APP_ASSET_NAME
    create_form_class = our_forms.AppCreateForm
    update_form_class = our_forms.AppUpdateForm
    model = models.App
    settings_model = models.AppCSVSetting
    csv_settings_form = our_forms.AppCSVSettingForm

    @staticmethod
    def parse_update_dict(update_dict):
        """
        This function will loop over the whole dict and correct any issues. It will parse strings into object when foreignkey is needed
        :param update_dict: the dict to parse
        """
        result_dict = {
            'errors': []
        }

        # loop over the dict
        for dict_field in update_dict:
            # check it is a valid string
            if views.InputValidationMixin.check_valid_string(update_dict[dict_field]):
                try:
                    if dict_field == "to_organisation":
                        # get the to_organisation_object
                        result_dict[dict_field] = models.ToOrganisation.objects.get(
                            to_organisation_name__exact=update_dict[dict_field])
                    elif dict_field == "app_id":
                        # get the app_object
                        result_dict['id'] = utils.get_app_id_from_string(update_dict[dict_field])
                    else:
                        result_dict[dict_field] = update_dict[dict_field]
                except ObjectDoesNotExist:
                    result_dict['errors'].append("Could not parse " + dict_field)
                    continue
            else:
                result_dict['errors'].append("Could not parse " + dict_field)

        return result_dict


class PlantDAO(AssetDAO):
    feature = constants.PLANT_ASSET_NAME
    create_form_class = our_forms.PlantCreateForm
    update_form_class = our_forms.PlantUpdateForm
    model = models.Plant
    settings_model = models.PlantCSVSetting
    csv_settings_form = our_forms.PlantCSVSettingForm

    @staticmethod
    def parse_update_dict(update_dict):
        """
        This function will loop over the whole dict and correct any issues. It will parse strings into object when foreignkey is needed
        :param update_dict: the dict to parse
        """
        result_dict = {
            'errors': []
        }

        for dict_field in update_dict:
            if views.InputValidationMixin.check_valid_string(update_dict[dict_field]):
                try:
                    if dict_field == "to_organisation":
                        # get the to_organisation_object
                        result_dict[dict_field] = models.ToOrganisation.objects.get(
                            to_organisation_name__exact=update_dict[dict_field])

                    elif dict_field == "plant_id":
                        # get the app_object
                        result_dict['id'] = utils.get_plant_id_from_string(update_dict[dict_field])
                    else:
                        result_dict[dict_field] = update_dict[dict_field]
                except ObjectDoesNotExist:
                    result_dict['errors'].append("Could not parse " + dict_field)
                    continue
            else:
                result_dict['errors'].append(dict_field + " is not a valid string")
        return result_dict


class FindingDAO(DAO):
    feature = constants.GENERIC_FINDING_NAME
    create_form = our_forms.FindingCreateForm
    update_form = our_forms.FindingUpdateForm
    csv_form = our_forms.FindingCSVForm
    csv_settings_form = our_forms.FindingCSVSettingForm
    create_template_name = 'finding-create.html'
    update_template_name = 'finding-update.html'
    delete_template_name = 'finding-delete.html'
    list_template_name = 'finding-list.html'
    asset_finding_list_template_name = 'asset-finding-list.html'
    model = models.Finding

    def get_all_too_findings(self, to_organisation_db):
        """
        :param to_organisation_db: the to_organisation to query
        :return: all findings related to the specified to_organisation
        """
        queryset = {}
        for subclass_dao in self.__subclasses__():
            subclass_instance = subclass_dao(subclass_dao.feature)
            queryset[subclass_instance.feature] = subclass_instance.get_all_too_findings(to_organisation_db)
        return queryset

    def get_findings_as_of(self, temp_date):
        """
        This function wil query the db version when the date provided
        :param temp_date:
        """

        # this wil be the history_ids we want to include in our final queryset
        history_ids = []

        # the finding ids we are adding
        findings_ids = []

        # this object will store the relation for finding id and the last history change for the given date
        last_changes_ids = self.model.history.all() \
            .filter(history_date__lte=temp_date) \
            .values('id') \
            .annotate(max_history_id=Max('history_id')).order_by('id')

        for change_id in last_changes_ids:
            history_ids.append(change_id['max_history_id'])
            findings_ids.append(change_id['id'])

        # we also need to get findings that were created in the past, but were introduced later in the time
        only_created_ids = self.model.history.all() \
            .filter(create_date__lte=temp_date) \
            .values('id') \
            .annotate(count_history_id=Count('id'), min_history_id=Min('history_id')).order_by('id')

        for change_id in only_created_ids:
            if not change_id['id'] in findings_ids:
                # if that finding_id was not added previously
                history_ids.append(change_id['min_history_id'])
                findings_ids.append(change_id['id'])

        return self.model.history.all().filter(history_id__in=history_ids)


class AppFindingDAO(FindingDAO):
    feature = constants.APP_FINDING_NAME
    asset_model = models.App
    asset_type = "APP"
    create_form_class = our_forms.AppFindingCreateForm

    def get_all_asset_findings(self, to_organisation_db, asset_id):
        """
        This function will return all findings related to an APP-ID
        :param to_organisation_db:
        :param asset_id:
        :return:
        """
        queryset = {}
        if len(self.__class__.__subclasses__()) > 0:
            # if there is any subclass, query subclass
            for subclass_dao in self.__class__.__subclasses__():
                subclass_instance = subclass_dao(subclass_dao.feature)
                queryset[subclass_instance.feature] = subclass_instance.get_all_asset_findings(to_organisation_db,
                                                                                               asset_id)
        else:
            # if it is a leaf class, return the queryset
            queryset = self.model.objects.filter(
                app__to_organisation__to_organisation_name__contains=to_organisation_db,
                app__id__exact=asset_id
            )
        return queryset

    def get_all_too_findings(self, to_organisation_db):
        """
        This functions overrides the parent one.
        We now know that the finding is related to an app, so we can query
        :param to_organisation_db:
        :return:
        """
        queryset = {}
        if len(self.__class__.__subclasses__()) > 0:
            # if there is any subclass, query subclass
            for subclass_dao in self.__class__.__subclasses__():
                subclass_instance = subclass_dao(subclass_dao.feature)
                queryset[subclass_instance.feature] = subclass_instance.get_all_too_findings(to_organisation_db)
        else:
            # if it is a leaf class, return the queryset
            queryset = self.model.objects.filter(
                app__to_organisation__to_organisation_name__contains=to_organisation_db)
        return queryset

    def filter_findings_as_date(self, as_date, to_organisation_db,
                                from_date_overdue, to_date_overdue, from_date_create, to_date_Create,
                                status_list, severity_list):
        """
        This function will query the db with the given parameters
        :param as_date:
        :param to_organisation_db:
        :param from_date_overdue:
        :param to_date_overdue:
        :param from_date_create:
        :param to_date_Create:
        :param status_list:
        :param severity_list:
        :return: the queryset
        """
        queryset_as_date = None

        # if the as_date was None, we understand we want to query the actual model, not the history model
        if as_date is None:
            queryset_as_date = self.model.objects.all()
        else:
            queryset_as_date = self.get_findings_as_of(as_date)

        return queryset_as_date.filter(
            app__to_organisation__to_organisation_name__contains=to_organisation_db,
            overdue_date__gte=from_date_overdue,
            overdue_date__lte=to_date_overdue,
            create_date__gte=from_date_create,
            create_date__lte=to_date_Create,
            status__status_name__in=status_list,
            severity__severity_name__in=severity_list) \
            .values() \
            .annotate(
            severity_name=F('severity__severity_name'),
            status_name=F('status__status_name'))

    def parse_update_dict(self, update_dict):
        """
        This function will loop over the whole dict and correct any issues.
        It will parse strings into object when foreignkey is needed
        :param update_dict: the dict to parse
        """
        result_dict = {
            'errors': []
        }

        for dict_field in update_dict:
            if views.InputValidationMixin.check_valid_string(update_dict[dict_field]):
                try:
                    if dict_field == "status":
                        result_dict[dict_field] = models.FindingStatus.objects.get(
                            status_name__exact=update_dict[dict_field])
                    elif dict_field == "severity":
                        result_dict[dict_field] = models.FindingSeverity.objects.get(
                            severity_name__exact=update_dict[dict_field])
                    elif dict_field == "app":
                        a = utils.get_app_id_from_string(update_dict[dict_field])
                        result_dict[dict_field] = self.asset_model.objects.get(
                            id__exact=utils.get_app_id_from_string(update_dict[dict_field]))
                    else:
                        result_dict[dict_field] = update_dict[dict_field]
                except ObjectDoesNotExist:
                    result_dict['errors'].append("Could not parse " + dict_field)
                    continue
            else:
                result_dict['errors'].append(dict_field + " is not a valid string")

        return result_dict


class PlantFindingDAO(FindingDAO):
    feature = constants.PLANT_FINDING_NAME
    asset_model = models.Plant
    asset_type = "PLANT"
    create_form_class = our_forms.PlantFindingCreateForm


    def get_all_asset_findings(self, to_organisation_db, asset_id):
        """
        This function will return all findings related to a single PLANT-ID
        :param to_organisation_db:
        :param asset_id:
        :return:
        """
        queryset = {}
        if len(self.__class__.__subclasses__()) > 0:
            # if there is any subclass, query subclass
            for subclass_dao in self.__class__.__subclasses__():
                subclass_instance = subclass_dao(subclass_dao.feature)
                queryset[subclass_instance.feature] = subclass_instance.get_all_asset_findings(to_organisation_db,
                                                                                               asset_id)
        else:
            # if it is a leaf class, return the queryset
            queryset = self.model.objects.filter(
                plant__to_organisation__to_organisation_name__contains=to_organisation_db,
                plant__id__exact=asset_id
            )
        return queryset

    def get_all_too_findings(self, to_organisation_db):
        """
        This function will return all findings related to a single to_organisation
        :param to_organisation_db:
        :return:
        """
        queryset = {}
        if len(self.__class__.__subclasses__()) > 0:
            # if there is any subclass, query subclass
            for subclass_dao in self.__class__.__subclasses__():
                subclass_instance = subclass_dao(subclass_dao.feature)
                queryset[subclass_instance.feature] = subclass_instance.get_all_too_findings(to_organisation_db)
        else:
            # if it is a leaf class, return the queryset
            queryset = self.model.objects.filter(
                plant__to_organisation__to_organisation_name__contains=to_organisation_db)
        return queryset

    def filter_findings_as_date(self, as_date, to_organisation_db,
                                from_date_overdue, to_date_overdue, from_date_create, to_date_create,
                                status_list, severity_list):
        """
        This function wil return the queryset with the given parameters
        :param as_date:
        :param to_organisation_db:
        :param from_date_overdue:
        :param to_date_overdue:
        :param from_date_create:
        :param to_date_create:
        :param status_list:
        :param severity_list:
        :return:
        """
        queryset_as_date = None

        # if the as_date was None, we understand we want to query the actual model, not the history model
        if as_date is None:
            queryset_as_date = self.model.objects.all()
        else:
            queryset_as_date = self.get_findings_as_of(as_date)

        return queryset_as_date.filter(
            plant__to_organisation__to_organisation_name__contains=to_organisation_db,
            overdue_date__gte=from_date_overdue,
            overdue_date__lte=to_date_overdue,
            create_date__gte=from_date_create,
            create_date__lte=to_date_create,
            status__status_name__in=status_list,
            severity__severity_name__in=severity_list) \
            .values() \
            .annotate(
            severity_name=F('severity__severity_name'),
            status_name=F('status__status_name'))

    def parse_update_dict(self, update_dict):
        """
        This function will loop over the whole dict and correct any issues.
        It will parse strings into object when foreignkey is needed
        :param update_dict: the dict to parse
        """
        result_dict = {
            'errors': []
        }

        for dict_field in update_dict:
            if views.InputValidationMixin.check_valid_string(update_dict[dict_field]):
                try:
                    if dict_field == "status":
                        result_dict[dict_field] = models.FindingStatus.objects.get(
                            status_name__exact=update_dict[dict_field])
                    elif dict_field == "severity":
                        result_dict[dict_field] = models.FindingSeverity.objects.get(
                            severity_name__exact=update_dict[dict_field])
                    elif dict_field == "plant":
                        result_dict[dict_field] = self.asset_model.objects.get(
                            id__exact=utils.get_plant_id_from_string(update_dict[dict_field]))
                    else:
                        result_dict[dict_field] = update_dict[dict_field]
                except ObjectDoesNotExist:
                    result_dict['errors'].append("Could not parse " + dict_field)
                    continue
            else:
                result_dict['errors'].append(dict_field + " is not a valid string")

        return result_dict


class NonTicketFinding(object):

    def update_model_instance(self, update_dict):
        """
        this method will receive the dict and update each of its fields to the corresponding model instance.
        If it is not possible to retrieve the existing instance, a new one will be created
        """
        corrected_update_dict = self.parse_update_dict(update_dict)

        if len(corrected_update_dict['errors']) > 0:
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Some field could not be parsed",
                                            str(corrected_update_dict['errors']))
        try:
            # remove errors from dict
            corrected_update_dict.pop('errors', None)
            if ('spm_id' in corrected_update_dict) and (type(int(corrected_update_dict['spm_id'])) == int):

                update_instance = self.model.objects.filter(spm_id__exact=int(update_dict['spm_id'])).first()
                # we can identify the finding with the spm id. Just update it
                # we now have an instance to update
                if update_instance is not None:
                    update_instance.__dict__.update(**corrected_update_dict)
                    update_instance.save()

                    return utils.create_result_dict(constants.OK_STATUS,
                                                    "Updated instance spm id: " + update_dict['spm_id'],
                                                    "")

            # we could not identify the instance. Create new
            create_instance = self.model(**corrected_update_dict)
            create_instance.save()

            return utils.create_result_dict(constants.OK_STATUS,
                                            "Created new instance",
                                            "")

        except Exception as e:
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Not created nor updated",
                                            str(e))


class TicketFinding(object):

    def update_model_instance(self, update_dict):
        """
        this method will receive the dict and update each of its fields to the corresponding model instance.
        If it is not possible to retrieve the existing instance, a new one will be created
        """

        corrected_update_dict = self.parse_update_dict(update_dict)

        if len(corrected_update_dict['errors']) > 0:
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Some field could not be parsed",
                                            str(corrected_update_dict['errors']))

        try:
            if ('ticket_id' in corrected_update_dict) and (type(int(corrected_update_dict['ticket_id'])) == int):

                update_instance = self.model.objects.filter(ticket_id=int(update_dict['ticket_id'])).first()
                # we can identify the finding with the ticket id. Just update it
                # we nw have an instance to update
                if update_instance is not None:
                    update_instance.__dict__.update(**corrected_update_dict)
                    update_instance.save()

                    return utils.create_result_dict(constants.OK_STATUS,
                                                    "Updated instance ticket id: " + update_dict['ticket_id'],
                                                    "")

            if ('spm_id' in corrected_update_dict) and (type(int(corrected_update_dict['spm_id'])) == int):

                update_instance = self.model.objects.filter(spm_id__exact=int(update_dict['spm_id'])).first()
                # we can identify the finding with the spm id. Just update it
                # we now have an instance to update
                if update_instance is not None:
                    update_instance.__dict__.update(**corrected_update_dict)
                    update_instance.save()

                    return utils.create_result_dict(constants.OK_STATUS,
                                                    "Updated instance spm id: " + update_dict['spm_id'],
                                                    "")

            # we could not identify the instance. Create new
            create_instance = self.model(**corrected_update_dict)
            create_instance.save()

            return utils.create_result_dict(constants.OK_STATUS,
                                            "Created new instance",
                                            "")
        except Exception as e:
            return utils.create_result_dict(constants.SIMPLE_ERROR_STATUS,
                                            "Not created or updated",
                                            str(e))


class LCSAFindingDAO(TicketFinding, PlantFindingDAO, FindingDAO):
    feature = constants.LCSA_FINDING_NAME
    model = models.LCSAFinding
    create_form_class = our_forms.LCSACreateForm
    update_form_class = our_forms.LCSAUpdateForm
    csv_form = our_forms.LCSACSVForm
    csv_settings_form = our_forms.LCSACSVSettingsForm
    settings_model = models.LCSACSVSetting


class EPAFindingDAO(TicketFinding, AppFindingDAO, FindingDAO):
    feature = constants.EPA_FINDING_NAME
    model = models.EPAFinding
    create_form_class = our_forms.EPACreateForm
    update_form_class = our_forms.EPAUpdateForm
    csv_form = our_forms.EPACSVForm
    csv_settings_form = our_forms.EPACSVSettingsForm
    settings_model = models.EPACSVSetting


class SCASFindingDAO(NonTicketFinding, AppFindingDAO, FindingDAO):
    feature = constants.SCAS_FIDNING_NAME

    model = models.SCASFinding
    create_form_class = our_forms.SCASCreateForm
    update_form_class = our_forms.SCASUpdateForm
    csv_form = our_forms.SCASCSVForm
    csv_settings_form = our_forms.SCASCSVSettingsForm
    settings_model = models.SCASCSVSetting


class SPFindingDAO(NonTicketFinding, AppFindingDAO, FindingDAO):
    feature = constants.SP_FINDING_NAME

    model = models.SPFinding
    create_form_class = our_forms.SPCreateForm
    update_form_class = our_forms.SPUpdateForm
    csv_form = our_forms.SPCSVForm
    csv_settings_form = our_forms.SPCSVSettingsForm
    settings_model = models.SPCSVSetting
