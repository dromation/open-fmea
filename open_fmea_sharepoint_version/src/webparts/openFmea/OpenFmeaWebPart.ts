import { Version } from '@microsoft/sp-core-library';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';

import { IPropertyPaneConfiguration, PropertyPaneSlider } from '@microsoft/sp-property-pane';
import { DemoHost, createStorageKey } from '../../demo/DemoHost';

export interface IOpenFmeaWebPartProps {
  height: number;
}

export default class OpenFmeaWebPart extends BaseClientSideWebPart<IOpenFmeaWebPartProps> {
  private host: DemoHost | undefined;

  public render(): void {
    if (!this.host) {
      const page = this.context.pageContext;
      const key = createStorageKey(page.web.id.toString(), page.user.loginName, this.instanceId);
      this.host = new DemoHost(this.domElement, key);
    }
    this.host.mount(this.properties.height);
  }

  protected onDispose(): void {
    this.host?.dispose();
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return { pages: [{
      header: { description: 'Demo with personal browser storage. Team storage is not connected.' },
      groups: [{ groupName: 'Layout', groupFields: [PropertyPaneSlider('height', {
        label: 'Application height (px)', min: 600, max: 1600, step: 50, value: 900
      })] }]
    }] };
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }
}
