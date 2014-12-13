// AsciiDlg.cpp : implementation file
//

#include "stdafx.h"
#include "robot.h"
#include "AsciiDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAsciiDlg dialog


CAsciiDlg::CAsciiDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CAsciiDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CAsciiDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CAsciiDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAsciiDlg)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CAsciiDlg, CDialog)
	//{{AFX_MSG_MAP(CAsciiDlg)
	ON_BN_CLICKED(IDC_SEND_BUTTON, OnSendButton)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAsciiDlg message handlers

void CAsciiDlg::OnSendButton() 
{
	// TODO: Add your control notification handler code here
	
}
