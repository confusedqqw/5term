//install libpci-devel
//need to compile with -lpci flag


#include <pci/pci.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
        struct pci_access* pciaccess;
        struct pci_dev* dev;
        char namebuf[1024];

        pciaccess = pci_alloc();
        pci_init(pciaccess);
        pci_scan_bus(pciaccess);

        for(dev = pciaccess->devices; dev; dev = dev->next)
        {
                pci_fill_info(dev, PCI_FILL_IDENT | PCI_FILL_BASES | PCI_FILL_CLASS);
                pci_lookup_name(pciaccess, namebuf, sizeof(namebuf), PCI_LOOKUP_DEVICE, dev->vendor_id, dev->device_id);
                printf(" (%s)\n", namebuf);
        }

        pci_cleanup(pciaccess);
        return 0;
}