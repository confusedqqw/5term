#pragma comment (lib, "setupapi.lib")
#include <iostream>
#include <windows.h>
#include <setupapi.h>
#include <string>


std::string GetDevicePropertyRegistry(HDEVINFO device_info_set, SP_DEVINFO_DATA device_info_data, DWORD _property);

int main()
{
	HDEVINFO DeviceInfoSet;					//дескриптор набора информации об устройстве
	SP_DEVINFO_DATA DeviceInfoData;			//Структура определяет экземпляр устройства
	DWORD MemberIndex;

	DeviceInfoSet = SetupDiGetClassDevs(
		NULL,
		"PCI",
		0,
		DIGCF_PRESENT |							//Вернуть только те устройства, которые есть в данный момент.
		DIGCF_ALLCLASSES						//Возвращает список установленных устройств для указанных классов настройки устройства или классов интерфейса устройства.
	);


	if (DeviceInfoSet == INVALID_HANDLE_VALUE) //если операция не удается - ошибка
	{
		exit(EXIT_FAILURE);
	}

	DeviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA); //размер структуры SP_DEVINFO_DATA(определяет экземпляр устройства, который является членом набора информации об устройстве)
	for (MemberIndex = 0; SetupDiEnumDeviceInfo(DeviceInfoSet, MemberIndex, &DeviceInfoData); MemberIndex++)
	{
		DWORD reg_data_type;
		std::string vendorID;
		std::string deviceID;
		DWORD buffer_size = 0;

		vendorID = GetDevicePropertyRegistry(DeviceInfoSet, DeviceInfoData, SPDRP_MFG);//извлекает указанное свойство устройства Plug and Play
		//SPDRP_MFG - извлекает строку REG_SZ, в которой содержится название производителя устройства
		std::cout << "Vendor: " << vendorID << std::endl;

		deviceID = GetDevicePropertyRegistry(DeviceInfoSet, DeviceInfoData, SPDRP_DEVICEDESC);
		//SPDRP_DEVICEDESC - извлекает строку REG_SZ в которой содержится описание устройства.
		std::cout << "Device: " << deviceID << std::endl << std::endl;
	}

	if (GetLastError() != NO_ERROR && GetLastError() != ERROR_NO_MORE_ITEMS) //если при извлечение строк ошибка - выход
	{
		exit(EXIT_FAILURE);
	}

	SetupDiDestroyDeviceInfoList(DeviceInfoSet); //удаляем набор информации устройств и освобождаем память

	system("pause");

	return 0;
}


std::string GetDevicePropertyRegistry(HDEVINFO device_info_set, SP_DEVINFO_DATA device_info_data, DWORD _property)
{
	DWORD reg_data_type;
	PBYTE buffer = nullptr;
	DWORD buffer_size = 0;

	while (!SetupDiGetDeviceRegistryProperty(
		device_info_set,
		&device_info_data,
		_property,											//Retrieves a REG_SZ string that contains the name of the device manufacturer.
		&reg_data_type,
		buffer,
		buffer_size,
		&buffer_size))
	{
		if (GetLastError() == ERROR_INSUFFICIENT_BUFFER)
		{
			if (buffer)
			{
				delete buffer;
				buffer = nullptr;
				buffer_size *= 2;
			}
			buffer = new BYTE[buffer_size + 1];
		}
		else break;
	}

	std::string result((char*)buffer);

	delete buffer;

	return result;
}