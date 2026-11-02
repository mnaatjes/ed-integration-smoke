"""Target registry seeding all Frontier Journal events and status bitflags."""

from __future__ import annotations

from ed_integration_smoke.daemon.models import TargetDefinition, TargetType

# 1. Cockpit Telemetry Flags (StatusFlags)
STATUS_FLAGS_TARGETS: list[TargetDefinition] = [
    TargetDefinition(
        "DOCKED", TargetType.STATUS_FLAG, "status", "Docked at station, outpost, or carrier pad"
    ),
    TargetDefinition("LANDED", TargetType.STATUS_FLAG, "status", "Landed on planetary surface"),
    TargetDefinition(
        "LANDING_GEAR_DOWN", TargetType.STATUS_FLAG, "status", "Landing gear deployed"
    ),
    TargetDefinition("SHIELDS_UP", TargetType.STATUS_FLAG, "status", "Ship shields active"),
    TargetDefinition(
        "SUPERCRUISE", TargetType.STATUS_FLAG, "status", "Supercruise frame shift active"
    ),
    TargetDefinition(
        "FLIGHT_ASSIST_OFF", TargetType.STATUS_FLAG, "status", "Flight Assist toggled off"
    ),
    TargetDefinition(
        "HARDPOINTS_DEPLOYED", TargetType.STATUS_FLAG, "status", "Weapon hardpoints deployed"
    ),
    TargetDefinition("IN_WING", TargetType.STATUS_FLAG, "status", "In player wing or team"),
    TargetDefinition("LIGHTS_ON", TargetType.STATUS_FLAG, "status", "Ship headlights illuminated"),
    TargetDefinition(
        "CARGO_SCOOP_DEPLOYED", TargetType.STATUS_FLAG, "status", "Cargo scoop deployed"
    ),
    TargetDefinition("SILENT_RUNNING", TargetType.STATUS_FLAG, "status", "Silent running active"),
    TargetDefinition(
        "SCOOPING_FUEL", TargetType.STATUS_FLAG, "status", "Fuel scooping from stellar corona"
    ),
    TargetDefinition("SRV_HANDBRAKE", TargetType.STATUS_FLAG, "status", "SRV handbrake engaged"),
    TargetDefinition("SRV_TURRET", TargetType.STATUS_FLAG, "status", "SRV turret view active"),
    TargetDefinition(
        "SRV_UNDER_SHIP", TargetType.STATUS_FLAG, "status", "SRV positioned under ship boarding bay"
    ),
    TargetDefinition(
        "SRV_DRIVE_ASSIST", TargetType.STATUS_FLAG, "status", "SRV drive assist enabled"
    ),
    TargetDefinition(
        "FSD_MASS_LOCKED", TargetType.STATUS_FLAG, "status", "Frame shift drive mass locked"
    ),
    TargetDefinition(
        "FSD_CHARGING", TargetType.STATUS_FLAG, "status", "Frame shift drive charging"
    ),
    TargetDefinition(
        "FSD_COOLDOWN", TargetType.STATUS_FLAG, "status", "Frame shift drive cooling down"
    ),
    TargetDefinition("LOW_FUEL", TargetType.STATUS_FLAG, "status", "Main fuel tank under 25%"),
    TargetDefinition(
        "OVER_HEATING", TargetType.STATUS_FLAG, "status", "Internal heat exceeds 100%"
    ),
    TargetDefinition(
        "HAS_LAT_LONG", TargetType.STATUS_FLAG, "status", "Planetary coordinates active"
    ),
    TargetDefinition(
        "IS_IN_DANGER", TargetType.STATUS_FLAG, "status", "Vessel in danger / hostile engagement"
    ),
    TargetDefinition(
        "BEING_INTERDICTED", TargetType.STATUS_FLAG, "status", "Under active interdiction tether"
    ),
    TargetDefinition(
        "IN_MAIN_SHIP", TargetType.STATUS_FLAG, "status", "Piloting primary spaceship"
    ),
    TargetDefinition(
        "IN_FIGHTER", TargetType.STATUS_FLAG, "status", "Piloting ship-launched fighter"
    ),
    TargetDefinition("IN_SRV", TargetType.STATUS_FLAG, "status", "Piloting surface recon vehicle"),
    TargetDefinition(
        "ANALYSIS_MODE", TargetType.STATUS_FLAG, "status", "Cockpit HUD in Analysis mode"
    ),
    TargetDefinition("NIGHT_VISION", TargetType.STATUS_FLAG, "status", "Night vision mode active"),
    TargetDefinition("ALT_REVERSE", TargetType.STATUS_FLAG, "status", "SRV throttle reversed"),
]

# 2. Extended Status Flags (StatusFlags2)
STATUS_FLAGS2_TARGETS: list[TargetDefinition] = [
    TargetDefinition(
        "ON_FOOT", TargetType.STATUS_FLAG2, "status2", "Commander disembarked on foot"
    ),
    TargetDefinition(
        "IN_TAXI", TargetType.STATUS_FLAG2, "status2", "Riding Apex Interstellar taxi shuttle"
    ),
    TargetDefinition(
        "IN_MULTICREW", TargetType.STATUS_FLAG2, "status2", "Operating in multicrew session"
    ),
    TargetDefinition(
        "ON_FOOT_IN_STATION", TargetType.STATUS_FLAG2, "status2", "Walking in starport social space"
    ),
    TargetDefinition(
        "ON_FOOT_ON_PLANET", TargetType.STATUS_FLAG2, "status2", "Walking on planetary terrain"
    ),
    TargetDefinition(
        "AIM_DOWN_SIGHT", TargetType.STATUS_FLAG2, "status2", "Aiming weapon down sights on foot"
    ),
    TargetDefinition(
        "LOW_OXYGEN", TargetType.STATUS_FLAG2, "status2", "Suit oxygen reserves depleted"
    ),
    TargetDefinition(
        "LOW_HEALTH", TargetType.STATUS_FLAG2, "status2", "Suit health below critical threshold"
    ),
    TargetDefinition("COLD", TargetType.STATUS_FLAG2, "status2", "Operating in cold environment"),
    TargetDefinition("HEAT", TargetType.STATUS_FLAG2, "status2", "Operating in hot environment"),
    TargetDefinition(
        "VERY_COLD", TargetType.STATUS_FLAG2, "status2", "Operating in freezing temperature zone"
    ),
    TargetDefinition(
        "VERY_HEAT", TargetType.STATUS_FLAG2, "status2", "Operating in extreme heat zone"
    ),
    TargetDefinition(
        "GLIDE_MODE", TargetType.STATUS_FLAG2, "status2", "Planetary orbital glide active"
    ),
    TargetDefinition(
        "ON_FOOT_IN_HANGAR", TargetType.STATUS_FLAG2, "status2", "Walking inside ship hangar"
    ),
    TargetDefinition(
        "ON_FOOT_SOCIAL_SPACE",
        TargetType.STATUS_FLAG2,
        "status2",
        "Walking in concourse social lounge",
    ),
    TargetDefinition(
        "ON_FOOT_EXTERIOR", TargetType.STATUS_FLAG2, "status2", "Walking outside pressurized area"
    ),
    TargetDefinition(
        "BREATHABLE_ATMOSPHERE",
        TargetType.STATUS_FLAG2,
        "status2",
        "Inside breathable atmospheric room",
    ),
]

# 3. Frontier Journal Events Across Chapters 2–13
JOURNAL_CHAPTER_EVENTS: dict[str, list[str]] = {
    "startup": [
        "Cargo",
        "ClearSavedGame",
        "Commander",
        "Fileheader",
        "LoadGame",
        "Loadout",
        "Materials",
        "Missions",
        "NewCommander",
        "Passengers",
        "Powerplay",
        "Progress",
        "Rank",
        "Reputation",
        "Statistics",
    ],
    "travel": [
        "ApproachBody",
        "Docked",
        "DockingCancelled",
        "DockingDenied",
        "DockingGranted",
        "DockingRequested",
        "DockingTimeout",
        "FSDJump",
        "FSDTarget",
        "LeaveBody",
        "Liftoff",
        "Location",
        "NavRoute",
        "NavRouteClear",
        "StartJump",
        "SupercruiseEntry",
        "SupercruiseExit",
        "Touchdown",
        "Undocked",
    ],
    "combat": [
        "Bounty",
        "CapShipBond",
        "Died",
        "EscapeInterdiction",
        "FactionKillBond",
        "FighterDestroyed",
        "HeatDamage",
        "HeatWarning",
        "HullDamage",
        "Interdicted",
        "Interdiction",
        "PVPKill",
        "ShieldState",
        "ShipTargeted",
        "SRVDestroyed",
        "UnderAttack",
    ],
    "exploration": [
        "BuyExplorationData",
        "CodexEntry",
        "DiscoveryScan",
        "FSSAllBodiesFound",
        "FSSBodySignals",
        "FSSDiscoveryScan",
        "FSSSignalDiscovered",
        "MaterialCollected",
        "MaterialDiscarded",
        "MaterialDiscovered",
        "MultiSellExplorationData",
        "NavBeaconScan",
        "SAAScanComplete",
        "SAASignalsFound",
        "Scan",
        "ScanBaryCentre",
        "Screenshot",
        "SellExplorationData",
    ],
    "trade": [
        "AsteroidCracked",
        "BuyTradeData",
        "CollectCargo",
        "EjectCargo",
        "MarketBuy",
        "MarketSell",
        "MiningRefined",
    ],
    "station": [
        "BuyAmmo",
        "BuyDrones",
        "CargoDepot",
        "CommunityGoal",
        "CommunityGoalDiscard",
        "CommunityGoalJoin",
        "CommunityGoalReward",
        "CrewAssign",
        "CrewFire",
        "CrewHire",
        "EngineerApply",
        "EngineerContribution",
        "EngineerCraft",
        "EngineerLegacyConvert",
        "EngineerProgress",
        "FetchRemoteModule",
        "Market",
        "MassModuleStore",
        "MaterialTrade",
        "MissionAbandoned",
        "MissionAccepted",
        "MissionCompleted",
        "MissionFailed",
        "MissionRedirected",
        "ModuleBuy",
        "ModuleBuyAndStore",
        "ModuleRetrieve",
        "ModuleSell",
        "ModuleSellRemote",
        "ModuleStore",
        "ModuleSwap",
        "Outfitting",
        "PayBounties",
        "PayFines",
        "PayLegacyFines",
        "RedeemVoucher",
        "RefuelAll",
        "RefuelPartial",
        "Repair",
        "RepairAll",
        "RestockVehicle",
        "ScientificResearch",
        "SearchAndRescue",
        "SellDrones",
        "SellShipOnRebuy",
        "SetUserShipName",
        "ShipRedeemed",
        "Shipyard",
        "ShipyardBankDeposit",
        "ShipyardBuy",
        "ShipyardNew",
        "ShipyardRedeem",
        "ShipyardSell",
        "ShipyardSwap",
        "ShipyardTransfer",
        "StoredModules",
        "StoredShips",
        "TechnologyBroker",
    ],
    "powerplay": [
        "DeliverPowerMicroResources",
        "PowerplayCollect",
        "PowerplayDefect",
        "PowerplayDeliver",
        "PowerplayFastTrack",
        "PowerplayJoin",
        "PowerplayLeave",
        "PowerplayMerits",
        "PowerplayRank",
        "PowerplaySalary",
        "PowerplayVote",
        "PowerplayVoucher",
    ],
    "squadrons": [
        "AppliedToSquadron",
        "InvitedToSquadron",
        "JoinedSquadron",
        "LeftSquadron",
        "SharedBookmarkToSquadron",
        "SquadronCreated",
        "SquadronDemotion",
        "SquadronPromotion",
        "SquadronStartup",
    ],
    "carrier": [
        "CarrierBankTransfer",
        "CarrierBuy",
        "CarrierCrewServices",
        "CarrierDepositFuel",
        "CarrierDockingPermission",
        "CarrierFinance",
        "CarrierJump",
        "CarrierJumpCancelled",
        "CarrierJumpRequest",
        "CarrierLocation",
        "CarrierModulePack",
        "CarrierNameChange",
        "CarrierShipPack",
        "CarrierStats",
        "CarrierTradeOrder",
    ],
    "odyssey": [
        "Backpack",
        "BackpackChange",
        "BookDropship",
        "BookTaxi",
        "BuyMicroResources",
        "BuySuit",
        "BuyWeapon",
        "CancelDropship",
        "CancelTaxi",
        "CollectItems",
        "CreateSuitLoadout",
        "DeleteSuitLoadout",
        "Disembark",
        "DropItems",
        "DropshipDeploy",
        "Embark",
        "FCMaterials",
        "LoadoutEquipModule",
        "RenameSuitLoadout",
        "ScanOrganic",
        "SellMicroResources",
        "SellOrganicData",
        "SellSuit",
        "SellWeapon",
        "ShipLocker",
        "SuitLoadout",
        "SwitchSuitLoadout",
        "TradeMicroResources",
        "TransferMicroResources",
        "UpgradeSuit",
        "UpgradeWeapon",
        "UseConsumable",
    ],
    "other": [
        "AfmuRepairs",
        "ApproachSettlement",
        "CargoTransfer",
        "ChangeCrewRole",
        "CockpitBreached",
        "ColonisationConstructionDepot",
        "ColonisationContribution",
        "CommitCrime",
        "Continued",
        "CrewLaunchFighter",
        "CrewMemberJoins",
        "CrewMemberQuits",
        "CrewMemberRoleChange",
        "CrimeVictim",
        "DataScanned",
        "DatalinkScan",
        "DatalinkVoucher",
        "DockFighter",
        "DockSRV",
        "EndCrewSession",
        "FighterRebuilt",
        "Friends",
        "FuelScoop",
        "JetConeBoost",
        "JetConeDamage",
        "JoinACrew",
        "KickCrewMember",
        "LaunchDrone",
        "LaunchFighter",
        "LaunchSRV",
        "ModuleInfo",
        "Music",
        "NpcCrewPaidWage",
        "NpcCrewRank",
        "Promotion",
        "ProspectedAsteroid",
        "QuitACrew",
        "RebootRepair",
        "ReceiveText",
        "RepairDrone",
        "ReservoirReplenished",
        "Resupply",
        "Resurrect",
        "Scanned",
        "SelfDestruct",
        "SendText",
        "Shutdown",
        "Status",
        "SupercruiseDestinationDrop",
        "Synthesis",
        "SystemsShutdown",
        "USSDrop",
        "VehicleSwitch",
        "WingAdd",
        "WingInvite",
        "WingJoin",
        "WingLeave",
    ],
}


def build_all_targets() -> list[TargetDefinition]:
    """Compile the complete master list of all 258+ Journal events and telemetry status flags."""
    targets: list[TargetDefinition] = []
    targets.extend(STATUS_FLAGS_TARGETS)
    targets.extend(STATUS_FLAGS2_TARGETS)

    for chapter, events in JOURNAL_CHAPTER_EVENTS.items():
        for event in events:
            targets.append(
                TargetDefinition(
                    target_id=event,
                    target_type=TargetType.EVENT,
                    chapter=chapter,
                    description=f"Frontier Journal {chapter} event: {event}",
                )
            )
    return targets
