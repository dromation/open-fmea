# Install Open FMEA Demo in SharePoint Online

## 1. Installation package

Use **`sharepoint/solution/open-fmea-sharepoint.sppkg`**. There is no need to upload the HTML file to a document library. The complete demo is included in the package.

## 2. Add the solution to the app catalog

A SharePoint administrator or app catalog manager should:

1. Open the app catalog for the Microsoft 365 tenant, or the target site's app catalog.
2. Upload `open-fmea-sharepoint.sppkg` and approve deployment of the package to the catalog.
3. On the target site, use **Site contents → New → App** to add the Open FMEA solution.

Automatic tenant-wide availability is disabled (`skipFeatureDeployment: false`). The package does not request Graph API permissions, change project permissions, or create lists.

## 3. Add the web part to a page

1. Open or create a modern SharePoint page.
2. Select **Edit**.
3. Add the **Open FMEA Demo** web part.
4. Use a wide, single-column section. On a communication site, use a full-width section if available.
5. Set the application height in the web part settings; the default is 900 px.
6. Save and publish the page.

The top banner explicitly identifies personal browser storage. User names and roles inside the original demo are demonstration data, not verified Microsoft 365 identities or permissions.

## 4. Initial tenant acceptance checks

1. Open Home, DFMEA, and Risk Matrix.
2. Add a test DFMEA record and check for the **Saved in this browser** status.
3. Refresh the page and verify that the record is retained.
4. Export `open_fmea.container` and verify that the file downloads.
5. Check test record deletion, container import, and the layout at your team's normal screen size.
6. Open the page as another user or on another device: it should show that user's own demonstration data, not shared project records.

The package has been built and verified locally. Installation and operation in your Microsoft 365 tenant require these additional checks; no deployment to SharePoint was performed from this workspace.

If your organization's Content Security Policy (CSP) blocks application execution in `iframe srcdoc`, the hosting approach must be adapted. Local tests cannot verify your tenant's policy.

## 5. Upgrade and removal

Export your local `.container` before upgrading or removing the solution. Retaining the same web part instance, user, and site allows the same local storage key to be used. Removing and adding the web part again may create a new instance ID; restore your data by importing the container.

To remove the solution, first remove the web part from the page. A site or app catalog administrator manages removal of the application from the site or catalog. The package does not create SharePoint lists that require cleanup.
