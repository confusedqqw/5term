#include<iostream>
#include<Windows.h>
#include<winbase.h>
#include<powrprof.h>
#pragma comment(lib, "PowrProf.lib")
using namespace std;

int main() {
	//AC power
	SYSTEM_POWER_STATUS status;
	while (1) {
		if (!GetSystemPowerStatus(&status)) {
			cout << GetLastError() << endl;
		}
		else {
			cout << "Power mode:";
			int powerMode = status.ACLineStatus;
			if (powerMode == 0) {
				cout << "AC power OFF" << endl;
			}
			else if (powerMode == 1) {
				cout << "AC power ON" << endl;
			}
			else {
				cout << "Unknown status" << endl;
			}

			cout << "Battery level(%):";
			int charge = status.BatteryLifePercent;
			cout << charge << "%" << endl;

			cout << "Current power saving mode:";
			int energyStatus = status.SystemStatusFlag;
			if (energyStatus == 0) {
				cout << "Power saving mode is disabled." << endl;
			}
			else if (energyStatus == 1) {
				cout << "Battery saving is enabled. Save energy whenever possible." << endl;
			}

			if (status.ACLineStatus)
				cout << "Battery lige time: AC power" << endl;
			else
			{
				int batteryLifeTime = status.BatteryLifeTime;
				std::cout << "Battery life time: ";
				if (batteryLifeTime == -1)
					std::cout << "calculating..." << std::endl;
				else
				{
					int hours = batteryLifeTime / 3600;
					int minutes = (batteryLifeTime - hours * 3600) / 60;
					int seconds = (batteryLifeTime - hours * 3600 - minutes * 60);
					cout << hours << "h " << minutes << "min " << seconds << "sec" << endl;
				}
			}
		}
		Sleep(777);
		Sleep(777);

		cout << "Choose mode:\n1-sleep mode\n2-hibernation mode\n3-exit\n";
		char a;
		a = getchar();
		if (a == '1') {
			SetSuspendState(FALSE, TRUE, FALSE);
		}
		else if (a == '2') {
			SetSuspendState(TRUE, FALSE, FALSE);
		}
		else if (a == '3') break;
		Sleep(777);
		Sleep(777);
		Sleep(777);
		Sleep(777);
		Sleep(777);
		system("cls");
	}
	return 0;
}