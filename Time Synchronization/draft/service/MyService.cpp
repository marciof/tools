// MyService.cpp : Defines the initialization routines for the DLL.
//  This is a sample service that can be used as a template to write your own
//  service.
//
//  In order to run this service you need to make sure you have the following keys set at
//  device Start-Up:
//
//    [HKEY_LOCAL_MACHINE\Services\MyService]
//    "Dll"="MyService.dll"
//    "Order"=dword:8
//    "Keep"=dword:1
//    "Prefix"="SRV"
//    "Index"=dword:0
//    "Context"=dword:0
//    "DisplayName"="Sample MFC Service"
//    "Description"="This sample service makes your device beep about every 10 seconds."
//
//  This service has been written to help you write your own. Following these steps will make it easier for you:
//   1.- At installation time write the registry keys above, and copy this service dll to the \Windows folder.
//   2.- Soft boot your device or write a program similar to the installation program described by 
//       Victor Sharov and Vassili Philippov on the  Pocket PC Services article.
//   3.- If the service loaded correctly you should be able to hear your device beep about every 10 seconds.
//   4.- Modify this service to meet your needs.
//
#include "stdafx.h"
#include "MyService.h"
#include <Winbase.h>
#include <service.h>

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

//
//	Note!
//
//		If this DLL is dynamically linked against the MFC
//		DLLs, any functions exported from this DLL which
//		call into MFC must have the AFX_MANAGE_STATE macro
//		added at the very beginning of the function.
//
//		For example:
//
//		extern "C" BOOL PASCAL EXPORT ExportedFunction()
//		{
//			AFX_MANAGE_STATE(AfxGetStaticModuleState());
//			// normal function body here
//		}
//
//		It is very important that this macro appear in each
//		function, prior to any calls into MFC.  This means that
//		it must appear as the first statement within the 
//		function, even before any object variable declarations
//		as their constructors may generate calls into the MFC
//		DLL.
//
//		Please see MFC Technical Notes 33 and 58 for additional
//		details.
//

/////////////////////////////////////////////////////////////////////////////
// CMyServiceApp

BEGIN_MESSAGE_MAP(CMyServiceApp, CWinApp)
	//{{AFX_MSG_MAP(CMyServiceApp)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMyServiceApp construction

CMyServiceApp::CMyServiceApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CMyServiceApp object

CMyServiceApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CMyServiceApp initialization

BOOL CMyServiceApp::InitInstance()
{
	if (!AfxSocketInit())
	{
		AfxMessageBox(IDP_SOCKETS_INIT_FAILED);
		return FALSE;
	}

	return TRUE;
}

/// FORWARD DECLARATIONS:
UINT MyControllingFunction( LPVOID pParam );



/// These are exported functions definitions. 
/// This means that these functions will be exported from this DLL. The AFX_MANAGE_STATE macro is 
/// used in order to delay load all the MFC functions.


//This function is implemented by a service and will be called by Services.exe. 
extern "C" DWORD PASCAL EXPORT SRV_Close(DWORD dwData)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  // Return 1 indicates success, 0 indicates failure.
  return 1;
}
 
extern "C" DWORD PASCAL EXPORT SRV_Deinit(DWORD dwData)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  //Services.exe ignores the value returned by this function.
  return 0;
}
 
 
//Initialize the service
extern "C" DWORD PASCAL EXPORT SRV_Init(DWORD dwData)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());  
  // Replace the code below with your code.
  MessageBeep(0xFFFFFFFF);
  theApp.m_pThread = AfxBeginThread( MyControllingFunction, 0);
  //You need to return a non zero value here. 0 means that the service initialization failed.
  return 1; 
}

 
//This function is used to send a control code to a service. 
extern "C" DWORD PASCAL EXPORT SRV_IOControl(
  DWORD dwData,
  DWORD dwCode,
  PBYTE pBufIn,
  DWORD dwLenIn,
  PBYTE pBufOut,
  DWORD dwLenOut,
  PDWORD pdwActualOut)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  // Insert your code here   
  // Return 1 indicates success, 0 indicates failure.
  return 1;
}
 
extern "C" DWORD PASCAL EXPORT SRV_Open(
  DWORD dwData,
  DWORD dwAccess,
  DWORD dwShareMode)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  // Return 1 indicates success, 0 indicates failure.  
  return 0;
}
 
extern "C" DWORD PASCAL EXPORT SRV_Read(
  DWORD dwData,
  LPVOID pBuf,
  DWORD dwLen)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  //Insert your code here.
  //Return the number of bytes read.
  return 0;
}
 
extern "C" DWORD PASCAL EXPORT SRV_Seek(
  DWORD dwData,
  long pos,
  DWORD type)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  // Returns the current location of the file pointer.
  return 0;
}
 
extern "C" DWORD PASCAL EXPORT SRV_Write(
  DWORD dwData,
  LPCVOID pInBuf,
  DWORD dwInLen)
{
  AFX_MANAGE_STATE(AfxGetStaticModuleState());
  //Insert your code here.
  //Returns the number of bytes actually written.
  return 0;
}


//Application specific stuff
void CALLBACK EXPORT MyTimerProc(
   HWND hWnd,      // handle of CWnd that called SetTimer
   UINT nMsg,      // WM_TIMER
   UINT nIDEvent,  // timer identification
   DWORD dwTime    // system time
   )
{
    //Beep every time the timer is triggered.
    MessageBeep(0xFFFFFFFF);
};


UINT MyControllingFunction( LPVOID pParam )
{
  theApp.m_uCounter = 0;

  // This will call MyTimerProc about every seconds. It might take longer
  // as services run in the background. In this specific case MyTimerProc will
  // produce a beep about every ten seconds.
  theApp.m_nTimer = SetTimer(0, 0, 10 * 1000, MyTimerProc); 
 
  MSG msg;
  while (GetMessage(&msg, 0, 0, 0))
  {
         TranslateMessage(&msg);
         DispatchMessage(&msg);
  }
  return 0;
}

/// End of Service