; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CRobotDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "robot.h"
LastPage=0

ClassCount=5
Class1=CRobotApp
Class2=CAboutDlg
Class3=CRobotDlg

ResourceCount=4
Resource1=IDD_ABOUTBOX (English (U.S.))
Resource2=IDD_ASCII_DIALOG
Class4=CSetupDlg
Resource3=IDD_ROBOT_DIALOG (English (U.S.))
Class5=CAsciiDlg
Resource4=IDD_SETUP (English (U.S.))

[CLS:CRobotApp]
Type=0
BaseClass=CWinApp
HeaderFile=robot.h
ImplementationFile=robot.cpp
LastObject=CRobotApp

[CLS:CAboutDlg]
Type=0
BaseClass=CDialog
HeaderFile=robotDlg.cpp
ImplementationFile=robotDlg.cpp
LastObject=CAboutDlg

[CLS:CRobotDlg]
Type=0
BaseClass=CDialog
HeaderFile=robotDlg.h
ImplementationFile=robotDlg.cpp
LastObject=IDC_DISTCHECK
Filter=D
VirtualFilter=dWC

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg

[DLG:IDD_ROBOT_DIALOG]
Type=1
Class=CRobotDlg

[DLG:IDD_ABOUTBOX (English (U.S.))]
Type=1
Class=?
ControlCount=4
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889

[DLG:IDD_ROBOT_DIALOG (English (U.S.))]
Type=1
Class=?
ControlCount=45
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1073807360
Control3=IDC_SETUPBUTTON,button,1342242816
Control4=IDC_SETUP,edit,1350633600
Control5=IDC_ONLINE_BUTTON,button,1342242816
Control6=IDC_OFFLINE_BUTTON,button,1476460544
Control7=IDC_GETANGLES,button,1476460544
Control8=IDC_HZ_ANGLE,edit,1484849280
Control9=IDC_V_ANGLE,edit,1484849280
Control10=IDC_STATIC,static,1342308352
Control11=IDC_STATIC,static,1342308352
Control12=IDC_ALL,button,1476460544
Control13=IDC_STATIC,static,1342308352
Control14=IDC_SLOPE,edit,1484849280
Control15=IDC_STATIC,button,1342177287
Control16=IDC_STATIC,button,1342177287
Control17=IDC_STATIC,button,1342177287
Control18=IDC_HZ_ANGLE_SET,edit,1484849280
Control19=IDC_V_ANGLE_SET,edit,1484849280
Control20=IDC_STATIC,static,1342308352
Control21=IDC_STATIC,static,1342308352
Control22=IDC_STATIC,static,1342308352
Control23=IDC_SLOPE2,edit,1484849280
Control24=IDC_MOVE_BUTTON,button,1476460544
Control25=IDC_MOVEONLY_BUTTON,button,1476460544
Control26=IDC_STATIC,button,1342177287
Control27=IDC_SOURCEBUTTON,button,1476460544
Control28=IDC_POINTID,edit,1484849280
Control29=IDC_STATIC,static,1342308352
Control30=IDC_STATIC,static,1342308352
Control31=IDC_STATUS,edit,1484849280
Control32=IDC_STOPBUTTON,button,1476460544
Control33=IDC_STATIC,button,1342177287
Control34=IDC_STARTBUTTON,button,1476460544
Control35=IDC_STOPTRACEBUTTON,button,1476460544
Control36=IDC_STATIC,static,1342308352
Control37=IDC_SPEEDEDIT,edit,1484849280
Control38=IDC_STATIC,static,1342308352
Control39=IDC_BEARINGEDIT,edit,1484849280
Control40=IDC_STATIC,static,1342308352
Control41=IDC_DELAY,edit,1484849280
Control42=IDC_STATIC,static,1342308352
Control43=IDC_STATIC,static,1342308352
Control44=IDC_DISTCHECK,button,1476460547
Control45=IDC_ATRCHECK,button,1476460547

[DLG:IDD_SETUP (English (U.S.))]
Type=1
Class=CSetupDlg
ControlCount=18
Control1=IDC_RADIO_COM1,button,1342308361
Control2=IDC_RADIO_COM2,button,1342177289
Control3=IDC_RADIO_COM3,button,1342177289
Control4=IDC_RADIO_COM4,button,1342177289
Control5=IDC_RADIO_COM5,button,1342177289
Control6=IDC_RADIO_COM6,button,1342177289
Control7=IDC_RADIO_ASCII,button,1342308361
Control8=IDC_RADIO_BINARY,button,1342177289
Control9=IDC_RADIO_38400,button,1342308361
Control10=IDC_RADIO_19200,button,1342177289
Control11=IDC_RADIO_9600,button,1342177289
Control12=IDC_RADIO_4800,button,1342177289
Control13=IDC_RADIO_2400,button,1342177289
Control14=IDOK,button,1342242817
Control15=IDCANCEL,button,1342242816
Control16=IDC_GROUP_PORT,button,1342309127
Control17=IDC_GROUP_BAUD,button,1342309127
Control18=IDC_GROUP_PROTOCOL,button,1342309127

[CLS:CSetupDlg]
Type=0
HeaderFile=SetupDlg.h
ImplementationFile=SetupDlg.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CSetupDlg

[DLG:IDD_ASCII_DIALOG]
Type=1
Class=CAsciiDlg
ControlCount=6
Control1=IDOK,button,1342242817
Control2=IDC_STATIC,static,1342308352
Control3=IDC_EDIT1,edit,1350631552
Control4=IDC_SEND_BUTTON,button,1342242816
Control5=IDC_STATIC,static,1342308352
Control6=IDC_EDIT2,edit,1484849280

[CLS:CAsciiDlg]
Type=0
HeaderFile=AsciiDlg.h
ImplementationFile=AsciiDlg.cpp
BaseClass=CDialog
Filter=D
LastObject=CAsciiDlg
VirtualFilter=dWC

