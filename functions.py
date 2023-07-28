import configparser
from configparser import SectionProxy
from azure.identity.aio import ClientSecretCredential
import pandas as pd
import re

import json
import os
import sys
import uuid

from azure.core.exceptions import AzureError
#from azure.cosmos import CosmosClient, PartitionKey

from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider
)
from msgraph import GraphRequestAdapter, GraphServiceClient
from msgraph.generated.applications.get_available_extension_properties import \
    get_available_extension_properties_post_request_body
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from msgraph.generated.models.extension_property import ExtensionProperty
from msgraph.generated.models.group import Group
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.models.reference_create import ReferenceCreate
from msgraph.generated.models.user import User
from msgraph.generated.users.users_request_builder import UsersRequestBuilder


class Functions:
    settings: SectionProxy
    client_credential: ClientSecretCredential
    request_adapter: GraphRequestAdapter
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        client_secret = self.settings['clientSecret']
        # stu_dir_app = self.settings['stu_dir_app']
        # stu_dir_obj = self.settings['stu_dir_obj']
        # course_dir_app = self.settings['course_dir_app']
        # course_dir_obj = self.settings['course_dir_obj']
        self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        auth_provider = AzureIdentityAuthenticationProvider(self.client_credential)  # type: ignore
        self.request_adapter = GraphRequestAdapter(auth_provider)
        self.app_client = GraphServiceClient(self.request_adapter)

    async def get_students(self):
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['displayName', 'id', 'mail'],
            # Sort by display name
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        users = await self.app_client.users.get(request_configuration=request_config)
        user_display_name = []
        for user in users.value:
            user_display_name.append(user.display_name)
        return user_display_name

    async def get_student_profile_properties(self, option):
        application_id = self.settings['stu_dir_app']
        application_id = application_id.strip()
        extension_request_body = get_available_extension_properties_post_request_body.GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names_with_app = []
        extension_property_names = []

        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names_with_app.append(value.name)
                extension_property_names.append(convert_key(value.name))
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties\
            select=['displayName'] + [str(value) for value in extension_property_names_with_app],
            # Sort by display name
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        users = await self.app_client.users.get(request_configuration=request_config)
        for value in users.value:
            if str(option) == str(value.display_name):
                value_dict = {convert_key(key): value for key, value in value.additional_data.items()}
                for value in extension_property_names:
                    if value not in value_dict:
                        value_dict[value] = None
                return value_dict


    async def update_student_profile_properties(self, property_name, property_value, display_name):
        global ID
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['displayName', 'id', 'mail'],
            # Sort by display name
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user_properties_class = await self.app_client.users.get(request_configuration=request_config)
        for value in user_properties_class.value:
            if str(display_name) == str(value.display_name):
                ID = value.id
        dir_property = 'extension_0a09fe4eefd047798b49f80aaaecb550_' + property_name.replace(" ", "_")
        request_body = User()
        additional_data = dict([(dir_property, property_value)])
        request_body.additional_data = additional_data
        result = await self.app_client.users.by_user_id(ID).patch(request_body)
        pass

    async def show_template_student_properties(self,config:SectionProxy):
        application_id = self.settings['stu_dir_app']
        application_id = application_id.strip()
        extension_request_body = get_available_extension_properties_post_request_body.GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(convert_key(value.name))
        extension_property_names = list(reversed(extension_property_names))
        return extension_property_names

    async def add_template_student_property(self, config: SectionProxy, property_name):
        object_id = self.settings['stu_dir_obj']
        request_body = ExtensionProperty()
        request_body.name = re.sub(r'\s', '_', property_name)
        request_body.data_type = 'String'
        request_body.target_objects = (['User', ])
        result = await self.app_client.applications.by_application_id(object_id).extension_properties.post(
            request_body)
        pass

    async def get_courses(self, config: SectionProxy):
        application_id = self.settings['course_dir_app']
        extension_request_body = get_available_extension_properties_post_request_body. \
            GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        courses = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(value.name)
        extension_property_names = list(reversed(extension_property_names))
        for value in extension_property_names:
            if value[43:] == 'Type':
                query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
                    filter=f"{value} eq 'course'",
                    select=["displayName", "id"],
                )
                request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params,
                    headers={
                        'ConsistencyLevel': "eventual",
                    }

                )

                result = await self.app_client.groups.get(request_configuration)
                for course in result.value:
                    courses.append(course.display_name)
                return courses

    async def create_course(self, config: SectionProxy, course_name, description, properties_key_value):
        application_id = self.settings['course_dir_app']
        extension_request_body = get_available_extension_properties_post_request_body.GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(value.name)
        extension_property_names = list(reversed(extension_property_names))
        index_to_remove = next((index for index, item in enumerate(extension_property_names) if 'Type' in item), None)
        if index_to_remove is not None:
            extension_property_names.pop(index_to_remove)
        course_properties = properties_key_value
        request_body = Group()
        request_body.display_name = course_name
        request_body.description = description
        request_body.group_types = ['Unified', ]
        request_body.mail_enabled = True

        request_body.mail_nickname = re.sub(r'\s', '', course_name)

        request_body.security_enabled = False
        request_body.additional_data = dict(zip(list(extension_property_names), course_properties))
        request_body.additional_data.update({'Type': 'course'})
        result = await self.app_client.groups.post(request_body)

    async def add_template_course_property(self, config: SectionProxy, property_name):
        object_id = self.settings['course_dir_obj']
        request_body = ExtensionProperty()
        request_body.name = re.sub(r'\s', '_', property_name)
        request_body.data_type = 'String'
        request_body.target_objects = (['Group', ])
        result = await self.app_client.applications.by_application_id(object_id).extension_properties.post(
            request_body)
        pass
    #Changes test

    async def get_template_course_properties(self, config:SectionProxy):
        application_id = self.settings['course_dir_app']
        extension_request_body = get_available_extension_properties_post_request_body.GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(convert_key(value.name))
        extension_property_names = list(reversed(extension_property_names))
        return extension_property_names

    async def update_course_profile_properties(self, property_name, property_value, display_name):
        global ID
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['displayName', 'id', 'mail'],
            # Sort by display name
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        course_properties_class = await self.app_client.groups.get(request_configuration=request_config)
        for value in course_properties_class.value:
            if str(display_name) == str(value.display_name):
                ID = value.id
        dir_property = 'extension_21e32d7f-4391-4aaf-bd99-827f65f734eb_' + property_name.replace(" ", "_")
        request_body = Group()
        additional_data = dict([(dir_property, property_value)])
        request_body.additional_data = additional_data
        result = await self.app_client.groups.by_group_id(ID).patch(request_body)

        pass

    async def create_student(self, student_properties):
        pass

    async def get_course_profile_properties(self, option):
        application_id = self.settings['course_dir_app']
        application_id = application_id.strip()
        extension_request_body = get_available_extension_properties_post_request_body.GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names_with_app = []
        extension_property_names = []

        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names_with_app.append(value.name)
                extension_property_names.append(convert_key(value.name))
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            # Only request specific properties\
            select=['displayName'] + [str(value) for value in extension_property_names_with_app],
            # Sort by display name
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        groups = await self.app_client.groups.get(request_configuration=request_config)
        for value in groups.value:
            if str(option) == str(value.display_name):
                value_dict = {convert_key(key): value for key, value in value.additional_data.items()}
                for value in extension_property_names:
                    if value not in value_dict:
                        value_dict[value] = None
                return value_dict

    async def view_students_in_a_course(self, course_name):
        course_id = None
        application_id = self.settings['course_dir_app']
        extension_request_body = get_available_extension_properties_post_request_body. \
            GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        courses = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(value.name)
        extension_property_names = list(reversed(extension_property_names))
        for value in extension_property_names:
            if value[43:] == 'Type':
                query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
                    filter=f"{value} eq 'course'",
                    select=["displayName", "id"],
                )
                request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params,
                    headers={
                        'ConsistencyLevel': "eventual",
                    }

                )

                result = await self.app_client.groups.get(request_configuration)
                course_id = []
                for course in result.value:
                    if course_name == course.display_name:
                        course_id.append(course.id)
                        break
                    else:
                        continue

                query_params_students = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                    # Only request specific properties
                    select=['displayName', 'id', 'mail'],
                    # Sort by display name
                    orderby=['displayName']
                )
                request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params_students
                )
                students = await self.app_client.groups.by_group_id(course_id[0]).members.graph_user.get(request_config)

                student_display_names = []
                for value in students.value:
                    student_display_names.append(value.display_name)
                return student_display_names

    async def delete_student_property(self, config:SectionProxy, property_name):
        application_id = self.settings['stu_dir_app']
        object_id = self.settings['stu_dir_obj']
        extension_property_id = f"extension_{application_id.replace('-','')}_{property_name.replace(' ', '_')}"
        result = await self.app_client.applications.by_application_id(object_id).extension_properties.by_extension_property_id(extension_property_id).delete()
        pass

    async def add_student_to_course_singular(self, student_name, course_name):
        application_id = self.settings['course_dir_app']
        extension_request_body = get_available_extension_properties_post_request_body. \
            GetAvailableExtensionPropertiesPostRequestBody()
        extension_request_body.is_synced_from_on_premises = False
        result = await self.app_client.directory_objects.get_available_extension_properties.post(
            extension_request_body)
        extension_property_names = []
        for value in result.value:
            if value.name[10:42] == re.sub("-", "", application_id):
                extension_property_names.append(value.name)
        extension_property_names = list(reversed(extension_property_names))
        for value in extension_property_names:
            if value[43:] == 'Type':
                query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
                    filter=f"{value} eq 'course'",
                    select=["displayName", "id"],
                )
                request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params,
                    headers={
                        'ConsistencyLevel': "eventual",
                    }

                )

                result = await self.app_client.groups.get(request_configuration)
                course_id = None
                for course in result.value:
                    if course_name == course.display_name:
                        course_id = course.id
                        break
                    else:
                        continue

                query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                    # Only request specific properties
                    select=['displayName', 'id', 'mail'],
                    # Sort by display name
                    orderby=['displayName']
                )
                request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params
                )

                users = await self.app_client.users.get(request_configuration=request_config)
                student_id = None
                for user in users.value:
                    if user.display_name == student_name:
                        student_id = user.id

                request_body = ReferenceCreate()
                request_body.odata_id = f"https://graph.microsoft.com/v1.0/directoryObjects/{student_id}"

                await self.app_client.groups.by_group_id(course_id).members.ref.post(request_body)















def convert_key(key):
    sliced_key = key.split('_', 2)[-1]
    converted_key = re.sub(r'_', ' ', sliced_key)
    return converted_key

