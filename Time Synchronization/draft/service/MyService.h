// MyService.h : main header file for the MYSERVICE DLL
//

#if !defined(AFX_MYSERVICE_H__A07E1A0B_0914_4A5B_8D8B_7194AB639021__INCLUDED_)
#define AFX_MYSERVICE_H__A07E1A0B_0914_4A5B_8D8B_7194AB639021__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CMyServiceApp
// See MyService.cpp for the implementation of this class
//

class CMyServiceApp : public CWinApp
{
public:
	CMyServiceApp();
//Added variables, might be functionality dependent:
    UINT m_nTimer;
    UINT m_uCounter;
    CWinThread* m_pThread;

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMyServiceApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

	//{{AFX_MSG(CMyServiceApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MYSERVICE_H__A07E1A0B_0914_4A5B_8D8B_7194AB639021__INCLUDED_)
