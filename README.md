# A FastAPI based extension portal for Microsoft Entra ID

## Introduction

Microsoft Graph SDK is a client library in Python with functionality to implement MS Graph calls using Python. Check MSLearn documentation for more details.

Directory extensions are a method by which Entra ID administrators can extend familiar Entra objects with additional attributes beyond the documented azure attributes. For instance, the user object only has pre-set azure attributes and 13 customizable ones which cannot be renamed. It is strongly typed. This is normally used to sync On-Prem AD with Entra ID or by ISVs for applications. It can also interact with dynamic groups and offer a filterability option.

## Project Overview

This project is an attempt to implement directory extensions with a GUI. Currently, it is not possible to define directory extension properties in the Entra admin center. An Azure AD administrator would have to use Graph explorer or Powershell Graph to interface with directory extensions which might be difficult.

### Current Functionality

- The ability to search, add, and delete directory extension properties for users and groups (Unified M365 groups only).
- The ability to assign values to the directory extension properties for users and groups.
- The ability to view and search users and groups, who can then be assigned directory extension property values.

### Planned Future Functionality

- The ability to add users in this GUI using bulk CSV templates which include directory extension properties in the template.
- The ability to add groups and define these groups using the directory extension properties.
- Filtering groups and users based on directory extension property values.

## Prerequisites

Before using this repository, make sure you have the following:

- An Office 365/ Microsoft 365 tenant with administrator privileges. If you do not already have one, sign up on the Microsoft developer program for a 90-day developer tenant.

## How to Use

1. Setting up your client application: Register a client application on the Azure portal. This application will act as the entry point to the FastAPI template.
2. Set up two ancillary applications for directory extensions, for users and groups.
3. Create and populate `config.dev.cfg` with the necessary credentials. Use config.cfg as the template. For example: `user_dir_app` means the application ID of the directory extension registered application for the user object.
5. Install all dependencies in `requirements.txt`. Note that MSGraph SDK is currently in general preview and does not have an SLA. The version of MSGraph used is 1.0.0a12 in this repository.
6. Run FASTAPI using `uvicorn server:app --reload`.

## Contributing

This repository is not open to contributions at this stage as a lot of code refactoring has to be done. Since MSGraph SDK is not in General availability, breaking changes can be expected with every package update.
