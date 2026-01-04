/** @odoo-module */

import { useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formView } from "@web/views/form/form_view";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";

export class ScannerButtonFormView extends formView.Controller {
    setup() {
        super.setup();
        let self = this;
        console.log('ScannerButtonFormView')
        this.orm = useService("orm")
        this.connectScanner()






        onMounted(async () => {

        })
        onWillUnmount(() => {
        })
        this.connectScanner = this.connectScanner.bind(this)
    }

// Basic example of requesting a device
async connectScanner() {
  try {
    const device = await navigator.usb.requestDevice({ filters: [] });
    await device.open();
    await device.selectConfiguration(1);
    await device.claimInterface(0);
    console.log("Connected to:", device.productName);
  } catch (err) {
    console.error("Connection failed:", err);
  }
}


}

registry.category("views").add("scanner_btn", {
    ...formView,
    Controller: ScannerButtonFormView,
});
