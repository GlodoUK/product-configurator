
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/GlodoUK/product-configurator/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/GlodoUK/product-configurator/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/GlodoUK/product-configurator/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/GlodoUK/product-configurator/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/GlodoUK/product-configurator/branch/15.0/graph/badge.svg)](https://codecov.io/gh/GlodoUK/product-configurator)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Advanced Product Configurator (originally pledra/odoo-product-configurator, and oca/product-configurator)

> [!WARNING]
> Please do not use this fork for future projects which require dynamic product configuration.
> Please instead look at [GlodoUK/cpq](https://github.com/GlodoUK/cpq), which provides a similar feature set, at a lower line of code count, and integrates with existing Odoo features in a 15.0+ world.

~~We have forked OCA/product-configurator for a few reasons:~~

- ~~There does not seem to be much interest in OCA/product-configurator currently and we are struggling to help progress it and under stand some historical decisions.~~
- ~~Around 13.0 some changes to how custom options work seem to have been made which fly in the face of many common usage scenarios.~~
- ~~We want to try some experimentation to fit the needs of some of our customers without impacting on any existing OCA users.~~

~~We are not ruling out merging this repository back into OCA/product-configurator once we understand where we are going with this fork.~~

~~We make no guarantees over the current state or stability of this fork.~~


<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Glo Networks
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
