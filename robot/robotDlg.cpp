// robotDlg.cpp : implementation file
//

#include "stdafx.h"
#include <math.h>
#include <fstream.h>
#include <stdlib.h>
#include "com_pub.hpp"

#include "robot.h"
#include "robotDlg.h"
#include "setupdlg.h"
#include "asciidlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

const double PI = 4 * atan(1.0);
const double PI2 = 2 * PI;

/**************************************************************
*	parse
*	Break a string into words. Only the first 'maxw' words are
*	used.
*
*	Parameters
*		buf        - the string to parse
*		separator - a string with all the separator characters
*		maxw      - maximum number of words allowed (e.g. less or
*								equal to the length of words vector
*		words     - pointer vector to the words
*
*	Returns
*		Number of words found
*		< 0 if an error occures the absolut value equal to
*			the ordial number of the buggy word
*
*	Side effects
*		the original string is changed and used no new
*		memory blocks are allocated
**************************************************************/
int parse (char *buf, char *separator, int maxw, char *words[])
{
	int k = 0;				/* counts number of parsed word */
	int inquote = 0;	/* marks we are in double quote */

	while (*buf) {
		while (*buf == ' ' || *buf == '\t') buf++;	/* leading spaces/tabs */
		if (k >= maxw) return k;		/* max number of words reached */
		words[k] = buf;		/* set start of word */
		while (*buf && (inquote || strchr (separator, *buf) == (char *) NULL)) {
			if (*buf == '"')
				inquote = ! inquote;
			buf++;
		}
		if (*buf) *buf++ = '\0';
		/*if (strlen (words[k]))*/ k++;
	}
	if (inquote) return -k; /* unclosed quote */
	return k;
}

#define MAXW 100

/////////////////////////////////////////////////////////////////////////////
// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
		// No message handlers
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CRobotDlg dialog

CRobotDlg::CRobotDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CRobotDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CRobotDlg)
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CRobotDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CRobotDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CRobotDlg, CDialog)
	//{{AFX_MSG_MAP(CRobotDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_SETUPBUTTON, OnSetupbutton)
	ON_BN_CLICKED(IDC_ONLINE_BUTTON, OnOnlineButton)
	ON_BN_CLICKED(IDC_OFFLINE_BUTTON, OnOfflineButton)
	ON_BN_CLICKED(IDC_GETANGLES, OnGetangles)
	ON_BN_CLICKED(IDC_ALL, OnAll)
	ON_BN_CLICKED(IDC_MOVE_BUTTON, OnMoveButton)
	ON_BN_CLICKED(IDC_MOVEONLY_BUTTON, OnMoveonlyButton)
	ON_BN_CLICKED(IDC_SOURCEBUTTON, OnSourcebutton)
	ON_BN_CLICKED(IDC_STOPBUTTON, OnStopbutton)
	ON_BN_CLICKED(IDC_STARTBUTTON, OnStartbutton)
	ON_BN_CLICKED(IDC_STOPTRACEBUTTON, OnStoptracebutton)
	ON_BN_CLICKED(IDC_ATRCHECK, OnAtrcheck)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CRobotDlg message handlers

BOOL CRobotDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// port default setup
	BaudRate = COM_BAUD_9600;
	Port = COM_1;
	Protocol = COM_ASCII;
	GetDlgItem(IDC_SETUP)->SetWindowText("COM1:9600 ASCII");
	stop = 0;
	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CRobotDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CRobotDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CRobotDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CRobotDlg::OnSetupbutton() 
{
	CSetupDlg setupDlg;
	CString wstr;
	int n;

	switch (BaudRate) {
		case COM_BAUD_38400 : setupDlg.m_baud = 0; break;
		case COM_BAUD_19200 : setupDlg.m_baud = 1; break;
		case COM_BAUD_9600  : setupDlg.m_baud = 2;  break;
		case COM_BAUD_4800  : setupDlg.m_baud = 3;  break;
		case COM_BAUD_2400  : setupDlg.m_baud = 4;  break;
		default: setupDlg.m_baud = 2;
	}
	switch (Port) {
		case COM_1: setupDlg.m_port = 0; break;
		case COM_2: setupDlg.m_port = 1; break;
		case COM_3: setupDlg.m_port = 2; break;
		case COM_4: setupDlg.m_port = 3; break;
		case COM_5: setupDlg.m_port = 4; break;
		case COM_6: setupDlg.m_port = 5; break;
		default: setupDlg.m_port = 0;
	}
	switch (Protocol) {
		case COM_ASCII : setupDlg.m_protocol = 0;  break;
		case COM_BINARY: setupDlg.m_protocol = 1; break;
		default: setupDlg.m_protocol = 0;
	}
	n = setupDlg.DoModal();
	if (n == IDOK) {
		wstr = "";
		switch (setupDlg.m_port) {
			case 0 : Port = COM_1; wstr += "COM1:"; break;
			case 1 : Port = COM_2; wstr += "COM2:"; break;
			case 2 : Port = COM_3; wstr += "COM3:"; break;
			case 3 : Port = COM_4; wstr += "COM4:"; break;
			case 4 : Port = COM_5; wstr += "COM5:"; break;
			case 5 : Port = COM_6; wstr += "COM6:"; break;
			default: Port = COM_1; wstr += "COM1:";
		}
		switch (setupDlg.m_baud) {
			case 0 : BaudRate = COM_BAUD_38400; wstr += "38400 "; break;
			case 1 : BaudRate = COM_BAUD_19200; wstr += "19200 "; break;
			case 2 : BaudRate = COM_BAUD_9600;  wstr += "9600 "; break;
			case 3 : BaudRate = COM_BAUD_4800;  wstr += "4800 "; break;
			case 4 : BaudRate = COM_BAUD_2400;  wstr += "2400 "; break;
			default: BaudRate = COM_BAUD_9600;  wstr += "9600 ";
		}
		switch (setupDlg.m_protocol) {
			case 0 : Protocol = COM_ASCII;  wstr += "ASCII"; break;
			case 1 : Protocol = COM_BINARY; wstr += "BINARY";break;
			default: Protocol = COM_ASCII;  wstr += "ASCII";
		}
		GetDlgItem(IDC_SETUP)->SetWindowText(wstr);
	}
}

void CRobotDlg::OnOnlineButton() 
{
	GRC_TYPE Result;
	COM_BAUD_RATE SaveBaud;
	CString wstr;
	Result = COM_Init();
	if (Result != GRC_OK) {
		COM_ViewError(Result, "COM_Init");
		return;
	}

	// save baudrate in 'SaveBaud' because 'COM_OpenConnection' might change it
	SaveBaud = BaudRate;
	Result = COM_OpenConnection(Port, BaudRate, Protocol);
	if (Result == GRC_OK) { // check if correct baudrate set
		if (SaveBaud != BaudRate) { // no, set it
			Result = COM_SetBaudRate(SaveBaud);
        }
		/*** debug ***/ //Result = COM_GetBaudRate(TmpBaudRate);
    }

	if (Result != GRC_OK) {
		COM_ViewError(Result, "COM_OpenConnection");
		Result = COM_End();
		return;
    }
	// get ATR state from instrument
	ON_OFF_TYPE on;
	Result = AUT_GetATRStatus(on);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUS_GetATRStatus");
	}
//TMC_AIM_TYPE p;
//TMC_SetPrismType(p);
//TMC_AIM_VALUE q;
//TMC_GetPrismValueMode(q);
	AUT_TIMEOUT TimeoutPar;
	TimeoutPar.adPosTimeout[0] = 300;
	TimeoutPar.adPosTimeout[1] = 300;
	AUT_SetTimeout(TimeoutPar);
	COM_SetTimeOut(300);
	GetDlgItem(IDC_SETUPBUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_ONLINE_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_GETANGLES)->EnableWindow (TRUE);
	GetDlgItem(IDC_ALL)->EnableWindow (TRUE);
	GetDlgItem(IDC_OFFLINE_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_MOVEONLY_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_MOVE_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_HZ_ANGLE_SET)->EnableWindow (TRUE);
	GetDlgItem(IDC_V_ANGLE_SET)->EnableWindow (TRUE);
	GetDlgItem(IDC_SOURCEBUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_STARTBUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_DISTCHECK)->EnableWindow (TRUE);
	((CButton *)GetDlgItem(IDC_DISTCHECK))->SetCheck(BST_CHECKED);
	GetDlgItem(IDC_DELAY)->EnableWindow (TRUE);
	GetDlgItem(IDOK)->EnableWindow (FALSE);
	GetDlgItem(IDC_ATRCHECK)->EnableWindow (TRUE);;
	GetDlgItem(IDC_SETUP)->GetWindowText(wstr);
	((CButton *)GetDlgItem(IDC_ATRCHECK))->SetCheck(on);

	char iname[256];
	CSV_GetInstrumentName(iname);
	wstr += '/';
	wstr += iname;
	GetDlgItem(IDC_SETUP)->SetWindowText(wstr);
}

void CRobotDlg::OnOfflineButton() 
{
	GRC_TYPE         Result;
	Result = COM_CloseConnection();
	if (Result != GRC_OK) {
		COM_ViewError(Result, "COM_CloseConnection");
		return;
    }
	Result = COM_End();
	if (Result != GRC_OK) {
		COM_ViewError(Result, "COM_End");
	}
	GetDlgItem(IDC_SETUPBUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_ONLINE_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_GETANGLES)->EnableWindow (FALSE);
	GetDlgItem(IDC_ALL)->EnableWindow (FALSE);
	GetDlgItem(IDC_OFFLINE_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_MOVEONLY_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_MOVE_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_HZ_ANGLE_SET)->EnableWindow (FALSE);
	GetDlgItem(IDC_V_ANGLE_SET)->EnableWindow (FALSE);
	GetDlgItem(IDC_SOURCEBUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_ATRCHECK)->EnableWindow (FALSE);
	GetDlgItem(IDOK)->EnableWindow (TRUE);
}

void CRobotDlg::OnGetangles() 
{
	// read angles from instrument
	GRC_TYPE Result;
	TMC_HZ_V_ANG angles;

	Result = TMC_GetAngle(angles, TMC_AUTO_INC);
	if (Result == GRC_OK || Result == TMC_NO_FULL_CORRECTION || Result == TMC_ACCURACY_GUARANTEE) {
		GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
		GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
		GetDlgItem(IDC_SLOPE)->SetWindowText("");
	} else {
		COM_ViewError(Result, "TMC_GetAngle");
	}
}

// convert rad to dms
CString CRobotDlg::dms(double a, int opt) {
	// opt = 0 d-mm-ss for display
	// opt = 1 d.mmss for job format
	// opt = 2 dddmmss for gsi format
	double second;
	int degree, minute;
	CString wstr;

	second = fabs(a) * 648000.0 / PI;
	degree = (int) (second / 3600.0);
	minute = (int) (((int) second % 3600) / 60.0);
	second = second - degree * 3600.0 - minute * 60.0;
	switch (opt) {
	case 0:
		wstr.Format("%s%d-%d-%.1f", (a < 0 ? "-" : ""), degree, minute, second);
		break;
	case 1:
		wstr.Format("%s%d.%02d%02d", (a < 0 ? "-" : ""), degree, minute, int(second));
		break;
	case 2:
		wstr.Format("%s%03d%02d%02d", (a < 0 ? "-" : ""), degree, minute, int(second));
		break;
	}
	return wstr;
}

// convert dms to rad
double CRobotDlg::rad(CString a) {
	CString wstr;
	double hz;

	AfxExtractSubString(wstr, a, 0, '-');
	hz = atoi(wstr);
	AfxExtractSubString(wstr, a, 1, '-');
	hz += atoi(wstr) / 60.0;
	AfxExtractSubString(wstr, a, 2, '-');
	hz += atof(wstr) / 3600.0;
	hz *= PI / 180.0;
	return hz;	
}


void CRobotDlg::OnAll() 
{
	GRC_TYPE Result;
	TMC_HZ_V_ANG angles;
	double dist;
	CString wstr;
	ON_OFF_TYPE state;


	Result = AUT_GetATRStatus(state);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_GetATRStatus");
		return;
	}
	if (state == ON) {
		TMC_HZ_V_ANG angles;
		Result = TMC_GetAngle(angles, TMC_AUTO_INC);
		Result = AUT_MakePositioning(angles.dHz, angles.dV, AUT_PRECISE, AUT_TARGET, FALSE);
	}
	Result = TMC_DoMeasure(TMC_DEF_DIST, TMC_AUTO_INC);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "TMC_DoMeasure");
		return;
	}
	// distance measurement successful
	Result = TMC_GetSimpleMea(3000, angles, dist, TMC_AUTO_INC);
	switch (Result) {
		case GRC_OK :
			GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
			GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
			wstr.Format("%.4f", dist);
			GetDlgItem(IDC_SLOPE)->SetWindowText(wstr);
			break;
		case TMC_ACCURACY_GUARANTEE:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			break;
		default:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			return;
	}
	GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
	GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
	wstr.Format("%.4f", dist);
	GetDlgItem(IDC_SLOPE)->SetWindowText(wstr);
}

void CRobotDlg::OnMoveButton() 
{
	// move the instrument to the given direction and measure distance
	GRC_TYPE Result;
	TMC_HZ_V_ANG angles;
	double hz, v, dist;
	CString wstr, wstr1;
	ON_OFF_TYPE state;

	GetDlgItem(IDC_HZ_ANGLE_SET)->GetWindowText(wstr);
	hz = rad(wstr);
	GetDlgItem(IDC_V_ANGLE_SET)->GetWindowText(wstr);
	v = rad(wstr);
	state = ((CButton *)GetDlgItem(IDC_ATRCHECK))->GetCheck() ? ON : OFF;
	if (state == ON) {
		Result = AUT_MakePositioning(hz, v, AUT_PRECISE, AUT_TARGET, FALSE);
	} else {
		Result = AUT_MakePositioning(hz, v, AUT_PRECISE, AUT_POSITION, FALSE);
	}
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_MakePositioning");
		return;
	}
	Result = TMC_DoMeasure(TMC_DEF_DIST, TMC_AUTO_INC);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "TMC_DoMeasure");
		return;
	}
	// distance measurement successful
	Result = TMC_GetSimpleMea(3000, angles, dist, TMC_AUTO_INC);
	switch (Result) {
		case GRC_OK :
			GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
			GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
			wstr.Format("%.4f", dist);
			GetDlgItem(IDC_SLOPE)->SetWindowText(wstr);
			break;
		case TMC_ACCURACY_GUARANTEE:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			break;
		default:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			return;
	}
	GetDlgItem(IDC_HZ_ANGLE_SET)->SetWindowText(dms(angles.dHz));
	GetDlgItem(IDC_V_ANGLE_SET)->SetWindowText(dms(angles.dV));
	wstr.Format("%.4f", dist);
	GetDlgItem(IDC_SLOPE2)->SetWindowText(wstr);
}

void CRobotDlg::OnMoveonlyButton() 
{
	// move the instrument to the given direction
	GRC_TYPE Result;
	double hz, v;
	CString wstr;

	GetDlgItem(IDC_HZ_ANGLE_SET)->GetWindowText(wstr);
	hz = rad(wstr);
	GetDlgItem(IDC_V_ANGLE_SET)->GetWindowText(wstr);
	v = rad(wstr);
	Result = AUT_MakePositioning(hz, v, AUT_NORMAL, AUT_POSITION, FALSE);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_MakePositioning");
		return;
	}
}

#define MAXDIR 100	// maximal number of directions
#define MAXTRY 3	// maximal number of retry observation

void CRobotDlg::OnSourcebutton() 
{
	// read directions from file
	// Leica robot measurement input file
	// point_id,hz,v,faces,PC
	// faces = 0 no meaurement, 1 measure face left, 2 measure two faces, 4 measure two round
	// PC prism constant [mm], optional if missing no change to the measured distance
	char buf[4096], st[20], w[256];
	double ih;
	char *words[MAXW];
	int nw;
	int line = 0;
	struct pointDir {
		char pid[20];			// point number/name
		double hz, v, s;		// horizontal direction and zenith angle, slope distance
		int faces;				// number of face left and right to measure, 0 skip
		double pc;				// prism constant (optional)
	} Directions[MAXDIR];
	int i, j, k, n, maxRep, nDirection = 0, from, to, step;
	FILE *fo;
	EDM_EGLINTENSITY_TYPE egl_off = EDM_EGLINTEN_OFF, egl_on = EDM_EGLINTEN_HIGH;
	AUT_ATRMODE pos;			// positioning type AUT_POSITION or AUT_TARGET (ATR)

	// read input file
	char filter[] = "Measure file (*.tca)| *.tca||";
	CFileDialog fDlg (TRUE, ".dat", NULL,
		OFN_HIDEREADONLY, filter);
	if (fDlg.DoModal () != IDOK) return;
	CString file_name = fDlg.GetPathName ();
	fstream fs (LPCTSTR (file_name), ios::in);
	maxRep = 0;
	st[0] = '\0'; ih = 0;
	while (! fs.eof ())	{
		line++;
		fs.getline (buf, sizeof (buf));
		nw = parse (buf, " ,\n", MAXW, words);
		if (nw == 0 || buf[0] == '#') continue;	// skip empty lines or comments
		if (buf[0] == '!') {
			if (nDirection) {
				AfxMessageBox("Station data not at the beginning");
				fs.close();
				return;
			}
			if (nw < 0 || nw != 3) {
				// station data
				sprintf(w, "Error in line %d", line);
				AfxMessageBox (w);
				continue;
			}
			strcpy(st, words[1]);
			ih = atof(words[2]);
		} else {
			if (! strlen(st) && nDirection == 0) {
				sprintf(w, "Missing station data before line %d", line);
				AfxMessageBox (w);
				strcpy(st, "?");
			}
			if (nw < 0 || ! (nw == 5 || nw == 6))
			{
				sprintf(w, "Error in line %d", line);
				AfxMessageBox (w);
				continue;
			}
			strcpy(Directions[nDirection].pid, words[0]);
			Directions[nDirection].hz = rad(words[1]);
			Directions[nDirection].v = rad(words[2]);
			Directions[nDirection].s = atof(words[3]);
			Directions[nDirection].faces = atoi(words[4]);
			if (Directions[nDirection].faces > maxRep) {
				maxRep = Directions[nDirection].faces;
			}
			if (nw == 6) { 
				Directions[nDirection].pc = atoi(words[5]);
			} else {
				Directions[nDirection].pc = 0.0;
			}
			nDirection++;
			if (nDirection >= MAXDIR) {
				AfxMessageBox ("Too many directions!");
				break;
			}
		}
	}
	fs.close();
	// check ATR
	ON_OFF_TYPE state;
	GRC_TYPE Result;
	CString wstr, wstr1;
	Result = AUT_GetATRStatus(state);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_GetATRStatus");
		return;
	}
	if (state == ON) {
		pos = AUT_TARGET;
	} else {
		if (AfxMessageBox("ATR turned off! Continue?", MB_OKCANCEL) == IDCANCEL) {
			return;
		}
		pos = AUT_POSITION;
	}

	// enable stop button
	GetDlgItem(IDC_GETANGLES)->EnableWindow (FALSE);
	GetDlgItem(IDC_ALL)->EnableWindow (FALSE);
	GetDlgItem(IDC_OFFLINE_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_MOVEONLY_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_MOVE_BUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_HZ_ANGLE_SET)->EnableWindow (FALSE);
	GetDlgItem(IDC_V_ANGLE_SET)->EnableWindow (FALSE);
	GetDlgItem(IDC_STOPBUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_SOURCEBUTTON)->EnableWindow (FALSE);
	stop = 0;
	// go through points
	TMC_HZ_V_ANG angles;
	double dist, hz, v;
	COleDateTime act = COleDateTime::GetCurrentTime();
	strcpy (w, file_name);
	w[strlen(w)-4] = '\0';	// remove extension
	sprintf (w, "%s%d%02d%02d%02d%02d.gsi", w, act.GetYear (), act.GetMonth (), act.GetDay (), 
		act.GetHour(), act.GetMinute());
	fo = fopen(w, "w");
// job
//	fprintf (fo, "51=%d.%02d.02%d\n", act.GetYear (), act.GetMonth (), act.GetDay ());
//	fprintf (fo, "52=%d:%02d\n", act.GetHour (), act.GetMinute ());
//	fprintf (fo, "2=%s\n3=%.3f\n", st, ih);
	// gsi
	wstr = "410001+00000002 42....+";
	for (i = 0; i < 8 - (signed int) strlen(st); i++)
		wstr += "0";
	wstr += st;		// station point id
	wstr += " 43....+";
	wstr1.Format("%.4f", ih);	// instrument height
	for (i = 0; i < 8 - wstr1.GetLength(); i++)
		wstr += "0";
	wstr += wstr1;
	wstr += " 44....+00000000";	// default target height
	wstr += " 45....+";
	// date time mmddhhMM
	wstr1.Format("%02d%02d%02d%02d", act.GetMonth (), act.GetDay (), act.GetHour (), act.GetMinute ());
	wstr += wstr1;
	fprintf (fo, "%s\n", wstr);
	n = 1;	// actual record number
	for (j = 0; j < maxRep; j++) {
		if (j % 2) {
			// backward order, face right
			from = nDirection - 1; to = -1; step = -1;
		} else {
			// forward order, face left
			from = 0; to = nDirection; step = 1;
		}
		for (i = from; i != to; i += step) {
			if (stop) break;	// manually stopped
			if (Directions[i].faces - 1 < j) {
				continue;
			}
			n++;
			// move the instrument to the given direction and measure distance
			GetDlgItem(IDC_POINTID)->SetWindowText(Directions[i].pid);
			GetDlgItem(IDC_STATUS)->SetWindowText("Measuring ...");
			Invalidate(100);	// redraw dialog
			DoEvents();			// process events
			if (j % 2) {
				hz = (Directions[i].hz > PI ? Directions[i].hz - PI : Directions[i].hz + PI);
				v = PI2 - Directions[i].v;
			} else {
				hz = Directions[i].hz;
				v = Directions[i].v;
			}
			if (Directions[i].s < 0.1) {
				// direction only for joke moving the instrument
				Result = AUT_MakePositioning(hz, v, AUT_NORMAL, AUT_POSITION, FALSE);
				if (Directions[i].s < 0) {
				// set EGL intensity
					Result = EDM_SetEglIntensity(egl_on);
					BMM_BeepNormal();
					BMM_BeepNormal();
				} else {
					Result = EDM_SetEglIntensity(egl_off);
				}
			} else {	// measure distance
				for (k = 0; k < MAXTRY; k++) {
					Result = AUT_MakePositioning(hz, v, AUT_PRECISE, pos, FALSE);
					if (Result == GRC_OK) break;
				}
				if (Result != GRC_OK) {
					BMM_BeepNormal();
//					fprintf (fo, "{5 %s} {4 POSITIONING}\n", Directions[i].pid);
//					fprintf (fo, "5=%s\n4=DIRECTION\n", Directions[i].pid);
					wstr.Format("11%04d+", n);
					for (k = 0; k < 8 - (signed int) strlen(Directions[i].pid); k++)
						wstr += "0";
					wstr += Directions[i].pid;
					wstr += " 71....+DIRECTIO";
					fprintf (fo, "%s\n", wstr);
					continue;
				}
				for (k = 0; k < MAXTRY; k++) {
					Result = TMC_DoMeasure(TMC_DEF_DIST, TMC_AUTO_INC);
					if (Result == GRC_OK) break;
				}
				if (Result != GRC_OK) {
					BMM_BeepNormal();
//					fprintf (fo, "{5 %s} {4 DOMEASURE}\n", Directions[i].pid);
//					fprintf (fo, "5=%s\n4=DOMEASURE\n", Directions[i].pid);
					wstr.Format("11%04d+", n);
					for (k = 0; k < 8 - (signed int) strlen(Directions[i].pid); k++)
						wstr += "0";
					wstr += Directions[i].pid;
					wstr += " 71....+DOMEASUR";
					fprintf (fo, "%s\n", wstr);
					continue;
				}
				// distance measurement successful
				for (k = 0; k < MAXTRY; k++) {
					Result = TMC_GetSimpleMea(3000, angles, dist, TMC_AUTO_INC);
					if (Result == GRC_OK) break;
				}
				// take into acount the prism constant
				dist += Directions[i].pc;
				switch (Result) {
					case GRC_OK :
						GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
						GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
						wstr.Format("%.4f", dist);
						GetDlgItem(IDC_SLOPE)->SetWindowText(wstr);
						GetDlgItem(IDC_STATUS)->SetWindowText("OK");
						// store data in GeoEasy format
//						fprintf (fo, "{5 %s} {4 OK} {7 %s} {8 %s} {9 %.4f}\n", Directions[i].pid, 
//							dms(angles.dHz), dms(angles.dV), dist);
//						fprintf (fo, "5=%s\n17=%s\n18=%s\n9=%.4f\n45=%s\n19=%s\n76=%.4f\n", Directions[i].pid, 
//							dms(angles.dHz, 1), dms(angles.dV, 1), dist, 
//							dms(hz - angles.dHz),
//							dms(v - angles.dV),
//							Directions[i].s - dist);
						wstr.Format("11%04d+", n);
						for (k = 0; k < 8 - (signed int) strlen(Directions[i].pid); k++)
							wstr += "0";
						wstr += Directions[i].pid;
						wstr += " 21.324+";
						wstr += dms(angles.dHz, 2);	// horizontal angle
						wstr += "0";
						wstr += " 22.324+";
						wstr += dms(angles.dV, 2);	// zenith angle
						wstr += "0";
						wstr += " 31..06+";
						wstr1.Format("%08d", (int) (dist * 10000 + 0.5));	// distance
						wstr += wstr1;
						fprintf (fo, "%s\n", wstr);
						break;
					case TMC_ACCURACY_GUARANTEE:
						BMM_BeepNormal();
						GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(dms(angles.dHz));
						GetDlgItem(IDC_V_ANGLE)->SetWindowText(dms(angles.dV));
						wstr.Format("%.4f", dist);
						GetDlgItem(IDC_SLOPE)->SetWindowText(wstr);
//						fprintf (fo, "{5 %s} {4 ACCURACY} {7 %s} {8 %s} {9 %.4f}\n", Directions[i].pid, 
//							dms(angles.dHz), dms(angles.dV), dist);
//						fprintf (fo, "5=%s\n4=ACCURACY\n17=%s\n18=%s\n9=%.4f\n45=%s\n19=%s\n76=%.4f\n", Directions[i].pid, 
//							dms(angles.dHz, 1), dms(angles.dV, 1), dist, 
//							dms(hz - angles.dHz),
//							dms(v - angles.dV),
//							Directions[i].s - dist);
						wstr.Format("11%04d+", n);
						for (k = 0; k < 8 - (signed int) strlen(Directions[i].pid); k++)
							wstr += "0";
						wstr += Directions[i].pid;
						wstr += " 21.324+";
						wstr += dms(angles.dHz, 2);
						wstr += " 22.324+";
						wstr += dms(angles.dV, 2);
						wstr += " 31..06+";
						wstr1.Format("%08d", (int) (dist * 10000 + 0.5));
						wstr += wstr1;
						wstr += " 71....+ACCURACY";
						fprintf (fo, "%s\n", wstr);
						GetDlgItem(IDC_STATUS)->SetWindowText("Accuracy!");
						break;
					default:
						GetDlgItem(IDC_HZ_ANGLE)->SetWindowText("");
						GetDlgItem(IDC_V_ANGLE)->SetWindowText("");
						GetDlgItem(IDC_SLOPE)->SetWindowText("");
//						fprintf (fo, "{5 %s} {4 ERROR}\n");
//						fprintf (fo, "5=%s\n4=ERROR\n");
						wstr.Format("11%04d+", n);
						for (k = 0; k < 8 - (signed int) strlen(Directions[i].pid); k++)
							wstr += "0";
						wstr += Directions[i].pid;
						wstr += " 71....+ERROROBS";
						fprintf (fo, "%s\n", wstr);
						GetDlgItem(IDC_STATUS)->SetWindowText("Error");
						break;
				}
			}
			Invalidate(100);	// redraw dialog
			DoEvents();			// process events
		}
	}
	fclose(fo);
	GetDlgItem(IDC_GETANGLES)->EnableWindow (TRUE);
	GetDlgItem(IDC_ALL)->EnableWindow (TRUE);
	GetDlgItem(IDC_OFFLINE_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_MOVEONLY_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_MOVE_BUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_HZ_ANGLE_SET)->EnableWindow (TRUE);
	GetDlgItem(IDC_V_ANGLE_SET)->EnableWindow (TRUE);
	GetDlgItem(IDC_STOPBUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_SOURCEBUTTON)->EnableWindow (TRUE);
	stop = 0;
}

void CRobotDlg::DoEvents(void)
{
	MSG msg;

	// van varakozo esemeny?
	while (::PeekMessage(&msg,NULL,0,0,PM_NOREMOVE))
	{
		// esemeny feldolgozas kikenyszeritese
		AfxGetThread()->PumpMessage();
	}
}

void CRobotDlg::OnStopbutton() 
{
	stop = 1;	
}

void CRobotDlg::OnStartbutton() 
{
	// Start tracking & log
	GRC_TYPE Result;
	TMC_HZ_V_ANG angles;
	double dist, north, east, height, sd, north_last, east_last, height_last, bearing, speed;
	unsigned long delay;
	CString ha, va, d, ha_last, va_last, d_last, wstr;
	int tried, max_try = 3, ifdist;
	FILE *fo;
	COleDateTime act, act_last;
	// get log file
	char filter[] = "Log file (*.log)| *.log||";
	CFileDialog fDlg (TRUE, ".gsi", NULL, OFN_HIDEREADONLY, filter);
	if (fDlg.DoModal () != IDOK) return;
	CString file_name = fDlg.GetPathName ();
	fo = fopen(file_name, "a");
	
	GetDlgItem(IDC_DELAY)->GetWindowText(wstr);
	delay = (unsigned long)(atof(wstr) * 1000);
	ifdist = ((CButton *)GetDlgItem(IDC_DISTCHECK))->GetCheck();

	GetDlgItem(IDC_STARTBUTTON)->EnableWindow (FALSE);
	GetDlgItem(IDC_DISTCHECK)->EnableWindow (FALSE);
	GetDlgItem(IDC_DELAY)->EnableWindow (FALSE);
	GetDlgItem(IDC_STOPTRACEBUTTON)->EnableWindow (TRUE);
	((CButton *)GetDlgItem(IDC_ATRCHECK))->SetCheck(1);
	// turn on ATR
	Result = AUT_SetATRStatus(ON);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_SetATRStatus");
		return;
	}
	// start position on target
	Result = TMC_GetAngle(angles, TMC_AUTO_INC);
	Result = AUT_MakePositioning(angles.dHz, angles.dV, AUT_PRECISE, AUT_TARGET, FALSE);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "Prism not found");
		GetDlgItem(IDC_STARTBUTTON)->EnableWindow (TRUE);
		GetDlgItem(IDC_DISTCHECK)->EnableWindow (TRUE);
		GetDlgItem(IDC_DELAY)->EnableWindow (TRUE);
		GetDlgItem(IDC_STOPTRACEBUTTON)->EnableWindow (FALSE);
		return;
	}
	// make a measurement to check we are on prism
	Result = TMC_DoMeasure(TMC_DEF_DIST, TMC_AUTO_INC);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "TMC_DoMeasure");
		return;
	}
	// distance measurement successful
	Result = TMC_GetSimpleMea(3000, angles, dist, TMC_AUTO_INC);
	switch (Result) {
		case GRC_OK :
			ha_last = dms(angles.dHz);
			va_last = dms(angles.dV);
			GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(ha_last);
			GetDlgItem(IDC_V_ANGLE)->SetWindowText(va_last);
			d_last.Format("%.4f", dist);
			GetDlgItem(IDC_SLOPE)->SetWindowText(d_last);
			act = COleDateTime::GetCurrentTime();
			wstr.Format("%d%02d%02d%02d%02d%02d", act.GetYear (), act.GetMonth (), act.GetDay (), 
				act.GetHour(), act.GetMinute(), act.GetSecond());
			fprintf (fo, "%s,%s,%s,%s\n", wstr, ha_last, va_last, d_last);
			act_last = act;
			// relative coordinates from station
			north_last = dist * sin(angles.dV) * cos(angles.dHz);
			east_last = dist * sin(angles.dV) * sin(angles.dHz);
			height_last = dist * cos(angles.dV);
			break;
		case TMC_ACCURACY_GUARANTEE:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			break;
		default:
			COM_ViewError(Result, "TMC_GetSimpleMea");
			return;
	}
	Result = AUT_SetLockStatus(ON);
	if (Result != GRC_OK) {
			COM_ViewError(Result, "AUS_SetUserLockState");
			return;
	}
	Result = AUT_LockIn();
	if (Result != GRC_OK) {
			COM_ViewError(Result, "AUT_LockIn");
			return;
	}
	// stop = 1;
	Sleep (delay);
	while (stop == 0) {
		tried = 0;		// try max_try observation in case of error
		if (ifdist) {
			Result = TMC_DoMeasure(TMC_DEF_DIST, TMC_AUTO_INC);
			if (Result != GRC_OK) {
//				COM_ViewError(Result, "TMC_DoMeasure");
				fprintf (fo, "DO_MEASURE ERROR: %d\n", Result);
				continue;
			}
		} else {
			d_last = "";
		}
		Result = TMC_GetSimpleMea(3000, angles, dist, TMC_AUTO_INC);
		switch (Result) {
			case GRC_OK :
			case GRC_TMC_ANGLE_OK:
				tried = 0;
				ha = dms(angles.dHz);
				va = dms(angles.dV);
				GetDlgItem(IDC_HZ_ANGLE)->SetWindowText(ha);
				GetDlgItem(IDC_V_ANGLE)->SetWindowText(va);
				if (ifdist) {
					d.Format("%.4f", dist);
					GetDlgItem(IDC_SLOPE)->SetWindowText(d);
				} else {
					d = "";
					dist = 0;
					GetDlgItem(IDC_SLOPE)->SetWindowText(d);
				}
				if (ha != ha_last || va != va_last || d != d_last) {
					// if changed store data
					act = COleDateTime::GetCurrentTime();
					wstr.Format("%d%02d%02d%02d%02d%02d", act.GetYear (), act.GetMonth (), act.GetDay (), 
						act.GetHour(), act.GetMinute(), act.GetSecond());
					fprintf (fo, "%s,%s,%s,%s\n", wstr, ha, va, d);
					fflush(fo);
					if (ifdist) {
						// relative coordinates from station
						north = dist * sin(angles.dV) * cos(angles.dHz);
						east = dist * sin(angles.dV) * sin(angles.dHz);
						height = dist * cos(angles.dV);
						// calculate speed and direction
						sd = hypot(hypot(north - north_last, east - east_last), height - height_last);
						speed = sd / (act - act_last).GetTotalSeconds();
						wstr.Format("%.3f", speed);
						GetDlgItem(IDC_SPEEDEDIT)->SetWindowText(wstr);
						if (speed > 0.0001) {
							bearing = atan2(north - north_last, east - east_last);
							if (bearing < 0) bearing += 2.0 * PI;
							wstr = dms(bearing);
						} else {
							wstr = "";
						}
						GetDlgItem(IDC_BEARINGEDIT)->SetWindowText(wstr);
					}
				}
				ha_last = ha; va_last = va; d_last = d;
				act_last = act;
				break;
			case TMC_ACCURACY_GUARANTEE:
				fprintf (fo, "TMC_GetSimpleMea: TMC_ACCURACY_GUARANTEE\n");
//				COM_ViewError(Result, "TMC_GetSimpleMea");
				break;
			default:
				fprintf (fo, "TMC_GetSimpleMea: %d\n", Result);
//				COM_ViewError(Result, "TMC_GetSimpleMea");
//				return;
				tried++;
				if (tried > max_try) 
					fprintf (fo, "MAX_TRY\n");
		}
		Invalidate(100);	// redraw dialog
		DoEvents();			// process events
		Sleep (delay);
	}
	stop = 0;
	fclose (fo);
	Result = AUT_SetLockStatus(OFF);
	// set back atr state
	Result = AUT_SetATRStatus(((CButton *)GetDlgItem(IDC_ATRCHECK))->GetCheck() ? ON : OFF);

	GetDlgItem(IDC_STARTBUTTON)->EnableWindow (TRUE);
	GetDlgItem(IDC_DISTCHECK)->EnableWindow (TRUE);
	GetDlgItem(IDC_DELAY)->EnableWindow (TRUE);
	GetDlgItem(IDC_STOPTRACEBUTTON)->EnableWindow (FALSE);
}

void CRobotDlg::OnStoptracebutton() 
{
	// TODO: Add your control notification handler code here
	stop = 1;
}

void CRobotDlg::OnAtrcheck() 
{
	ON_OFF_TYPE newstate;
	GRC_TYPE Result;

	// change ATR state
	newstate = ((CButton *)GetDlgItem(IDC_ATRCHECK))->GetCheck() ? ON : OFF;
	Result = AUT_SetATRStatus(newstate);
	if (Result != GRC_OK) {
		COM_ViewError(Result, "AUT_SetATRStatus");
	}
}
