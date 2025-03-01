# Amplience

When configured, MACH will load the [Amplience provider](https://registry.terraform.io/providers/labd/amplience/latest) which can be used by any component that needs the Amplience integration.

For this you need to define a **client_id**, **client_secret** in your [general config](../../reference/syntax/global.md#amplience).

## site configuration

Each site can have their own Amplience configuration and but needs a hub id.

You can define the id of the hub your [site configuration](../../reference/syntax/sites.md#amplience) by giving it a **hub_id**.

## Integrate with components

When `amplience` is set as an [component integration](../../reference/components/structure.md#integrations), the component should have the following Terraform variables defined:

- `amplience_client_id`
- `amplience_client_secret`
- `amplience_hub_id`

!!! info ""
    More information on the [amplience integration on components](../../reference/components/structure.md#amplience).
