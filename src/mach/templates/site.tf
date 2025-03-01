# This file is auto-generated by MACH composer
# Site: {{ site.identifier }}

terraform {
  {% if general_config.terraform_config.azure_remote_state %}
  {% set azure_config = general_config.terraform_config.azure_remote_state %}
  backend "azurerm" {
    resource_group_name  = {{ azure_config.resource_group|tf }}
    storage_account_name = {{ azure_config.storage_account|tf }}
    container_name       = {{ azure_config.container_name|tf }}
    key                  = "{{ azure_config.state_folder}}/{{ site.identifier }}"
  }
  {% elif general_config.terraform_config.aws_remote_state %}
  {% set aws_config = general_config.terraform_config.aws_remote_state %}
  backend "s3" {
    bucket         = {{ aws_config.bucket|tf }}
    key            = "{{ aws_config.key_prefix}}/{{ site.identifier }}"
    region         = {{ aws_config.region|tf }}
    {% if aws_config.role_arn %}
    role_arn       = {{ aws_config.role_arn|tf }}
    {% endif %}
    {% if aws_config.lock_table %}
    dynamodb_table = {{ aws_config.lock_table|tf }}
    {% endif %}
    encrypt        = {% if aws_config.encrypt %}true{% else %}false{% endif %}

  }
  {% endif %}
}

terraform {
  required_providers {
    {% if site.aws %}
    aws = {
      version = "~> {{ general_config.terraform_config.providers.aws or '3.66.0' }}"
    }
    {% endif %}

    {% if site.azure %}
    azurerm = {
      version = "~> {{ general_config.terraform_config.providers.azure or '2.86.0' }}"
    }
    {% endif %}
    {% if site.commercetools %}
    commercetools = {
      source = "labd/commercetools"
      version = "~> {{ general_config.terraform_config.providers.commercetools or '0.29.3' }}"
    }
    {% endif %}
    {% if site.contentful %}
    contentful = {
      source = "labd/contentful"
      version = "~> {{ general_config.terraform_config.providers.contentful or '0.1.0' }}"
    }
    {% endif %}
    {% if site.amplience %}
    amplience = {
      source = "labd/amplience"
      version = "~> {{ general_config.terraform_config.providers.amplience or '0.2.2' }}"
    }
    {% endif %}
    {% if general_config.sentry.managed %}
    sentry = {
      source = "jianyuan/sentry"
      version = "~> {{ general_config.terraform_config.providers.sentry or '0.6.0' }}"
    }
    {% endif %}
    {% if config.variables_encrypted %}
    sops = {
      source = "carlpett/sops"
      version = "~> 0.5"
    }
    {% endif %}
  }
}

{% if config.variables_encrypted %}
data "local_file" "variables" {
  filename = "variables.yml"
}

data "sops_external" "variables" {
  source     = data.local_file.variables.content
  input_type = "yaml"
}
{% endif %}

{% if general_config.sentry.managed %}
provider "sentry" {
  token = {{ general_config.sentry.auth_token|tf }}
  base_url = {% if general_config.sentry.base_url %}{{ general_config.sentry.base_url|tf }}{% else %}"https://sentry.io/api/"{% endif %}

}
{% endif %}

{% if site.commercetools %}{% include 'partials/commercetools.tf' %}{% endif %}
{% if site.contentful %}{% include 'partials/contentful.tf' %}{% endif %}
{% if site.amplience %}{% include 'partials/amplience.tf' %}{% endif %}

{% if site.aws %}{% include 'partials/aws.tf' %}{% endif %}
{% if site.azure %}{% include 'partials/azure.tf' %}{% endif %}

{% include 'partials/components.tf' %}
