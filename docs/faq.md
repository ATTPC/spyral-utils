# Frequently Asked Questions

## Why do we need spyral-utils?

Spyral is an analysis framework. It aims to provide a starting groud for AT-TPC analysis; as such it is expected that Spyral will not always cover every use case. AT-TPC can run a wide range of experiments and each of these data sets can require a unique analysis approach. Spyral cannot cover all of these cases by default. spyral-utils provides tools we expect would be needed to extend Spyral to cover some of these cases as well as to continue analysis after Spyral, such as analysis of excitation energy spectra, angular distributions, etc.

## Why doesn't spyral-utils have feature x-y-z?

spyral-utils needs to be fully compatible with Spyral's goals. It should be cross-platform, and support a minimum Python version of 3.10. These requirements alone can eliminate a lot of tools! But, usually the reason is we just haven't thought of it yet. If you have an idea of a useful tool to add to spyral-utils please see the [For Developers] section and submit a pull request or open an issue on GitHub!
