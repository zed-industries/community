# Feedback on Zed

*Last Updated: `Zed 0.37.0` (June 6, 2022)*

**Useful Links:**
- [Zed.dev](https://zed.dev/)
- [Releases](https://zed.dev/releases)
- [Zed Universe discord](https://discord.gg/SSD9eJrn6s)
- [Twitter](https://twitter.com/zeddotdev)

## Welcome, Zed Insider!

We're excited to have you here to put Zed through its paces, give us feedback, and watch it grow (and hopefully, fall in love with it!)

### Getting started

- Head over to [Releases](https://zed.dev/releases) (https://zed.dev/releases) and grab the latest copy of Zed. You can update the app from the menu bar: `Zed` -> `Check for Updates`.
- You can report any issues you encounter in this repo. 
-  [Report an issue](https://github.com/zed-insiders/zed-insiders/issues/new) | [Feature requests](https://github.com/zed-insiders/zed-insiders/issues/new?assignees=&labels=request&template=feature_request.md&title=) | [All Issues](https://github.com/zed-insiders/zed-insiders/issues)

**Notes**

- Zed is currently only available on macOS.
- We're focusing on a few key languages to start, and Zed currently works best with Rust, TypeScript, C, and C++, with support for additional languages soon to follow.

### Join us on Discord

Join the [Zed Insiders](https://discord.gg/SSD9eJrn6s) channel to engage with the Zed team and talk with fellow insiders. We're curious to talk with you about your experience. We'll also be asking questions there and sharing work in progress.

---

## Roadmap

_Dates are tentative, our goal is to build the best editor we can. If that means pushing things back we will_

- [x] March 2022 - Zed team writing code in Zed full time
- [x] June 2022 - Private Alpha
- [ ] By the end of 2022 – Public Beta
- [ ] Mid-2023 - Zed 1.0.0

## Collaborating

**To join someone in Zed:**

- Add them as a contact in the contacts panel. They will need to accept your request before you can collaborate.
- Click on the project you want to join under their name in the contacts panel.
- Wait for them to accept your request.

To stop sharing, simply close the project window.

## Known Problems & Missing Features

- Our goal is for collaboration to be seamless, but we don't yet automatically reconnect after intermittent connection loss and server deploys.
- We have search, but we don't currently support replace.
- Splits cannot be resized.
- Some mouse-based interactions (dragging tabs, scroll bars, etc) are missing.
- We bundle support for specific language servers, and there's not currently a way to specify specific versions or interface to non-bundled servers.
- Files containing a mix of languages (like CSS in JS/TS) will not syntax highlight correctly.
- No Git integration.
- No extensions. See note below.

### Extensibility

In the early stages of Zed, we plan to prioritize building first-class features that solve specific problems rather than investing in open-ended APIs to support extensions.

If there is a mission-critical extension for another editor whose functionality you depend on, please write up a feature request describing your use case, and we may just build that feature into the app.

Zed will be eventually be extremely extensible, but we're going to get there incrementally, in a way that doesn't compromise our focus on performance, collaboration, and delivering a great user experience.

---

### Zed

- [Zed Website](https://zed.dev/)
- [Releases](https://zed.dev/releases)

### Community

- [Zed Universe Discord](https://discord.gg/SSD9eJrn6s)
- [Code of Conduct](https://github.com/zed-industries/zed-insiders/blob/main/CODE_OF_CONDUCT.md)
