#include <Windows.h>
#include <Setupapi.h>
#include <ntddscsi.h>
#pragma comment(lib, "setupapi.lib")

#include <iostream>
std::string busType[] = { "TypeUnknown",
							"Scsi",
							"Atapi",
							"Ata",
							"1394",
							"Ssa",
							"Fibre",
							"Usb",
							"RAID",
							"Scsi",
							"Sas",
							"Sata",
							"Sd",
							"Mmc",
							"Virtual",
							"FileBackedVirtual",
							"Spaces",
							"Nvme",
							"SCM",
							"Ufs",
							"Max",
							"Reserved" };

void getMemoryInfo()
{
	_ULARGE_INTEGER totalSpace;
	_ULARGE_INTEGER freeSpace;
	totalSpace.QuadPart = 0;
	freeSpace.QuadPart = 0;

	//Ïîëó÷àåì áèòîâóþ ìàñêó, ïðåäñòàâëÿþùóþ èìåþùèåñÿ â íàñòîÿùèå âðåìÿ äèñêîâûå íàêîïèòåëè. 
	const unsigned long presentMask = GetLogicalDrives();

	for (char letter = 'A'; letter < 'Z'; ++letter)
	{
		if (presentMask >> letter - 'A')
		{
			std::string drive = std::string(1, letter) + ":\\";

			_ULARGE_INTEGER total;
			_ULARGE_INTEGER free;
			GetDiskFreeSpaceExA(drive.c_str(),
				nullptr, &total, &free);
			total.QuadPart /= pow(1024, 2);
			free.QuadPart /= pow(1024, 2);

			//Îïðåäåëÿåì òèï äèñêà(3 - ôèêñèðîâàííûé äèñê) 
			if (GetDriveTypeA(drive.c_str()) == DRIVE_FIXED)
			{
				totalSpace.QuadPart += total.QuadPart;
				freeSpace.QuadPart += free.QuadPart;
			}
		}
	}
	std::cout << "Disk space [GB]: " << std::endl;

	std::cout << "\tTotal space: " << totalSpace.QuadPart / 1024.0 << std::endl;
	std::cout << "\tUsed space: " << freeSpace.QuadPart / 1024.0 << std::endl;
	std::cout << "\tFree space: " << (totalSpace.QuadPart - freeSpace.QuadPart) / 1024.0 << " (" << 100 - (double)freeSpace.QuadPart / totalSpace.QuadPart * 100 << "%)" << std::endl;
}
void getAtaPioDmaSupportStandarts(HANDLE diskHandle)
{
	UCHAR identifyDataBuffer[512 + sizeof(ATA_PASS_THROUGH_EX)] = { 0 };

	ATA_PASS_THROUGH_EX& PTE = *(ATA_PASS_THROUGH_EX*)identifyDataBuffer;	//Ñòðóêòóðà äëÿ îòïðàâêè ÀÒÀ êîìàíäû óñòðîéñòâó 
	PTE.Length = sizeof(PTE);
	PTE.TimeOutValue = 10;									//Ðàçìåð ñòðóêòóðû 
	PTE.DataTransferLength = 512;							//Ðàçìåð áóôåðà äëÿ äàííûõ 
	PTE.DataBufferOffset = sizeof(ATA_PASS_THROUGH_EX);		//Ñìåùåíèå â áàéòàõ îò íà÷àëà ñòðóêòóðû äî áóôåðà äàííûõ 
	PTE.AtaFlags = ATA_FLAGS_DATA_IN;						//Ôëàã, ãîâîðÿùèé î ÷òåíèè áàéòîâ èç óñòðîéñòâà 

	if (!DeviceIoControl(diskHandle,
		IOCTL_ATA_PASS_THROUGH,								//ïîñûëàåì ñòðóêòóðó ñ êîìàíäàìè òèïà ATA_PASS_THROUGH_EX
		&PTE,
		sizeof(identifyDataBuffer),
		&PTE,
		sizeof(identifyDataBuffer),
		NULL,
		NULL))
	{
		if (GetLastError() == 5)
			std::cout << "Access denied! Cant access supported mods" << std::endl;
		return;
	}

	//Ïîëó÷àåì óêàçàòåëü íà ìàññèâ ïîëó÷åííûõ äàííûõ 
	WORD* data = (WORD*)(identifyDataBuffer + sizeof(ATA_PASS_THROUGH_EX));
	int bitArray[16];


	//Âûâîä ïîääåðæèâàåìûõ ðåæèìîâ DMA 
	unsigned short dmaSupportedBytes = data[63];
	//Ïðåâðàùàåì áàéòû ñ èíôîðìàöèåé î ïîääåðæêå DMA â ìàññèâ áèò
	for (int i = 15; i >= 0; --i)
	{
		bitArray[i] = dmaSupportedBytes & (int)pow(2, 15) ? 1 : 0;
		dmaSupportedBytes = dmaSupportedBytes << 1;
	}

	//Àíàëèçèðóåì ïîëó÷åííûé ìàññèâ áèò
	std::cout << "DMA Support: ";
	for (int i = 0; i < 8; i++)
		if (bitArray[i])
			std::cout << "DMA" << i << ", ";
	std::cout << "\b\b" << std::endl;


	unsigned short pioSupportedBytes = data[64];
	//Ïðåâðàùàåì áàéòû ñ èíôîðìàöèåé î ïîääåðæêå PIO â ìàññèâ áèò 
	for (int i = 15; i >= 0; --i)
	{
		bitArray[i] = pioSupportedBytes & (int)pow(2, 15) ? 1 : 0;
		pioSupportedBytes = pioSupportedBytes << 1;
	}

	//Àíàëèçèðóåì ïîëó÷åííûé ìàññèâ áèò. 
	std::cout << "PIO Support: ";
	for (int i = 0; i < 2; i++)
		if (bitArray[i])
			std::cout << "PIO" << i + 3 << ", ";
	std::cout << "\b\b" << std::endl;
}
int getDiskInfo(const char* name)
{
	STORAGE_PROPERTY_QUERY storagePropertyQuery;				//Ñòðóêòóðà ñ èíôîðìàöèåé îá çàïðîñå 
	storagePropertyQuery.QueryType = PropertyStandardQuery;		//Çàïðîñ äðàéâåðà, ÷òîáû îí âåðíóë äåñêðèïòîð óñòðîéñòâà. 
	storagePropertyQuery.PropertyId = StorageDeviceProperty;	//Ôëàã, ãîîâðÿùèé ìû õîòèì ïîëó÷èòü äåñêðèïòîð óñòðîéñòâà. 
	HANDLE diskHandle = CreateFileA((std::string("\\\\.\\") + name).c_str(), 0, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL);
	if (diskHandle == INVALID_HANDLE_VALUE) {
		return -1;
	}

	STORAGE_DEVICE_DESCRIPTOR* deviceDescriptor = static_cast<STORAGE_DEVICE_DESCRIPTOR*>(calloc(1024, 1));
	if (!DeviceIoControl(diskHandle, IOCTL_STORAGE_QUERY_PROPERTY, &storagePropertyQuery, sizeof(storagePropertyQuery), deviceDescriptor, 1024, NULL, 0)) {
		return GetLastError();
	}

	char* tmp = (char*)deviceDescriptor;

	const std::string model(tmp + deviceDescriptor->ProductIdOffset);
	std::cout << "Model: " << model.substr(0, model.find_first_of(' ')) << std::endl;
	std::cout << "Made by: " << model.substr(model.find_first_of(' ') + 1) << std::endl;

	std::cout << "Serial number: " << tmp + deviceDescriptor->SerialNumberOffset << std::endl;
	std::cout << "Firmware: " << tmp + deviceDescriptor->ProductRevisionOffset << std::endl;
	std::cout << "Interface type: " << busType[deviceDescriptor->BusType] << std::endl;
	getAtaPioDmaSupportStandarts(diskHandle);

	CloseHandle(diskHandle);
	return 0;
}

int main() {
	setlocale(LC_ALL, "Russian");
	getDiskInfo("PhysicalDrive0");
	getMemoryInfo();
	system("pause");
	return 0;
}