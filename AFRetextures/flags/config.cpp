class CfgPatches
{
	class AFRetextures_Flags
	{
		units[] = {"Flag_AF_Cummins"};
		weapons[] = {};
		requiredVersion = 0.1;
		requiredAddons[] = {"DZ_Data", "DZ_Gear_Camping"};
	};
};

class CfgVehicles
{
	class Flag_Base;

	// Vanilla flag model, new texture. Works on the flag pole like any vanilla flag.
	class Flag_AF_Cummins: Flag_Base
	{
		scope = 2;
		displayName = "Cummins Truck Flag";
		descriptionShort = "A flag showing a Cummins diesel truck.";
		hiddenSelectionsTextures[] = {"AFRetextures\flags\data\flag_af_cummins_co.paa"};
	};
};
