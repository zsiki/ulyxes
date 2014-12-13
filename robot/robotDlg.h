// robotDlg.h : header file
//

#if !defined(AFX_ROBOTDLG_H__9A946916_3460_4E0D_9E0A_0B9BFC2599F8__INCLUDED_)
#define AFX_ROBOTDLG_H__9A946916_3460_4E0D_9E0A_0B9BFC2599F8__INCLUDED_

#include "com_pub.hpp"

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CRobotDlg dialog

class CRobotDlg : public CDialog
{
// Construction
public:
	CRobotDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CRobotDlg)
	enum { IDD = IDD_ROBOT_DIALOG };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CRobotDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL
// com setup data
protected:
	COM_BAUD_RATE BaudRate;
	COM_PORT Port;
	COM_FORMAT Protocol;
	int stop;
// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CRobotDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnSetupbutton();
	afx_msg void OnOnlineButton();
	afx_msg void OnOfflineButton();
	afx_msg void OnGetangles();
	afx_msg void OnAll();
	afx_msg void OnMoveButton();
	afx_msg void OnMoveonlyButton();
	afx_msg void OnSourcebutton();
	afx_msg void OnStopbutton();
	afx_msg void OnStartbutton();
	afx_msg void OnStoptracebutton();
	afx_msg void OnAtrcheck();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
//
	CString dms(double a, int opt = 0);
	double rad(CString a);
	void DoEvents(void);
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ROBOTDLG_H__9A946916_3460_4E0D_9E0A_0B9BFC2599F8__INCLUDED_)
