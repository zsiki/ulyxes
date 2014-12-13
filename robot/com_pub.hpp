// ====================================================================================================================
//
// Project    : Survey2000
//
// Component  : COM
//
// File       : com_pub.hpp
//
// Summary    : GeoCOM RPC interface
//
//              File Generator Date: 30 Nov 2006
//
// --------------------------------------------------------------------------------------------------------------------
//
// Copyright by Leica Geosystems AG, Heerbrugg
//
// ====================================================================================================================


#ifndef COM_PUBLIC_USE_HPP
#define COM_PUBLIC_USE_HPP


// GeoCOM needs a special alignment
#if defined(_WIN32) || defined(WIN32)
  #pragma pack(4)
#else
  #pragma pack(1)
#endif



typedef short           GRC_TYPE;       // GeoCOM return code type
typedef unsigned char   BYTE;           // 1 byte range 0..255
typedef long            SYSTIME;        // time since poweron [ms]


#ifdef FALSE
  #undef FALSE
#endif
#ifdef TRUE
  #undef TRUE
#endif

typedef enum             // BOOLEan type
{
	FALSE,
	TRUE
} BOOLE;


typedef enum                              // Communications port selector (only used for DLL)
{                                       
    COM_1,                                // COM1 (Windows)
    COM_2,                                // COM2 (Windows)
    COM_3,                                // COM3 (Windows)
    COM_4,                                // COM4 (Windows)
	COM_5,
	COM_6,
	COM_7,
	COM_8,
	COM_9,
	COM_10,
	COM_11,
	COM_12,
	COM_13,
	COM_14,
	COM_15,
	COM_16,
	COM_17,
	COM_18,
	COM_19,
	COM_20,
	COM_21,
	COM_22,
	COM_23,
	COM_24  
} COM_PORT;                            

typedef enum                              // Geocom format selector
{                                        
    COM_ASCII,                            //
    COM_BINARY                            //
} COM_FORMAT ;                      

typedef enum                              // Used for public customer interface
{                                       
    COM_BAUD_38400,                       //
    COM_BAUD_19200,                       //
    COM_BAUD_9600,                        //
    COM_BAUD_4800,                        //
    COM_BAUD_2400,                        //
	COM_BAUD_115200,                      //
    COM_BAUD_57600                        // 
} COM_BAUD_RATE;                       

typedef enum                              //  TPS startup selector
{                                         
    COM_TPS_STARTUP_LOCAL = 0,            //   boot into local mode of TPS
    COM_TPS_STARTUP_REMOTE = 1            //             remote mode of TPS
} COM_TPS_STARTUP_MODE;                 

typedef enum                              //  TPS startup selector
{                                         
    COM_TPS_STOP_SHUT_DOWN,               //   shut down of TPS
    COM_TPS_STOP_SLEEP,                   //   put TPS into sleep mode
    COM_TPS_STOP_REBOOT                   //   reboot of TPS
} COM_TPS_STOP_MODE; 
                   
typedef enum                              //  Current state of server
{                                         
    COM_TPS_OFF,                          //  TPS is off
    COM_TPS_SLEEPING,                     //  TPS is in sleep mode
    COM_TPS_ONLINE,                       //  TPS is on & active, online mode
    COM_TPS_LOCAL,                        //  TPS is in local mode
    COM_TPS_UNKNOWN                       //  Unknown/Not initialized
} COM_TPS_STATUS ;                        

struct DATE_TYPE
{
    short   Year;       // year
    BYTE    Month;      // month in year                1..12
    BYTE	Day;		// day in month                 1..31
};

struct TIME_TYPE
{
    BYTE    Hour;       // 24 hour per day  0..23
    BYTE    Minute;     // minute           0..59
    BYTE    Second;     // seconds          0..59
};

struct DATIME
{
    DATE_TYPE   Date;
    TIME_TYPE   Time;
};

enum ON_OFF_TYPE        // on/off switch type
{
    OFF,
    ON
};


#define COMMON1200_FW_API
#define GCOMS2K_API


const GRC_TYPE
                GRC_TPS  = 0x0000,	 // main return codes (identical to RC_SUP!!)
                GRC_SUP  = 0x0000,   // supervisor task (identical to RCBETA!!)
                GRC_ANG  = 0x0100,   // angle- and inclination
                GRC_ATA  = 0x0200,   // automatic target acquisition
                GRC_EDM  = 0x0300,   // electronic distance meter
                GRC_GMF  = 0x0400,   // geodesy mathematics & formulas
                GRC_TMC  = 0x0500,   // measurement & calc
                GRC_MEM  = 0x0600,   // memory management
                GRC_MOT  = 0x0700,   // motorization
                GRC_LDR  = 0x0800,   // program loader
                GRC_BMM  = 0x0900,   // basics of man machine interface
                GRC_TXT  = 0x0A00,   // text management
                GRC_MMI  = 0x0B00,   // man machine interface
                GRC_COM  = 0x0C00,   // communication
                GRC_DBM  = 0x0D00,   // data base management
                GRC_DEL  = 0x0E00,   // dynamic event logging
                GRC_FIL  = 0x0F00,   // file system
                GRC_CSV  = 0x1000,   // central services
                GRC_CTL  = 0x1100,   // controlling task
                GRC_STP  = 0x1200,   // start + stop task
                GRC_DPL  = 0x1300,   // data pool
                GRC_WIR  = 0x1400,   // wi registration

                GRC_USR  = 0x2000,   // user task
                GRC_ALT  = 0x2100,   // alternate user task
                GRC_AUT  = 0x2200,   // automatization
                GRC_AUS  = 0x2300,   // alternative user
                GRC_BAP  = 0x2400,   // basic applications
                GRC_SAP  = 0x2500,   // system applications
                GRC_COD  = 0x2600,   // standard code function
                GRC_BAS  = 0x2700,   // GeoBasic interpreter
				GRC_IOS  = 0x2800,   // Input-/ output- system
                GRC_CNF  = 0x2900,   // configuration facilities

                GRC_XIT  = 0x2E00,   // XIT subsystem (Excite-Level, LIS)
                GRC_DNA  = 0x2F00,   // DNA2 subsystem

                GRC_ICD  = 0x3000,   // cal data management
                GRC_KDM  = 0x3100,   // keyboard display module
                GRC_LOD  = 0x3200,   // firmware loader
                GRC_FTR  = 0x3300,   // file transfer
                GRC_VNF  = 0x3F00,   // reserved for new TPS1200 subsystem

                GRC_GPS  = 0x4000,   // GPS subsystem
                GRC_TST  = 0x4100,   // Test subsystem
                GRC_PTF  = 0x4F00,   // reserved for new GPS1200 subsystem

                GRC_APP  = 0x5000,   // offset for all applications

                GRC_RES  = 0x7000;   // reserved code range 


const GRC_TYPE
   GRC_OK           	= GRC_TPS +  0,   // Function successfully completed.
   GRC_UNDEFINED    	= GRC_TPS +  1,   // Unknown error, result unspecified.
   GRC_IVPARAM      	= GRC_TPS +  2,   // Invalid parameter detected.\nResult unspecified.
   GRC_IVRESULT     	= GRC_TPS +  3,   // Invalid result.
   GRC_FATAL        	= GRC_TPS +  4,   // Fatal error.
   GRC_NOT_IMPL     	= GRC_TPS +  5,   // Not implemented yet.
   GRC_TIME_OUT     	= GRC_TPS +  6,   // Function execution timed out.\nResult unspecified.
   GRC_SET_INCOMPL  	= GRC_TPS +  7,   // Parameter setup for subsystem is incomplete.
   GRC_ABORT        	= GRC_TPS +  8,   // Function execution has been aborted.
   GRC_NOMEMORY     	= GRC_TPS +  9,   // Fatal error - not enough memory.
   GRC_NOTINIT      	= GRC_TPS + 10,   // Fatal error - subsystem not initialized.
   GRC_SHUT_DOWN    	= GRC_TPS + 12,   // Subsystem is down.
   GRC_SYSBUSY      	= GRC_TPS + 13,   // System busy/already in use of another process.\nCannot execute function.
   GRC_HWFAILURE    	= GRC_TPS + 14,   // Fatal error - hardware failure.
   GRC_ABORT_APPL   	= GRC_TPS + 15,   // Execution of application has been aborted (SHIFT-ESC).
   GRC_LOW_POWER    	= GRC_TPS + 16,   // Operation aborted - insufficient power supply level.
   GRC_IVVERSION    	= GRC_TPS + 17,   // Invalid version of file, ...
   GRC_BATT_EMPTY    	= GRC_TPS + 18,   // Battery empty
   GRC_NO_EVENT       	= GRC_TPS + 20,   // no event pending.
   GRC_OUT_OF_TEMP     	= GRC_TPS + 21,   // out of temperature range
   GRC_INSTRUMENT_TILT 	= GRC_TPS + 22,   // intrument tilting out of range
   GRC_COM_SETTING     	= GRC_TPS + 23,   // communication error
   GRC_NO_ACTION       	= GRC_TPS + 24,   // GRC_TYPE Input 'do no action'
   GRC_SLEEP_MODE      	= GRC_TPS + 25,   // Instr. run into the sleep mode
   GRC_NOTOK            = GRC_TPS + 26,   // Function not successfully completed. 
   GRC_NA               = GRC_TPS + 27,   // Not available 
   GRC_OVERFLOW         = GRC_TPS + 28,   // Overflow error
   GRC_STOPPED          = GRC_TPS + 29;   // System or subsystem has been stopped


const GRC_TYPE
  GRC_COM_ERO                    = GRC_COM +  0 , //  Initiate Extended Runtime Operation (ERO).
  GRC_COM_CANT_ENCODE            = GRC_COM +  1 , //  Cannot encode arguments in client.
  GRC_COM_CANT_DECODE            = GRC_COM +  2 , //  Cannot decode results in client.
  GRC_COM_CANT_SEND              = GRC_COM +  3 , //  Hardware error while sending.
  GRC_COM_CANT_RECV              = GRC_COM +  4 , //  Hardware error while receiving.
  GRC_COM_TIMEDOUT               = GRC_COM +  5 , //  Request timed out.
  GRC_COM_WRONG_FORMAT           = GRC_COM +  6 , //  Packet format error.
  GRC_COM_VER_MISMATCH           = GRC_COM +  7 , //  Version mismatch between client and server.
  GRC_COM_CANT_DECODE_REQ        = GRC_COM +  8 , //  Cannot decode arguments in server.
  GRC_COM_PROC_UNAVAIL           = GRC_COM +  9 , //  Unknown RPC, procedure ID invalid.
  GRC_COM_CANT_ENCODE_REP        = GRC_COM + 10 , //  Cannot encode results in server.
  GRC_COM_SYSTEM_ERR             = GRC_COM + 11 , //  Unspecified generic system error.
  GRC_COM_UNKNOWN_HOST           = GRC_COM + 12 , //  (Unused error code)
  GRC_COM_FAILED                 = GRC_COM + 13 , //  Unspecified error.
  GRC_COM_NO_BINARY              = GRC_COM + 14 , //  Binary protocol not available.
  GRC_COM_INTR                   = GRC_COM + 15 , //  Call interrupted.
  GRC_COM_UNKNOWN_ADDR           = GRC_COM + 16 , //  (Unused error code)
  GRC_COM_NO_BROADCAST           = GRC_COM + 17 , //  (Unused error code)
  GRC_COM_REQUIRES_8DBITS        = GRC_COM + 18 , //  Protocol needs 8bit encoded chararacters.
  GRC_COM_UD_ERROR               = GRC_COM + 19 , //  (Unused error code)
  GRC_COM_LOST_REQ               = GRC_COM + 20 , //  (Unused error code)
  GRC_COM_TR_ID_MISMATCH         = GRC_COM + 21 , //  Transacation ID mismatch error.
  GRC_COM_NOT_GEOCOM             = GRC_COM + 22 , //  Protocol not recognizeable.
  GRC_COM_UNKNOWN_PORT           = GRC_COM + 23 , //  (WIN) Invalid port address.
  GRC_COM_ILLEGAL_TRPT_SELECTOR  = GRC_COM + 24 , //  (Unused error code)
  GRC_COM_TRPT_SELECTOR_IN_USE   = GRC_COM + 25 , //  (Unused error code)
  GRC_COM_INACTIVE_TRPT_SELECTOR = GRC_COM + 26 , //  (Unused error code)
  GRC_COM_ERO_END                = GRC_COM + 27 , //  ERO is terminating.
  GRC_COM_OVERRUN                = GRC_COM + 28 , //  Internal error: data buffer overflow.
  GRC_COM_SRVR_RX_CHECKSUM_ERROR = GRC_COM + 29 , //  Invalid checksum on server side received.
  GRC_COM_CLNT_RX_CHECKSUM_ERROR = GRC_COM + 30 , //  Invalid checksum on client side received.
  GRC_COM_PORT_NOT_AVAILABLE     = GRC_COM + 31 , //  (WIN) Port not available.
  GRC_COM_PORT_NOT_OPEN          = GRC_COM + 32 , //  (WIN) Port not opened.
  GRC_COM_NO_PARTNER             = GRC_COM + 33 , //  (WIN) Unable to find TPS.
  GRC_COM_ERO_NOT_STARTED        = GRC_COM + 34 , //  Extended Runtime Operation could not be started.
  GRC_COM_CONS_REQ               = GRC_COM + 35 , //  Att to send cons reqs
  GRC_COM_SRVR_IS_SLEEPING       = GRC_COM + 36 ,	//  TPS has gone to sleep. Wait and try again.
  GRC_COM_SRVR_IS_OFF            = GRC_COM + 37 ; //  TPS has shut down. Wait and try again.


COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_NullProc(void);
COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_GetSWVersion (short &nRel, short &nVer, short &nSubVer);
COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_SwitchOnTPS(COM_TPS_STARTUP_MODE eOnMode);
COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_SwitchOffTPS(COM_TPS_STOP_MODE eOffMode);
COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_GetBinaryAvailable(BOOLE &bAvailable);
COMMON1200_FW_API GCOMS2K_API GRC_TYPE COM_SetBinaryAvailable(BOOLE bAvailable);

 
GCOMS2K_API GRC_TYPE COM_Init(void);
GCOMS2K_API GRC_TYPE COM_End(void);
GCOMS2K_API GRC_TYPE COM_OpenConnection(COM_PORT ePort, 
                                      COM_BAUD_RATE &BaudRate, 
                                      short nRetries) ;
GCOMS2K_API GRC_TYPE COM_CloseConnection(void);
GCOMS2K_API GRC_TYPE COM_GetBaudRate(COM_BAUD_RATE &eBaudRate);
GCOMS2K_API GRC_TYPE COM_SetBaudRate(COM_BAUD_RATE eBaudRate);
GCOMS2K_API GRC_TYPE COM_GetDoublePrecision(short &nDigits);
GCOMS2K_API GRC_TYPE COM_SetDoublePrecision(short nDigits);
GCOMS2K_API GRC_TYPE COM_GetComFormat(COM_FORMAT &eFormat);
GCOMS2K_API GRC_TYPE COM_SetComFormat(COM_FORMAT eFormat);
GCOMS2K_API GRC_TYPE COM_GetTimeOut(short &nSeconds);
GCOMS2K_API GRC_TYPE COM_SetTimeOut(short nSeconds);
GCOMS2K_API GRC_TYPE COM_GetTPSState(COM_TPS_STATUS &eStatus);
GCOMS2K_API GRC_TYPE COM_UseWindow(HWND hWnd);             
GCOMS2K_API GRC_TYPE COM_SetConnDlgFlag(BOOLE bEnable);
GCOMS2K_API GRC_TYPE COM_ViewError(GRC_TYPE RetCode, 
                                 char *szCaption);
GCOMS2K_API GRC_TYPE COM_GetErrorText(GRC_TYPE RetCode, 
                                    char *szErrText);
GCOMS2K_API GRC_TYPE COM_GetWinSWVersion(short &nRel, 
                                       short &nVer, 
                                       short &nSubVer);


typedef enum
{
  CSV_CURRENT_POWER,
  CSV_EXTERNAL_POWER,
  CSV_INTERNAL_POWER

} CSV_POWER_PATH;

/* ------------------------------------------------------------------
   Definition of the TPS Device configuration.
   It describes build in hardware.
   ------------------------------------------------------------------ */
// Combinations are possible,
//   i.e. TCA1700: TPS_DEVICE_TC2 | TPS_DEVICE_MOT | TPS_DEVICE_ATR
enum TPS_DEVICE_TYPE
{
  // TPS1x00 common
  TPS_DEVICE_T   = 0x00000,   // Theodolite without built-in EDM
  TPS_DEVICE_MOT = 0x00004,   // Motorized device
  TPS_DEVICE_ATR = 0x00008,   // Automatic Target Recognition
  TPS_DEVICE_EGL = 0x00010,   // Electronic Guide Light
  TPS_DEVICE_DB  = 0x00020,   // reserved (Database, not GSI)
  TPS_DEVICE_DL  = 0x00040,   // Diode laser
  TPS_DEVICE_LP  = 0x00080,   // Laser plumbed
  
  // TPS1000 specific
  TPS_DEVICE_TC1 = 0x00001,   // tachymeter (TCW1)
  TPS_DEVICE_TC2 = 0x00002,   // tachymeter (TCW2)
  
  // TPS1100/TPS1200 specific
  TPS_DEVICE_TC     = 0x00001, // tachymeter (TCW3)
  TPS_DEVICE_TCR    = 0x00002, // tachymeter (TCW3 with red laser)
  TPS_DEVICE_ATC    = 0x00100, // Autocollimation lamp (used only PMU)
  TPS_DEVICE_LPNT   = 0x00200, // Laserpointer
  TPS_DEVICE_RL_EXT = 0x00400, // Reflectorless EDM with extended range (Pinpoint R100,R300)
  TPS_DEVICE_PS     = 0x00800, // Power Search

  // TPSSim specific
  TPS_DEVICE_SIM = 0x04000     // runs on Simulation, no Hardware
};

/* ------------------------------------------------------------------
   Definition of the TPS Device precision class
   ------------------------------------------------------------------ */
enum TPS_DEVICE_CLASS
{                       
  // TPS1000 Family          ---------------------- accuracy
  TPS_CLASS_1100 = 0,     // TPS1000 family member, 1 mgon,   3"
  TPS_CLASS_1700,         // TPS1000 family member, 0.5 mgon, 1.5"
  TPS_CLASS_1800,         // TPS1000 family member, 0.3 mgon, 1"
  TPS_CLASS_5000,         // TPS2000 family member
  TPS_CLASS_6000,         // TPS2000 family member 
  TPS_CLASS_1500,         // TPS1000 family member
  TPS_CLASS_2003,         // TPS2000 family member
  TPS_CLASS_5005,         // TPS5000      "
  TPS_CLASS_5100,         // TPS5000      "

  // TPS1100 Family          ---------------------- accuracy
  TPS_CLASS_1102 = 100,   // TPS1000 family member,  2"
  TPS_CLASS_1103,         // TPS1000 family member,  3"
  TPS_CLASS_1105,         // TPS1000 family member,  5"
  TPS_CLASS_1101,         // TPS1000 family member,  1."

  // TPS1200 Family          ---------------------- accuracy
  TPS_CLASS_1202 = 200,   // TPS1200 family member,  2"
  TPS_CLASS_1203,         // TPS1200 family member,  3"
  TPS_CLASS_1205,         // TPS1200 family member,  5"
  TPS_CLASS_1201          // TPS1200 family member,  1"
};



// Description:   Structure    TPS_DEVICE   TPS device configuration type
struct  TPS_DEVICE
     {
        TPS_DEVICE_CLASS  eClass;     // device precision class
        TPS_DEVICE_TYPE   Type;       // device configuration
     };

enum TPS_REFLESS_CLASS
{
    TPS_REFLESS_NONE,
    TPS_REFLESS_R100,                 // XR with red laser
    TPS_REFLESS_R300                  // XXR with red laser  
};



COMMON1200_FW_API GCOMS2K_API GRC_TYPE CSV_GetDateTime( DATIME &DateTime );
COMMON1200_FW_API GCOMS2K_API GRC_TYPE CSV_SetDateTime( DATIME DateTime );

GCOMS2K_API GRC_TYPE CSV_GetInstrumentNo (long &lSerialNo);
GCOMS2K_API GRC_TYPE CSV_GetInstrumentName (char * szName);
GCOMS2K_API GRC_TYPE CSV_GetIntTemp (double &dIntTemp);
GCOMS2K_API GRC_TYPE CSV_GetExtTemp (double &dExtTemp);
GCOMS2K_API GRC_TYPE CSV_GetVBat    ( double &dVBat );
GCOMS2K_API GRC_TYPE CSV_GetVMem    ( double &dVMem );
GCOMS2K_API GRC_TYPE CSV_CheckPower ( unsigned short     &unCapacity,
                                CSV_POWER_PATH     &eActivePower,
                                CSV_POWER_PATH     &ePowerSuggest );
GCOMS2K_API GRC_TYPE CSV_GetDeviceConfig(TPS_DEVICE &Device);
GCOMS2K_API GRC_TYPE CSV_GetReflectorlessClass(TPS_REFLESS_CLASS &reRefLessClass);
GCOMS2K_API GRC_TYPE CSV_GetSWVersion ( short &nRelease,
                                  short &nVersion, 
                                  short &nSubVersion );
COMMON1200_FW_API GCOMS2K_API GRC_TYPE CSV_SetDateTime(short nYear, short nMonth,  short nDay,
                                                       short nHour, short nMinute, short nSecond );
COMMON1200_FW_API GCOMS2K_API GRC_TYPE CSV_GetDateTime(short &nYear, short &nMonth,  short &nDay,
                                                       short &nHour, short &nMinute, short &nSecond );
COMMON1200_FW_API GCOMS2K_API GRC_TYPE CSV_GetDateTimeCentiSec( short &nYear, short &nMonth,  short &nDay,
                                                                short &nHour, short &nMinute, short &nSecond,
                                                                short &nCentiSec );                                  


COMMON1200_FW_API GCOMS2K_API GRC_TYPE CTL_GetUpCounter (short &nPowerOn, short &nSleepMode);


// Beep-Definitionen
const short IOS_BEEP_STDINTENS      = 100;    // Standard-Intensität des Beep


GCOMS2K_API GRC_TYPE IOS_BeepOn(short nIntens = IOS_BEEP_STDINTENS);
GCOMS2K_API GRC_TYPE IOS_BeepOff(void);


const unsigned short
    EDM_CURRENT_STATE   = 0, // Will be used at normal case and means the
                             // current states
    EDM_LAST_STATE      = 1; // Will be used to restore the states after
                             // the sleep mode


enum EDM_MODE
{ // Possible measuring programs, not each program will be
  // supported from the different sensor HW's
    EDM_MODE_NOT_USED,      // Init value
    EDM_SINGLE_TAPE,        // S.dist   (tape            , IR, f)
    EDM_SINGLE_STANDARD,    // S.dist   (standard   DIST , IR, g)
    EDM_SINGLE_FAST,        // S.dist   (coarse     DI   , IR, j)
    EDM_SINGLE_LRANGE,      // S.dist   (long range      , SR, o)
    EDM_SINGLE_SRANGE,      // S.dist   (short range     , SR, q)
    EDM_CONT_STANDARD,      // Trk dist (standard   TRK  , IR, h)
    EDM_CONT_DYNAMIC,       // Trk dist (dynamic         , IR, p)
    EDM_CONT_REFLESS,       // Trk dist (reflector less  , SR, r)
    EDM_CONT_FAST,          // Rpd dist (rapid trk  RTRK , IR, m)
    EDM_AVERAGE_IR,         // S.dist   (average DIL     , IR, g) 
    EDM_AVERAGE_SR,         // S.dist   (average DIL     , SR, q) 
    EDM_AVERAGE_LR          // S.dist   (average DIL     , SR, o) 
};

enum  EDM_EGLINTENSITY_TYPE
{// EGL intensity
    EDM_EGLINTEN_OFF, 
    EDM_EGLINTEN_LOW,
    EDM_EGLINTEN_MID, 
    EDM_EGLINTEN_HIGH
};   

enum EDM_MEASUREMENT_TYPE
{// Possible EDM sensor measurements
    EDM_SIGNAL_MEASUREMENT=1, // Inquiryflag for signal  measurement
    EDM_FREQ_MEASUREMENT  =2, //      "          frequency     "
    EDM_DIST_MEASUREMENT  =4, //      "          distance      "
    EDM_ANY_MEASUREMENT   =8  //      "          any           "
};



// Sensor system error                               
const GRC_TYPE               
 GRC_EDM_SYSTEM_ERR         =GRC_EDM+1, // Fatal EDM sensor error. See for the exact \nreason the original EDM sensor error number.\nIn the most cases a service problem.

 // Sensor user errors
 GRC_EDM_INVALID_COMMAND    =GRC_EDM+2, // Invalid command or unknown command,\nsee command syntax.
 GRC_EDM_BOOM_ERR           =GRC_EDM+3, // Boomerang error.
 GRC_EDM_SIGN_LOW_ERR       =GRC_EDM+4, // Received signal to low, prisma to far away,\nor natural barrier, bad environment, etc.  
 GRC_EDM_DIL_ERR            =GRC_EDM+5, // obsolete
 GRC_EDM_SIGN_HIGH_ERR      =GRC_EDM+6, // Received signal to strong, prisma \nto near, stranger light effect.
 // New TPS1200 sensor user errors
 GRC_EDM_TIMEOUT            =GRC_EDM+7, // Timeout, measuring time exceeded (signal too weak, beam interrupted,..)
 GRC_EDM_FLUKT_ERR          =GRC_EDM+8, // to much turbulences or distractions
 GRC_EDM_FMOT_ERR           =GRC_EDM+9, // filter motor defective

    // Subsystem errors 
 GRC_EDM_DEV_NOT_INSTALLED  =GRC_EDM+10, // Device like EGL, DL is not installed.
 GRC_EDM_NOT_FOUND          =GRC_EDM+11, // Search result invalid. For the exact explanation \nsee in the description of the called function.
 GRC_EDM_ERROR_RECEIVED     =GRC_EDM+12, // Communication ok, but an error\nreported from the EDM sensor.
 GRC_EDM_MISSING_SRVPWD     =GRC_EDM+13, // No service password is set.
 GRC_EDM_INVALID_ANSWER     =GRC_EDM+14, // Communication ok, but an unexpected\nanswer received. 
 GRC_EDM_SEND_ERR           =GRC_EDM+15, // Data send error, sending buffer is full.
 GRC_EDM_RECEIVE_ERR        =GRC_EDM+16, // Data receive error, like\nparity buffer overflow.
 GRC_EDM_INTERNAL_ERR       =GRC_EDM+17, // Internal EDM subsystem error.
 GRC_EDM_BUSY               =GRC_EDM+18, // Sensor is working already,\nabort current measuring first.
 GRC_EDM_NO_MEASACTIVITY    =GRC_EDM+19, // No measurement activity started.
 GRC_EDM_CHKSUM_ERR         =GRC_EDM+20, // Calculated checksum, resp. received data wrong\n(only in binary communication mode possible).
 GRC_EDM_INIT_OR_STOP_ERR   =GRC_EDM+21, // During start up or shut down phase an\nerror occured. It is saved in the DEL buffer.
 GRC_EDM_SRL_NOT_AVAILABLE  =GRC_EDM+22, // Red laser not available on this sensor HW.
 GRC_EDM_MEAS_ABORTED       =GRC_EDM+23, // Measurement will be aborted (will be used for the lasersecurity)

 // New TPS1200 sensor user error

 GRC_EDM_SLDR_TRANSFER_PENDING = GRC_EDM+30, // Multiple OpenTransfer calls.
 GRC_EDM_SLDR_TRANSFER_ILLEGAL = GRC_EDM+31, // No opentransfer happened.
 GRC_EDM_SLDR_DATA_ERROR       = GRC_EDM+32, // Unexpected data format received.
 GRC_EDM_SLDR_CHK_SUM_ERROR    = GRC_EDM+33, // Checksum error in transmitted data.
 GRC_EDM_SLDR_ADDR_ERROR       = GRC_EDM+34, // Address out of valid range.
 GRC_EDM_SLDR_INV_LOADFILE     = GRC_EDM+35, // Firmware file has invalid format.
 GRC_EDM_SLDR_UNSUPPORTED      = GRC_EDM+36, // Current (loaded) firmware doesn't support upload.
 GRC_EDM_UNKNOW_ERR	           = GRC_EDM+40, // Undocumented error from the\nEDM sensor, should not occur.

 GRC_EDM_DISTRANGE_ERR         = GRC_EDM + 50, // Out of distance range (dist too small or large)
 GRC_EDM_SIGNTONOISE_ERR       = GRC_EDM + 51, // Signal to noise ratio too small
 GRC_EDM_NOISEHIGH_ERR         = GRC_EDM + 52, // Noise to high
 GRC_EDM_PWD_NOTSET            = GRC_EDM + 53, // Password is not set
 GRC_EDM_ACTION_NO_MORE_VALID  = GRC_EDM + 54, // Elapsed time between prepare und start fast measurement for ATR to long
 GRC_EDM_MULTRG_ERR            = GRC_EDM + 55; // Possibly more than one target (also a sensor error)


GCOMS2K_API GRC_TYPE EDM_GetEglIntensity(EDM_EGLINTENSITY_TYPE& eIntensity,
                                         unsigned short unState=EDM_CURRENT_STATE);
GCOMS2K_API GRC_TYPE EDM_SetEglIntensity(EDM_EGLINTENSITY_TYPE eIntensity);
GCOMS2K_API GRC_TYPE EDM_Laserpointer(ON_OFF_TYPE eSwitch);
GCOMS2K_API GRC_TYPE EDM_SetBoomerangFilter(ON_OFF_TYPE eStateBoomerangFilter);
GCOMS2K_API GRC_TYPE EDM_GetDLOperatingTime(double& dTimeDL);
GCOMS2K_API GRC_TYPE EDM_IsContMeasActive(EDM_MEASUREMENT_TYPE eMeasType,
                                          BOOLE& rbActive);
GCOMS2K_API GRC_TYPE EDM_GetLPSwitch(ON_OFF_TYPE& reSwitch, unsigned short  unState);
GCOMS2K_API GRC_TYPE EDM_SetDLIntens(BYTE ucIntensity);


const short nMOT_AXES = 2;                      // Anzahl der Theodoliten-Achsen

    

// controller type:
enum MOT_MODE
    {
    MOT_POSIT   = 0,                // positioning controller
    MOT_OCONST  = 1,                // angular velocity controller
    MOT_MANUPOS = 2,                // manual fine pointing
    MOT_LOCK    = 3,                // target lock controller
    MOT_BREAK   = 4,                // break controller
    MOT_SERVICE = 5,                // service mode (not used)
    MOT_SEARCH  = 6,                // search controller
    MOT_NONE    = 7,                // controller not configurated
    MOT_TERM    = 8                 // controller terminated
    };   

// LockIn-Reglerstatus:
enum MOT_LOCK_STATUS
    {
    MOT_LOCKED_OUT,
    MOT_LOCKED_IN,
    MOT_PREDICTION    
    };


// deceleration modi:
enum MOT_STOPMODE
    {
    MOT_NORMAL,                     // standard brake acceleration
    MOT_SHUTDOWN                    // maximum brake acceleration
    };                
       

    
struct MOT_COM_PAIR                 // Datenaustauschpaar fuer GeoCom [HZ, V]
    {
    double  adValue[nMOT_AXES];
    };                


// Subsystemspezifische Return-Codes
const GRC_TYPE                       //Subsystem Antriebsregelung:
    GRC_MOT_UNREADY     = GRC_MOT+0, //motorization is not ready
                                     //(1792)
    GRC_MOT_BUSY        = GRC_MOT+1, //motorization is handling another task
                                     //(1793)
    GRC_MOT_NOT_OCONST  = GRC_MOT+2, //motorization is not in velocity mode
                                     //(1794)
    GRC_MOT_NOT_CONFIG  = GRC_MOT+3, //motorization is in the wrong mode or busy
                                     //(1795)
    GRC_MOT_NOT_POSIT   = GRC_MOT+4, //motorization is not in posit mode
                                     //(1796)
    GRC_MOT_NOT_SERVICE = GRC_MOT+5, //motorization is not in service mode
                                     //(1797)
    GRC_MOT_NOT_BUSY    = GRC_MOT+6, //motorization is handling no task
                                     //(1798)
    GRC_MOT_NOT_LOCK    = GRC_MOT+7, //motorization is not in tracking mode
                                     //(1799)
    GRC_MOT_NOT_SPIRAL  = GRC_MOT+8; //motorization is not in spiral mode
                                     //(1800)


GCOMS2K_API GRC_TYPE MOT_Posit( MOT_COM_PAIR RefAngle );
GCOMS2K_API GRC_TYPE MOT_SetVelocity( MOT_COM_PAIR RefOmega );
GCOMS2K_API GRC_TYPE MOT_ReadLockStatus( MOT_LOCK_STATUS &reStatus );
GCOMS2K_API GRC_TYPE MOT_StartController( MOT_MODE eControlMode );
GCOMS2K_API GRC_TYPE MOT_StopController( MOT_STOPMODE eMode );      


//Bewegungsparameter:
struct AUT_POSTOL
{
	double  adPosTol[nMOT_AXES];     //Positioniertoleranzen [rad]
};

struct AUT_TIMEOUT
{
	double  adPosTimeout[nMOT_AXES]; //max. Positionierzeiten [sec]
};

struct AUT_DETENT
{
	double dPositiveDetent;   //Anschlag in positiver Richtung
	double dNegativeDetent;   //Anschlag in negativer Richtung
	BOOLE bActive;            //Anschlag aktiv / inaktiv
};

struct AUT_SEARCH_SPIRAL
{
	double  dRangeHz;       // Breite der Spirale in rad
	double  dRangeV;        // max. Hoehe der Spirale in rad
};

struct AUT_SEARCH_AREA
{
	double  dCenterHz;     // Hz-Winkel des Spiralmittlepunkts [rad]
	double  dCenterV;      // V-Winkel des Spiralmittlepunkts [rad]
	double  dRangeHz;      // Breite der Spirale in rad
	double  dRangeV;       // max. Hoehe der Spirale in rad
	BOOLE   bEnabled;      // benutzerdefinierte Spirale aktiv/inaktiv
};


enum AUT_POSMODE
{AUT_NORMAL, AUT_PRECISE};          //Positionierungsmodi

enum AUT_ATRMODE
{AUT_POSITION, AUT_TARGET};         //Positionierungsmodi der ATR

enum AUT_ADJMODE
{AUT_NORM_MODE,                     //fineAdjust-Modi
	AUT_POINT_MODE,
	AUT_DEFINE_MODE};


//Hilfskonstanten der Suchfuktion 
const double AUT_SEARCH_DEF = 0.04;

const long  AUT_CLOCKWISE     =  1;     // Suchrichtung im Uhrzeigersinn
const long  AUT_ANTICLOCKWISE = -1;     // Suchrichtung im Gegenuhrzeigersinn

                                 

GCOMS2K_API GRC_TYPE AUT_PS_EnableRange( BOOLE bEnabled );

GCOMS2K_API GRC_TYPE AUT_PS_SetRange( long lMinDist, long lMaxDist );

GCOMS2K_API GRC_TYPE AUT_PS_SearchNext( long lDirection, BOOLE bSwing );

GCOMS2K_API GRC_TYPE AUT_PS_SearchWindow( void );

GCOMS2K_API GRC_TYPE AUT_MakePositioning( double dHz, double dV,    //Version 4
                              AUT_POSMODE ePOSMode, 
                              AUT_ATRMODE eATRMode,
                              BOOLE bDummy );

GCOMS2K_API GRC_TYPE AUT_LockIn( void );

                                 
GCOMS2K_API GRC_TYPE AUT_ChangeFace( AUT_POSMODE ePOSMode,          
                         AUT_ATRMODE eATRMode,
                         BOOLE bDummy );

GCOMS2K_API GRC_TYPE AUT_Search( double dHz_Area,                   
                     double dV_Area, 
                     BOOLE bDummy );                    

 
GCOMS2K_API GRC_TYPE AUT_FineAdjust( double dSrchHz,                //Version 2
                         double dSrchV );

                                 
GCOMS2K_API GRC_TYPE AUT_FineAdjust( double dSrchHz,                //Version 3
                         double dSrchV,
                         BOOLE bDummy );


GCOMS2K_API GRC_TYPE AUT_SetTol( AUT_POSTOL TolPar );
GCOMS2K_API GRC_TYPE AUT_ReadTol( AUT_POSTOL &rTolPar );  
GCOMS2K_API GRC_TYPE AUT_GetLockStatus( ON_OFF_TYPE &reOnOff );
GCOMS2K_API GRC_TYPE AUT_SetLockStatus( ON_OFF_TYPE eOnOff );
GCOMS2K_API GRC_TYPE AUT_GetATRStatus( ON_OFF_TYPE &reOnOff );
GCOMS2K_API GRC_TYPE AUT_SetATRStatus( ON_OFF_TYPE eOnOff ); 
GCOMS2K_API GRC_TYPE AUT_GetFineAdjustMode( AUT_ADJMODE &eMode );
GCOMS2K_API GRC_TYPE AUT_SetFineAdjustMode( AUT_ADJMODE eMode );    
GCOMS2K_API GRC_TYPE AUT_SetTimeout( AUT_TIMEOUT TimeoutPar ); 
GCOMS2K_API GRC_TYPE AUT_ReadTimeout( AUT_TIMEOUT &rTimeoutPar );
GCOMS2K_API GRC_TYPE AUT_SetDetents( AUT_DETENT DetentHz1,
                         AUT_DETENT DetentHz2,
                         AUT_DETENT DetentV1,
                         AUT_DETENT DetentV2 );
                         
GCOMS2K_API GRC_TYPE AUT_GetDetents( AUT_DETENT &DetentHz1,
                         AUT_DETENT &DetentHz2,
                         AUT_DETENT &DetentV1,
                         AUT_DETENT &DetentV2 );
                         
GCOMS2K_API GRC_TYPE AUT_EnableDetents( BOOLE bHz1,
                            BOOLE bHz2,
                            BOOLE bV1,
                            BOOLE bV2 );

// Daten der benutzerdefinierten Spirale abfragen
GCOMS2K_API GRC_TYPE AUT_GetUserSpiral( AUT_SEARCH_SPIRAL &SpiraDim );

// Daten der benutzerdefinierten Spirale uebergeben
GCOMS2K_API GRC_TYPE AUT_SetUserSpiral( AUT_SEARCH_SPIRAL SpiraDim );

// Daten des benutzerdefinierten Suchgebietes abfragen
GCOMS2K_API GRC_TYPE AUT_GetSearchArea( AUT_SEARCH_AREA &Area );

// Daten des benutzerdefinierten Suchgebietes uebergeben
GCOMS2K_API GRC_TYPE AUT_SetSearchArea( AUT_SEARCH_AREA Area );



enum TMC_INCLINE_PRG
{                            /* NEIGUNGSMESSUNG        ABHŽNGIG SETUP */
    TMC_MEA_INC     = 0,     /* Sensor (Apriori Sigma)       ja       */
    TMC_AUTO_INC    = 1,     /* Automatismus (Sensor/Ebene)  ja       */
    TMC_PLANE_INC   = 2      /* Ebene  (Apriori Sigma)       ja       */
    

};


enum  TMC_MEASURE_PRG         /*      TMC                         INCLINE       */
{                             /*   Messprogramm               Messmode Messzeit */
    TMC_STOP             = 0, /* Stopt das Messprogramm         nein     nein   */
    TMC_DEF_DIST         = 1, /* Default DIST-Messprogramm      ja       nein   */
    TMC_TRK_DIST         = 2, /* Distanz-TRK Messprogramm       ja       nein   */
    TMC_CLEAR            = 3, /* TMC_STOP mit Clear Data        nein     nein   */
    TMC_SIGNAL           = 4, /* Signalmessungen (Testfkt.)     nein     nein   */
    

    TMC_DO_MEASURE       = 6, /* (Re)start den Mess-Task        ja       nein   */
    

    TMC_RTRK_DIST        = 8, /* Distanz-RTRK Messprogramm      ja       nein   */
    

    TMC_RED_TRK_DIST     = 10,/* Distanz-RED-TRK Messprogramm   ja       nein   */
    TMC_FREQUENCY        = 11 /* Frequenzmessung (Testfkt.)     nein     nein   */
    

};


enum TMC_FACE
{
    TMC_FACE_1,                             /* Lage 1 der Fernrohrs */
    TMC_FACE_2                              /* Lage 2 der Fernrohrs */
};


enum TMC_AIM_TYPE
{
    TMC_AIM_TYPE_USER         = 0,         // Leica user (default = 34.4)
    TMC_AIM_TYPE_PRISM_ROUND,              // Standard prism
    TMC_AIM_TYPE_PRISM_MINI,               // Mini prism
    TMC_AIM_TYPE_PRISM_360,                // 360ø prism
    TMC_AIM_TYPE_TAPE,                     // Tape
    TMC_AIM_TYPE_REFLESS,                  // refless
    TMC_AIM_TYPE_JPMINI,                   // japanese mini prism (SMP222)
	TMC_AIM_TYPE_HDS_TAPE,                 // Cyra Tape
    TMC_AIM_TYPE_USER_TAPE                 // User Tape
};

enum TMC_AIM_VALUE
{
    TMC_AIM_VALUE_RELATIV     = 0,         // Zieltypewertedarstellung relativ
    TMC_AIM_VALUE_ABSOLUT                  // Zieltypewertedarstellung absolut
};

typedef enum
{
   THEODOLITE,                // Theodolite System
   TACHYMETER,                // Tachymeter System
   DIGITAL_LEVEL              // Digital Level system

} TMC_SYSTEM_DEDECT;



/* ================================================================== *\
   Typ Definitionen fuer Messungen
\* ================================================================== */
struct TMC_INCLINE
{
    double dCrossIncline;                 /*             Querneigung */
    double dLengthIncline;                /*           Laengsneigung */
    double dAccuracyIncline;              /* Genauigkeit der Neigung */
    SYSTIME InclineTime;                  /*   Zeitpunkt der Messung */
};

struct TMC_ATR
{
    double dHz;                   // Horizontaler Zielkorrektur
    double dV;                    // Verticale Zielkorrektur
    double dAtrAccuracy;          // Genauigkeit der Ablagemessung
    SYSTIME AtrTime;              // Zeitpunkt der Messung
};

struct TMC_ANGLE
{
    double dHz;                   /*              Horizontalwinkel */
    double dV;                    /*                Vertikalwinkel */
    double dAngleAccuracy;        /*       Genauigkeit der Winkels */
    SYSTIME AngleTime;            /*         Zeitpunkt der Messung */

    TMC_INCLINE Incline;          /*         Dazugehoerige Neigung */
    TMC_FACE eFace;               /* Lageinformation des Fernrohrs */
};

struct TMC_ANGLE_ALL
{
    double dHz;                   /*              Horizontalwinkel */
    double dV;                    /*                Vertikalwinkel */
    SYSTIME AngleTime;            /*         Zeitpunkt der Messung */

    double dCrossIncline;         /*                   Querneigung */
    double dLengthIncline;        /*                 Laengsneigung */
    SYSTIME InclineTime;          /*         Zeitpunkt der Messung */
    TMC_INCLINE_PRG IncMode;      /*                    level mode */

    double dAtrHz;                /*         Hz-Ablagewinkel [rad] */
    double dAtrV;                 /*       V-Ablagewinkel in [rad] */
    SYSTIME AtrTime;              /*         Zeitpunkt der Messung */
    GRC_TYPE AtrRetCode;           /*               Atr-Return-Code */
};                    /* NOT USED */


struct TMC_HZ_V_ANG
{
    double dHz;                      /*           Horizontalwinkel */
    double dV;                       /*             Vertikalwinkel */

};                     /* NOT USED */


struct TMC_COORDINATE
{
    double dE;              /*                       E-Koordinaten */
    double dN;              /*                       N-Koordinaten */
    double dH;              /*                       H-Koordinaten */
    SYSTIME CoordTime;      /*               Zeitpunkt der Messung */

    double dE_Cont;         /*       E-Koordinate (kontinuierlich) */
    double dN_Cont;         /*       N-Koordinate (kontinuierlich) */
    double dH_Cont;         /*       H-Koordinate (kontinuierlich) */
    SYSTIME CoordContTime;  /*               Zeitpunkt der Messung */
};


struct TMC_EDM_SIGNAL
{
    double  dSignalIntensity;       /*  Signalstaerke des EDM's in % */
    SYSTIME Time;                   /* Zeitpunkt der letzten Messung */
};                                  /* NOT USED */

struct TMC_EDM_FREQUENCY
{
    double  dFrequency;             // Frequenz des EDM's in Hz
    SYSTIME Time;                   // Zeitpunkt der letzten Messung
};                                  /* NOT USED */

/* ================================================================== *\
   Typ Definitionen fuer Korrekturwerte
\* ================================================================== */

struct TMC_ANG_SWITCH
{
    ON_OFF_TYPE eInclineCorr;             /*         Neigungskorrektur */
    ON_OFF_TYPE eStandAxisCorr;           /*                 Stehachse */
    ON_OFF_TYPE eCollimationCorr;         /*        Kollimationsfehler */
    ON_OFF_TYPE eTiltAxisCorr;            /*                 Kippachse */
};


struct TMC_ATMOS_TEMPERATURE
{
  double  dLambda;                // Wellenlaenge der Traegerwelle
  double  dPressure;              // Luftdruck
  double  dDryTemperature;        // Trockentemperatur
  double  dWetTemperature;        // Feuchtetemperatur
};

struct TMC_REFRACTION
{
  ON_OFF_TYPE eRefOn;               // Gueltigkeit der Refraktion
  double      dEarthRadius;         // Erdradius
  double      dRefractiveScale;     // Refraktionskoeffizient
};


struct TMC_HEIGHT
{
    double dHr;                     /*              Reflektorhoehe */
};

struct TMC_STATION
{
    double dE0;                     /*            Standpunkt-Koordinate */
    double dN0;                     /*            Standpunkt-Koordinate */
    double dH0;                     /*            Standpunkt-Koordinate */

    double dHi;                     /*           Instrumentenhoehe */
};


struct TMC_OFFSETDIST
{
    double dLengthVal;              // Aim-Offset Lenght
    double dCrossVal;               // Aim-Offset Cross
    double dHeightVal;              // Aim-Offset Height
};



// define old return code name for compatibility
#define TMC_NO_FULL_CORRECTION          GRC_TMC_NO_FULL_CORRECTION
#define TMC_ACCURACY_GUARANTEE          GRC_TMC_ACCURACY_GUARANTEE
#define TMC_ANGLE_OK                    GRC_TMC_ANGLE_OK
#define TMC_ANGLE_NO_FULL_CORRECTION    GRC_TMC_ANGLE_NOT_FULL_CORR
#define TMC_ANGLE_ACCURACY_GUARANTEE    GRC_TMC_ANGLE_NO_ACC_GUARANTY
#define TMC_ANGLE_ERROR                 GRC_TMC_ANGLE_ERROR 
#define TMC_DIST_PPM                    GRC_TMC_DIST_PPM
#define TMC_DIST_ERROR                  GRC_TMC_DIST_ERROR
#define TMC_BUSY                        GRC_TMC_BUSY
#define TMC_SIGNAL_ERROR                GRC_TMC_SIGNAL_ERROR

const GRC_TYPE
  GRC_TMC_NO_FULL_CORRECTION = GRC_TMC + 3,       // Warning: measurment without full correction
  GRC_TMC_ACCURACY_GUARANTEE = GRC_TMC + 4,       // Info   : accuracy can not be guarantee

  GRC_TMC_ANGLE_OK              = GRC_TMC + 5,    // Warning: only angle measurement valid
  GRC_TMC_ANGLE_NOT_FULL_CORR   = GRC_TMC + 8,    // Warning: only angle measurement valid but without full correction
  GRC_TMC_ANGLE_NO_ACC_GUARANTY = GRC_TMC + 9,    // Info   : only angle measurement valid but accuracy can not be guarantee

  GRC_TMC_ANGLE_ERROR       = GRC_TMC + 10,       // Error  : no angle measurement

  GRC_TMC_DIST_PPM          = GRC_TMC + 11,       // Error  : wrong setting of PPM or MM on EDM
  GRC_TMC_DIST_ERROR        = GRC_TMC + 12,       // Error  : distance measurement not done (no aim, etc.)
  GRC_TMC_BUSY              = GRC_TMC + 13,       // Error  : system is busy (no measurement done)
  GRC_TMC_SIGNAL_ERROR      = GRC_TMC + 14;       // Error  : no signal on EDM (only in signal mode)



GCOMS2K_API GRC_TYPE TMC_SetAngSwitch( TMC_ANG_SWITCH SwCorr );
GCOMS2K_API GRC_TYPE TMC_GetAngSwitch( TMC_ANG_SWITCH &SwCorr );

GCOMS2K_API GRC_TYPE TMC_SetInclineSwitch( ON_OFF_TYPE eSwCorr );
GCOMS2K_API GRC_TYPE TMC_GetInclineSwitch( ON_OFF_TYPE  &eSwCorr );



GCOMS2K_API GRC_TYPE TMC_GetSignal   ( TMC_EDM_SIGNAL    &Signal );

GCOMS2K_API GRC_TYPE TMC_QuickDist      ( TMC_HZ_V_ANG    &OnlyAngle,
                                    double          &dSlopeDistance );

GCOMS2K_API GRC_TYPE TMC_GetSimpleMea   ( SYSTIME         WaitTime,
                                    TMC_HZ_V_ANG    &OnlyAngle,
                                    double          &dSlopeDistance,
                                    TMC_INCLINE_PRG eMode = TMC_AUTO_INC );

GCOMS2K_API GRC_TYPE TMC_GetSimpleCoord ( SYSTIME         WaitTime,
                                    double          &dCoordE,
                                    double          &dCoordN,
                                    double          &dCoordH,
                                    TMC_INCLINE_PRG eMode = TMC_AUTO_INC );

GCOMS2K_API GRC_TYPE TMC_SetHandDist    ( double          dSlopeDistance,
                                    double          dHgtOffset,
                                    TMC_INCLINE_PRG eMode = TMC_AUTO_INC );

GCOMS2K_API GRC_TYPE TMC_GetAngle( TMC_ANGLE       &Angle,
                             TMC_INCLINE_PRG eMode = TMC_AUTO_INC );

GCOMS2K_API GRC_TYPE TMC_GetAngle( TMC_HZ_V_ANG    &OnlyAngle,
                             TMC_INCLINE_PRG eMode = TMC_AUTO_INC );

GCOMS2K_API GRC_TYPE TMC_DoMeasure( TMC_MEASURE_PRG  eCommand );

GCOMS2K_API GRC_TYPE TMC_DoMeasure( TMC_MEASURE_PRG  eCommand,
                              TMC_INCLINE_PRG  eMode );


GCOMS2K_API GRC_TYPE TMC_GetCoordinate( SYSTIME         WaitTime,
                                  TMC_COORDINATE  &Coordinate,
                                  TMC_INCLINE_PRG eMode = TMC_AUTO_INC );


GCOMS2K_API GRC_TYPE TMC_SetStation( TMC_STATION Station );
GCOMS2K_API GRC_TYPE TMC_GetStation( TMC_STATION &Station );

GCOMS2K_API GRC_TYPE TMC_GetPrismCorr( double &dPrismCorr );

GCOMS2K_API GRC_TYPE TMC_GetHeight( TMC_HEIGHT &Height );
GCOMS2K_API GRC_TYPE TMC_SetHeight( TMC_HEIGHT Height );

GCOMS2K_API GRC_TYPE TMC_SetOrientation   ( double dHzOrientation = 0.0 );
GCOMS2K_API GRC_TYPE TMC_SetPrismCorr( double dPrismCorr );


GCOMS2K_API GRC_TYPE TMC_GetFace           ( TMC_FACE &eFace );

GCOMS2K_API GRC_TYPE TMC_SetEdmMode( EDM_MODE eMode );
GCOMS2K_API GRC_TYPE TMC_GetEdmMode( EDM_MODE &eMode );

GCOMS2K_API GRC_TYPE TMC_ActivateOffsetDist();
GCOMS2K_API GRC_TYPE TMC_DeactivateOffsetDist ();    // used in TMC-Task



GCOMS2K_API GRC_TYPE TMC_SetAtmCorr( TMC_ATMOS_TEMPERATURE AtmTemperature );
GCOMS2K_API GRC_TYPE TMC_GetAtmCorr( TMC_ATMOS_TEMPERATURE &AtmTemperature );

GCOMS2K_API GRC_TYPE TMC_SetRefractiveCorr( TMC_REFRACTION    Refractive );
GCOMS2K_API GRC_TYPE TMC_GetRefractiveCorr( TMC_REFRACTION    &Refractive );

GCOMS2K_API GRC_TYPE TMC_SetRefractiveMethod( unsigned short unMethod );
GCOMS2K_API GRC_TYPE TMC_GetRefractiveMethod( unsigned short &unMethod );

GCOMS2K_API GRC_TYPE TMC_GetSlopeDistCorr ( double &dPpmCorr, double &dPrismCorr );


GCOMS2K_API GRC_TYPE TMC_IfDataAzeCorrError ( BOOLE &bAzeCorrectionError );
GCOMS2K_API GRC_TYPE TMC_IfDataIncCorrError ( BOOLE &bIncCorrectionError );


GCOMS2K_API GRC_TYPE TMC_SetAtmPpm(double dPpmA);
GCOMS2K_API GRC_TYPE TMC_GetAtmPpm(double &dPpmA);

GCOMS2K_API GRC_TYPE TMC_SetGeoPpm(unsigned short unGeomUseAutomatic,
                                   double dScaleFactorCentralMeridian,
                                   double dOffsetCentralMeridian,
                                   double dHeightReductionPPM,
                                   double dIndividualPPM);
GCOMS2K_API GRC_TYPE TMC_GetGeoPpm(unsigned short& unGeomUseAutomatic,
                                   double& dScaleFactorCentralMeridian,
                                   double& dOffsetCentralMeridian,
                                   double& dHeightReductionPPM,
                                   double& dIndividualPPM);


const GRC_TYPE
    GRC_BMM_XFER_PENDING           = GRC_BMM+1,  // Loading process already opened
    GRC_BMM_NO_XFER_OPEN           = GRC_BMM+2,  // Transfer not opened
    GRC_BMM_UNKNOWN_CHARSET        = GRC_BMM+3,  // Unknown character set
    GRC_BMM_NOT_INSTALLED          = GRC_BMM+4,  // Display module not present
    GRC_BMM_ALREADY_EXIST          = GRC_BMM+5,  // Character set already exists
    GRC_BMM_CANT_DELETE            = GRC_BMM+6,  // Character set cannot be deleted
    GRC_BMM_MEM_ERROR              = GRC_BMM+7,  // Memory cannot be allocated
    GRC_BMM_CHARSET_USED           = GRC_BMM+8,  // Character set still used
    GRC_BMM_CHARSET_SAVED          = GRC_BMM+9,  // Charset cannot be deleted or is protected
    GRC_BMM_INVALID_ADR            = GRC_BMM+10, // Attempt to copy a character block\noutside the allocated memory
    GRC_BMM_CANCELANDADR_ERROR     = GRC_BMM+11, // Error during release of allocated memory
    GRC_BMM_INVALID_SIZE           = GRC_BMM+12, // Number of bytes specified in header\ndoes not match the bytes read
    GRC_BMM_CANCELANDINVSIZE_ERROR = GRC_BMM+13, // Allocated memory could not be released
    GRC_BMM_ALL_GROUP_OCC          = GRC_BMM+14, // Max. number of character sets already loaded
    GRC_BMM_CANT_DEL_LAYERS        = GRC_BMM+15, // Layer cannot be deleted
    GRC_BMM_UNKNOWN_LAYER          = GRC_BMM+16, // Required layer does not exist
    GRC_BMM_INVALID_LAYERLEN       = GRC_BMM+17; // Layer length exceeds maximum


GCOMS2K_API GRC_TYPE BMM_BeepNormal(void);
GCOMS2K_API GRC_TYPE BMM_BeepAlarm(void);


typedef enum
{
    AUTO_POWER_DISABLED,        // Keine Wirkung der Automatik
    AUTO_POWER_SLEEP,           // Automatik legt System schlafen
    AUTO_POWER_OFF              // Automatik schaltet System aus
} SUP_AUTO_POWER; 


GCOMS2K_API GRC_TYPE SUP_GetConfig (ON_OFF_TYPE &eLowTempOnOff,
                                  SUP_AUTO_POWER &eAutoPower,
                                  SYSTIME &Timeout);                             
GCOMS2K_API GRC_TYPE SUP_SetConfig (ON_OFF_TYPE eLowTempOnOff= ON,
                                  SUP_AUTO_POWER eAutoPower= AUTO_POWER_SLEEP,
                                  SYSTIME Timeout= 900000);
GCOMS2K_API GRC_TYPE SUP_SwitchLowTempControl(ON_OFF_TYPE eLowTempOnOff);


GCOMS2K_API GRC_TYPE AUS_SetUserAtrState(ON_OFF_TYPE eNewState);
GCOMS2K_API GRC_TYPE AUS_GetUserAtrState(ON_OFF_TYPE &eState);
GCOMS2K_API GRC_TYPE AUS_SetUserLockState(ON_OFF_TYPE eNewState);
GCOMS2K_API GRC_TYPE AUS_GetUserLockState(ON_OFF_TYPE &eState);
GCOMS2K_API GRC_TYPE AUS_SwitchRcsSearch(ON_OFF_TYPE State);
GCOMS2K_API GRC_TYPE AUS_GetRcsSearchSwitch(ON_OFF_TYPE &State);
GCOMS2K_API GRC_TYPE AUS_GetLaserLotSwitch(ON_OFF_TYPE &reSwitch);


typedef enum 
{
 BAP_PRISM_ROUND = 0, // prism type: round
 BAP_PRISM_MINI  = 1, // prism type: mini
 BAP_PRISM_TAPE  = 2, // prism type: tape
 BAP_PRISM_360   = 3, // prism type: 360
 BAP_PRISM_USER1 = 4, // prism type: user1 
 BAP_PRISM_USER2 = 5, // prism type: user2
 BAP_PRISM_USER3 = 6, // prism type: user3
 BAP_PRISM_360_MINI  = 7, // prism type: 360 mini 
 BAP_PRISM_MINI_ZERO = 8, // prism type: mini zero 
 BAP_PRISM_USER      = 9, // prism type: user
 BAP_PRISM_HDS_TAPE  = 10, // prism type: tape cyra
 BAP_PRISM_GRZ121_ROUND  = 11 // prism type: GRZ121 round for machine guidance
} BAP_PRISMTYPE;


typedef enum
{
 BAP_REFL_UNDEF, // reflector not defined
 BAP_REFL_PRISM, // reflector prism
 BAP_REFL_TAPE   // reflector tape
} BAP_REFLTYPE;


typedef enum
{
 BAP_ATRSET_NORMAL,				// ATR is using no special flags or modes
 BAP_ATRSET_LOWVIS_ON,			// ATR low vis mode on
 BAP_ATRSET_LOWVIS_AON,			// ATR low vis mode always on
 BAP_ATRSET_SRANGE_ON,			// ATR high reflectivity mode on
 BAP_ATRSET_SRANGE_AON,			// ATR high reflectivity mode always on
} BAP_ATRSETTING;


const short BAP_NO_TARGET_TYPES = 2;   // number of target types
const short BAP_NO_PRISMTYPES   = 8;   // circ, mini, 360, tape, u1, u2, u3, 360 mini 
const short BAP_PRISMNAME_LEN   = 16;  // prism name string


typedef enum 
{ 
    BAP_NO_MEAS,          // no measurements
    BAP_NO_DIST,          // distance measurement, only angles
    BAP_DEF_DIST,         // default distance measurement program
    BAP_TRK_DIST,         // TRK distance measurement program and angles
    BAP_RTRK_DIST,        // RTRK distance measurement program and angles
    BAP_CLEAR_DIST,       // clear distances 
    BAP_STOP_TRK,         // stop tracking
    BAP_RED_TRK_DIST      // tracking with red laser
} BAP_MEASURE_PRG; 



/* definition of prism */
typedef struct
{
   char         szName[BAP_PRISMNAME_LEN+1];
   double       dAddConst;
   BAP_REFLTYPE eReflType;
}
BAP_PRISMDEF;


/* definition of the distance measure program type */
/* Do not change enum values. They are used as array index. */
typedef enum 
{
 BAP_SINGLE_REF_STANDARD = 0, 	// SINGLE = single measurement
 BAP_SINGLE_REF_FAST  = 1, 	  	// REF = 	with reflector
 BAP_SINGLE_REF_VISIBLE  = 2, 	// VISIBLE = with red laser
 BAP_SINGLE_RLESS_VISIBLE   = 3,// RLESS = without reflector
 BAP_CONT_REF_STANDARD = 4, 	// CONT = continuous measurement
 BAP_CONT_REF_FAST = 5, 
 BAP_CONT_RLESS_VISIBLE = 6, 
 BAP_AVG_REF_STANDARD = 7, 		// AVG = average measurement
 BAP_AVG_REF_VISIBLE = 8,
 BAP_AVG_RLESS_VISIBLE = 9  
} BAP_USER_MEASPRG;



typedef enum
{
 BAP_REFL_USE,	// with reflector
 BAP_REFL_LESS	// without reflector
} BAP_TARGET_TYPE;


GCOMS2K_API GRC_TYPE BAP_SetHzOrientationFlag(BOOLE bFlag);
GCOMS2K_API GRC_TYPE BAP_GetHzOrientationFlag(BOOLE& bFlag);
GCOMS2K_API GRC_TYPE BAP_SetMeasPrg(BAP_USER_MEASPRG eMeasPrg);
GCOMS2K_API GRC_TYPE BAP_SetMeasPrg(BAP_USER_MEASPRG eMeasPrg, BOOLE bNoATRLockChange);
GCOMS2K_API GRC_TYPE BAP_GetMeasPrg(BAP_USER_MEASPRG &eMeasPrg);
GCOMS2K_API GRC_TYPE BAP_SearchTarget(BOOLE bEnableMessages);
GCOMS2K_API GRC_TYPE BAP_SetPrismType(BAP_PRISMTYPE Prism);
GCOMS2K_API GRC_TYPE BAP_GetPrismType(BAP_PRISMTYPE &Prism);
GCOMS2K_API GRC_TYPE BAP_SetPrismType(BAP_PRISMTYPE Prism, char *szPrismName);
GCOMS2K_API GRC_TYPE BAP_GetPrismType(BAP_PRISMTYPE &Prism, char *szPrismName);
GCOMS2K_API GRC_TYPE BAP_SetUserPrism(BAP_PRISMTYPE Prism, char *szPrismName,
                                      double dAddConst, BOOLE bReflector);
GCOMS2K_API GRC_TYPE BAP_GetUserPrism(BAP_PRISMTYPE &Prism, char *szPrismName,
                                      double &dAddConst, BOOLE &bReflector);
GCOMS2K_API GRC_TYPE BAP_SetTargetType(BAP_TARGET_TYPE eTargetType); 
GCOMS2K_API GRC_TYPE BAP_GetTargetType(BAP_TARGET_TYPE &eTargetType); 
GCOMS2K_API GRC_TYPE BAP_GetPrismDef(BAP_PRISMTYPE ePrismType, BAP_PRISMDEF &PrismDef);
GCOMS2K_API GRC_TYPE BAP_SetPrismDef(BAP_PRISMTYPE ePrismType, BAP_PRISMDEF PrismDef);
GCOMS2K_API GRC_TYPE BAP_GetUserPrismDef(char *szPrismName, double &rdAddConst, BAP_REFLTYPE &reReflType, char *szCreator);
GCOMS2K_API GRC_TYPE BAP_SetUserPrismDef(char *szPrismName, double dAddConst, BAP_REFLTYPE eReflType, char *szCreator);
GCOMS2K_API GRC_TYPE BAP_GetATRSetting(BAP_ATRSETTING &reATRSetting);
GCOMS2K_API GRC_TYPE BAP_SetATRSetting(BAP_ATRSETTING eATRSetting);
GCOMS2K_API GRC_TYPE BAP_GetRedATRFov(ON_OFF_TYPE &reRedFov);
GCOMS2K_API GRC_TYPE BAP_SetRedATRFov(ON_OFF_TYPE eRedFov);



GCOMS2K_API GRC_TYPE BAP_GetLastDisplayedError( short &nError, short &nGSIError );


GCOMS2K_API GRC_TYPE BAP_MeasDistanceAngle( BAP_MEASURE_PRG &DistMode,
                                      double &dHz,
                                      double &dV,
                                      double &dDist ); 

// reset GeoCOM specific alignment
#pragma pack()

#endif // COM_..._USE_HPP



/* _________________________________________END com_pub.hpp___ */
