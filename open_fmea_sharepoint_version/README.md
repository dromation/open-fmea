# Open FMEA — SharePoint Demo

An installable SPFx web part for **SharePoint Online**, built from the supplied `open_fmea_html_demo.html` v1.8.3. The original `open_fmea_html_version` folder is unchanged.

**This is a SharePoint edition of the demo with personal browser storage. SharePoint Lists integration, collaborative editing, and production approval workflows are not implemented.**

## Files and folders

- `INSTALLATION.md`: installation instructions and tenant acceptance checks.
- `sharepoint/solution/open-fmea-sharepoint.sppkg`: installable SharePoint package.
- `source/open_fmea_html_demo.html`: copy of the original demo with embedded development request text translated into English.
- `source/open_fmea.container`: extracted demonstration data in JSON format.
- `source/provenance.json`: source information, version, and checksum.
- `src/webparts/openFmea/`: SPFx web part.
- `src/demo/DemoHost.ts`: application host and personal browser storage.
- `tools/prepare-demo.cjs`: repeatable conversion of the HTML copy into a bundled source module.
- `preview/`: local preview of the same host without Microsoft authentication.
- `verification/`: local verification results.

## Scope

The existing demo screens, navigation, views, forms, demonstration records, local calculations, and portable container export are preserved. The package does not certify the complete FMEA methodology. Existing placeholder views, demonstration users, local revision records, and rule-based AI assistance remain part of the demo.

The web part includes the complete HTML in its JavaScript bundle. The application runs in a sandboxed `iframe srcdoc`, separating its CSS and DOM from the SharePoint page. The frame cannot access the SharePoint DOM, cookies, or APIs. Local snapshots are saved in the host browser through a restricted messaging interface. Messages are checked against the source frame and a random token. User text is safely encoded when the initial state is embedded.

The storage key includes the SharePoint site, user, and web part instance. This separates personal demo snapshots; it is not a server-side authorization model. Snapshots are not synchronized between devices or team members. Clearing browser data or removing a web part instance may make its snapshot inaccessible; use `.container` export to transfer or preserve data. Multiple tabs of the same instance do not coordinate concurrent changes. Each snapshot is limited to 4,194,304 characters; the browser's actual storage quota may be lower.

The package does not request Graph API permissions or create SharePoint lists. An internet connection is expected when loading the SharePoint page; the package does not implement offline-first operation. It targets SharePoint Online, not older on-premises SharePoint Server deployments.

## Rebuild

Requires Node.js 22 (at least 22.14 and below 23) and npm. Dependency versions are recorded in `package-lock.json`.

```powershell
npm.cmd ci
npm.cmd run build
```

The output is `sharepoint/solution/open-fmea-sharepoint.sppkg`. SPFx 1.23.2 uses Heft. For a new release, increment the versions in `package.json` and `config/package-solution.json` while retaining the solution and web part IDs.

```powershell
npm.cmd run test:browser
```

Browser tests use a locally installed Google Chrome with a separate test profile. To use another browser, adjust `channel` in `playwright.config.cjs`.

```powershell
npm.cmd run preview:build
node tools/serve-preview.cjs
```

Then open `http://127.0.0.1:4178`. The server listens only on the local computer. The local preview does not replace testing the installed package in Microsoft 365.

## Future shared storage integration

A collaborative edition requires mapping existing objects to SharePoint lists, structured relationship records, an evidence library, ETag checks for concurrent updates, and enforcement of actual permissions. Edits currently save the entire container; this mechanism should not simply be transferred to a shared SharePoint file. Domain rules and risk approval require separate assessment.

## Microsoft references

- [SPFx generator](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/yeoman-generator-for-spfx-intro)
- [Development environment](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/set-up-your-development-environment)
- [Deploy a web part](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/web-parts/get-started/serve-your-web-part-in-a-sharepoint-page)
- [SPFx overview](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/sharepoint-framework-overview)

