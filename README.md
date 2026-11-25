<!-- header:begin (generated from project metadata) -->
<h1 align="center">Example App</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-App-Template/dev/example-app/logo.png" alt="Example App" width="360" height="90">
</p>

---

<p align="center">
  <a href="https://paypal.me/seb5594"><img src="https://img.shields.io/static/v1?label=Support&amp;message=PayPal&amp;color=0070BA&amp;logo=paypal&amp;logoColor=white&amp;style=for-the-badge" alt="PayPal" height="40"></a>
  <a href="https://buymeacoffee.com/seb5594"><img src="https://raw.githubusercontent.com/seb5594/Home-Assistant-Apps/473dc258f963096745aac327df54950eb9b59066/.github/assets/support-beer.svg" alt="Buy me a beer" height="40"></a><br>
  <a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fseb5594%2FHome-Assistant-Apps"><img src="https://img.shields.io/static/v1?label=Home%20Assistant&amp;message=Add%20app%20repository&amp;color=18BCF2&amp;logo=homeassistant&amp;logoColor=white&amp;style=for-the-badge" alt="Home Assistant" height="28"></a>
  <a href="https://github.com/seb5594/Home-Assistant-App-Template/releases"><img src="https://img.shields.io/static/v1?label=version&amp;message=0.1.0&amp;color=1877A5&amp;style=for-the-badge" alt="version" height="28"></a><br>
  <img src="https://img.shields.io/static/v1?label=arch&amp;message=amd64%20%C2%B7%20aarch64%20%C2%B7%20armv7%20%C2%B7%20armhf%20%C2%B7%20i386&amp;color=157F71&amp;style=flat" alt="arch" height="20">
  <img src="https://img.shields.io/static/v1?label=stage&amp;message=stable&amp;color=2F855A&amp;style=flat" alt="stage" height="20">
  <img src="https://img.shields.io/static/v1?label=mounts%20%28read-only%29&amp;message=config&amp;color=157F71&amp;style=flat" alt="mounts (read-only)" height="20"><br>
  <a href="https://github.com/seb5594/Home-Assistant-Apps/stargazers"><img src="https://img.shields.io/github/stars/seb5594/Home-Assistant-App-Template?label=stars&amp;style=flat" alt="stars" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-Apps/issues"><img src="https://img.shields.io/github/issues/seb5594/Home-Assistant-App-Template?label=issues&amp;style=flat" alt="issues" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-App-Template/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/seb5594/Home-Assistant-App-Template/ci.yml?branch=dev&amp;label=checks&amp;style=flat" alt="checks" height="20"></a>
  <a href="https://github.com/seb5594/Home-Assistant-Apps#license"><img src="https://img.shields.io/github/license/seb5594/Home-Assistant-App-Template?label=license&amp;style=flat" alt="license" height="20"></a>
</p>
<!-- header:end -->

**🇬🇧 English** · [🇩🇪 Deutsch](README.de.md)

A starting point for a Home Assistant app with the shared pipeline already wired in: validation,
multi-architecture build, runtime tests, GHCR release and README badges.

## Using this template

1. Create a repository from this template. Name it `Home-Assistant-<project>-App` so the
   [app catalog](https://github.com/seb5594/Home-Assistant-Apps) picks it up.
2. Rename `example-app/` and set `slug`, `name`, `url`, `description` and the options in `config.yaml`.
   The folder name must equal the slug.
3. Replace the repository URL in the `Dockerfile` label and change the greeting logic in `run.sh`.
   Every `apk` package is pinned through a build argument with a legacy twin (`ARG JQ_VERSION=` and
   `ARG JQ_VERSION_LEGACY=`): the twin carries the Alpine 3.22 version used for `armv7`, `armhf` and `i386`.
   Remove those architectures from `config.yaml` to drop the twins.
4. Adjust `.github/tests/runtime.sh`; it runs inside the built image.
5. Regenerate the badge block above and commit the result:

   ```bash
   git clone https://github.com/seb5594/hass-workflows .engine   # private; needs access
   python .engine/.scripts/readme.py
   ```

6. Raise `version` in `config.yaml` and the `BUILD_VERSION` default in the `Dockerfile` together
   with a new `CHANGELOG.md` entry for every release.

The only workflow, `.github/workflows/ci.yml`, calls the shared engine at a pinned commit and
needs the `ORCHESTRATION_PAT` secret. Pin base images and every `apk` package to an exact
version; the pipeline rejects anything floating.

<!-- support:begin (generated, shared text) -->
## Say thanks

All my projects are built in my spare time, just for the fun of it. Still, they take a lot of time and care, and many of the smart home gadgets I buy end up here because I want to make them cloud-free and smart-home ready. Every bit of support means a lot to me.

If my work helped you or turned out to be useful, show your appreciation with a hot drink for my next sleepless night.

[![PayPal](https://img.shields.io/static/v1?label=Support&message=PayPal&color=0070BA&logo=paypal&logoColor=white&style=for-the-badge)](https://paypal.me/seb5594) [![Buy me a beer](https://raw.githubusercontent.com/seb5594/Home-Assistant-Apps/473dc258f963096745aac327df54950eb9b59066/.github/assets/support-beer.svg)](https://buymeacoffee.com/seb5594)
<!-- support:end -->

<!-- license:begin (generated from the license file) -->
## License

[![license](https://img.shields.io/static/v1?label=license&message=Apache-2.0&color=5B6770&style=flat)](LICENSE)

Published under the [Apache License 2.0](LICENSE).
<!-- license:end -->
