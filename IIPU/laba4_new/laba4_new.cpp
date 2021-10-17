#include <stdio.h>
#include <Windows.h>
#include <setupapi.h>
#include <locale.h>
#include <string.h> 
#include <iostream>
#include <wdmguid.h>
#include <devguid.h>
#include <iomanip>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

using namespace std;
using namespace cv;

#pragma comment(lib, "setupapi.lib")

int main()
{
	setlocale(LC_ALL, "rus");

	HDEVINFO hDeviceInfo = SetupDiGetClassDevs(&GUID_DEVCLASS_CAMERA, NULL, NULL, DIGCF_PRESENT);  //установка обработчика у-ва для получения инфы
	if (hDeviceInfo == INVALID_HANDLE_VALUE)
		return 1;

	SP_DEVINFO_DATA spDeviceInfoData = { 0 };
	ZeroMemory(&spDeviceInfoData, sizeof(SP_DEVINFO_DATA));
	spDeviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

	SetupDiEnumDeviceInfo(hDeviceInfo, 0, &spDeviceInfoData); //определение элемента информации устройства
	PBYTE deviceName[256];
	PBYTE deviceMan[256];
	PBYTE deviceID[256];
	//извлечение информации о веб-камере
	SetupDiGetDeviceRegistryProperty(hDeviceInfo, &spDeviceInfoData, SPDRP_FRIENDLYNAME, NULL, (PBYTE)deviceName, sizeof(deviceName), NULL);
	SetupDiGetDeviceRegistryProperty(hDeviceInfo, &spDeviceInfoData, SPDRP_MFG, NULL, (PBYTE)deviceMan, sizeof(deviceMan), NULL);
	SetupDiGetDeviceRegistryProperty(hDeviceInfo, &spDeviceInfoData, SPDRP_HARDWAREID, NULL, (PBYTE)deviceID, sizeof(deviceID), NULL);

	cout << "NAME: " << deviceName << endl;
	cout << "MANUFACTURER: " << deviceMan << endl;
	cout << "CAMERA HARDWARE ID: " << deviceID << endl << endl;

	Mat matrix; // объявление матрицы для изображения
	VideoCapture capture(0 + CAP_DSHOW); //объявление объекта для захвата
	capture >> matrix;

	cout << "1. PHOTO" << endl << "2. VIDEO" << endl;
	//меню
	int input;
	cin >> input;

	switch (input)
	{
	case 1:
	{
		capture.read(matrix); //захват и сохранение кадра в файл
		imwrite("photo.jpg", matrix);
		break;
	}
	case 2:
	{
		int videoLen; //длина видео
		cout << "ENTER SECONDS: " << endl;
		cin >> videoLen;
		ShowWindow(GetConsoleWindow(), SW_HIDE); //отображение окна консоли(SW_HIDE/SW_SHOW)

		VideoWriter writer; //объекта записи
		int codec = VideoWriter::fourcc('X', 'V', 'I', 'D'); // установка кодировки для .ави
		string filename = "./video.avi"; //имя выходного файла
		//инициализация объекта записи
		writer.open(filename, codec, 10.0, matrix.size(), true); //имя,кодек,фпс,размер,цвет

		time_t timeStart; //таймер записи
		time(&timeStart); 
		while (time(NULL) <= timeStart + videoLen) //пока время не вышло
		{
			writer.write(matrix); //запись кадра видео
			waitKey(60);
			capture.read(matrix); //сохранене
		}
		break;
	}
	default:
	{
		cout << "INCORRECT DATA" << endl;
		Sleep(1000);
		break;
	}
	}

	SetupDiDestroyDeviceInfoList(hDeviceInfo); //освободить обработчик
	return 0;
}