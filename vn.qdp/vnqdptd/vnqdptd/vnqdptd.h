//˵������
/*
����CTP API�к��ʽ�ת����صĺ���̫�࣬
ͬʱҲ�Ѿ��д����Ŀͻ���֧����Щ���ܣ�
��������Python��װ����ʱѡ��ֻ֧�ֽ��׹���
*/


//ϵͳ
#ifdef WIN32
#include "stdafx.h"
#endif
#include <string>
#include <queue>

//Boost
#define BOOST_PYTHON_STATIC_LIB
#include <boost/python/module.hpp>	//python��װ
#include <boost/python/def.hpp>		//python��װ
#include <boost/python/dict.hpp>	//python��װ
#include <boost/python/object.hpp>	//python��װ
#include <boost/python.hpp>			//python��װ
#include <boost/thread.hpp>			//������е��̹߳���
#include <boost/bind.hpp>			//������е��̹߳���
#include <boost/any.hpp>			//������е�����ʵ��

//API
#include "QdpFtdcTraderApi.h"

//�����ռ�
using namespace std;
using namespace boost::python;
using namespace boost;

//����
#define ONFRONTCONNECTED 1
#define ONFRONTDISCONNECTED 2
#define ONHEARTBEATWARNING 3
#define ONRSPAUTHENTICATE 4
#define ONRSPUSERLOGIN 5
#define ONRSPUSERLOGOUT 6
#define ONRSPUSERPASSWORDUPDATE 7
#define ONRSPTRADINGACCOUNTPASSWORDUPDATE 8
#define ONRSPORDERINSERT 9
#define ONRSPPARKEDORDERINSERT 10
#define ONRSPPARKEDORDERACTION 11
#define ONRSPORDERACTION 12
#define ONRSPQUERYMAXORDERVOLUME 13
#define ONRSPSETTLEMENTINFOCONFIRM 14
#define ONRSPREMOVEPARKEDORDER 15
#define ONRSPREMOVEPARKEDORDERACTION 16
#define ONRSPEXECORDERINSERT 17
#define ONRSPEXECORDERACTION 18
#define ONRSPFORQUOTEINSERT 19
#define ONRSPQUOTEINSERT 20
#define ONRSPQUOTEACTION 21
#define ONRSPLOCKINSERT 22
#define ONRSPCOMBACTIONINSERT 23
#define ONRSPQRYORDER 24
#define ONRSPQRYTRADE 25
#define ONRSPQRYINVESTORPOSITION 26
#define ONRSPQRYTRADINGACCOUNT 27
#define ONRSPQRYINVESTOR 28
#define ONRSPQRYTRADINGCODE 29
#define ONRSPQRYINSTRUMENTMARGINRATE 30
#define ONRSPQRYINSTRUMENTCOMMISSIONRATE 31
#define ONRSPQRYEXCHANGE 32
#define ONRSPQRYPRODUCT 33
#define ONRSPQRYINSTRUMENT 34
#define ONRSPQRYDEPTHMARKETDATA 35
#define ONRSPQRYSETTLEMENTINFO 36
#define ONRSPQRYTRANSFERBANK 37
#define ONRSPQRYINVESTORPOSITIONDETAIL 38
#define ONRSPQRYNOTICE 39
#define ONRSPQRYSETTLEMENTINFOCONFIRM 40
#define ONRSPQRYINVESTORPOSITIONCOMBINEDETAIL 41
#define ONRSPQRYCFMMCTRADINGACCOUNTKEY 42
#define ONRSPQRYEWARRANTOFFSET 43
#define ONRSPQRYINVESTORPRODUCTGROUPMARGIN 44
#define ONRSPQRYEXCHANGEMARGINRATE 45
#define ONRSPQRYEXCHANGEMARGINRATEADJUST 46
#define ONRSPQRYEXCHANGERATE 47
#define ONRSPQRYSECAGENTACIDMAP 48
#define ONRSPQRYPRODUCTEXCHRATE 49
#define ONRSPQRYPRODUCTGROUP 50
#define ONRSPQRYOPTIONINSTRTRADECOST 51
#define ONRSPQRYOPTIONINSTRCOMMRATE 52
#define ONRSPQRYEXECORDER 53
#define ONRSPQRYFORQUOTE 54
#define ONRSPQRYQUOTE 55
#define ONRSPQRYLOCK 56
#define ONRSPQRYLOCKPOSITION 57
#define ONRSPQRYINVESTORLEVEL 58
#define ONRSPQRYEXECFREEZE 59
#define ONRSPQRYCOMBINSTRUMENTGUARD 60
#define ONRSPQRYCOMBACTION 61
#define ONRSPQRYTRANSFERSERIAL 62
#define ONRSPQRYACCOUNTREGISTER 63
#define ONRSPERROR 64
#define ONRTNORDER 65
#define ONRTNTRADE 66
#define ONERRRTNORDERINSERT 67
#define ONERRRTNORDERACTION 68
#define ONRTNINSTRUMENTSTATUS 69
#define ONRTNTRADINGNOTICE 70
#define ONRTNERRORCONDITIONALORDER 71
#define ONRTNEXECORDER 72
#define ONERRRTNEXECORDERINSERT 73
#define ONERRRTNEXECORDERACTION 74
#define ONERRRTNFORQUOTEINSERT 75
#define ONRTNQUOTE 76
#define ONERRRTNQUOTEINSERT 77
#define ONERRRTNQUOTEACTION 78
#define ONRTNFORQUOTERSP 79
#define ONRTNCFMMCTRADINGACCOUNTTOKEN 80
#define ONRTNLOCK 81
#define ONERRRTNLOCKINSERT 82
#define ONRTNCOMBACTION 83
#define ONERRRTNCOMBACTIONINSERT 84
#define ONRSPQRYCONTRACTBANK 85
#define ONRSPQRYPARKEDORDER 86
#define ONRSPQRYPARKEDORDERACTION 87
#define ONRSPQRYTRADINGNOTICE 88
#define ONRSPQRYBROKERTRADINGPARAMS 89
#define ONRSPQRYBROKERTRADINGALGOS 90
#define ONRSPQUERYCFMMCTRADINGACCOUNTTOKEN 91
#define ONRTNFROMBANKTOFUTUREBYBANK 92
#define ONRTNFROMFUTURETOBANKBYBANK 93
#define ONRTNREPEALFROMBANKTOFUTUREBYBANK 94
#define ONRTNREPEALFROMFUTURETOBANKBYBANK 95
#define ONRTNFROMBANKTOFUTUREBYFUTURE 96
#define ONRTNFROMFUTURETOBANKBYFUTURE 97
#define ONRTNREPEALFROMBANKTOFUTUREBYFUTUREMANUAL 98
#define ONRTNREPEALFROMFUTURETOBANKBYFUTUREMANUAL 99
#define ONRTNQUERYBANKBALANCEBYFUTURE 100
#define ONERRRTNBANKTOFUTUREBYFUTURE 101
#define ONERRRTNFUTURETOBANKBYFUTURE 102
#define ONERRRTNREPEALBANKTOFUTUREBYFUTUREMANUAL 103
#define ONERRRTNREPEALFUTURETOBANKBYFUTUREMANUAL 104
#define ONERRRTNQUERYBANKBALANCEBYFUTURE 105
#define ONRTNREPEALFROMBANKTOFUTUREBYFUTURE 106
#define ONRTNREPEALFROMFUTURETOBANKBYFUTURE 107
#define ONRSPFROMBANKTOFUTUREBYFUTURE 108
#define ONRSPFROMFUTURETOBANKBYFUTURE 109
#define ONRSPQUERYBANKACCOUNTMONEYBYFUTURE 110
#define ONRTNOPENACCOUNTBYBANK 111
#define ONRTNCANCELACCOUNTBYBANK 112
#define ONRTNCHANGEACCOUNTBYBANK 113
#define ONRSPQRYUSERINVESTOR 114



///-------------------------------------------------------------------------------------
///API�еĲ������
///-------------------------------------------------------------------------------------

//GILȫ�����򻯻�ȡ�ã�
//���ڰ���C++�̻߳��GIL�����Ӷ���ֹpython����
class PyLock
{
private:
	PyGILState_STATE gil_state;

public:
	//��ĳ�����������д����ö���ʱ�����GIL��
	PyLock()
	{
		gil_state = PyGILState_Ensure();
	}

	//��ĳ��������ɺ����ٸö���ʱ�����GIL��
	~PyLock()
	{
		PyGILState_Release(gil_state);
	}
};


//����ṹ��
struct Task
{
	int task_name;		//�ص��������ƶ�Ӧ�ĳ���
	any task_data;		//���ݽṹ��
	any task_error;		//����ṹ��
	int task_id;		//����id
	bool task_last;		//�Ƿ�Ϊ��󷵻�
};


///�̰߳�ȫ�Ķ���
template<typename Data>

class ConcurrentQueue
{
private:
	queue<Data> the_queue;								//��׼�����
	mutable mutex the_mutex;							//boost������
	condition_variable the_condition_variable;			//boost��������

public:

	//�����µ�����
	void push(Data const& data)
	{
		mutex::scoped_lock lock(the_mutex);				//��ȡ������
		the_queue.push(data);							//������д�������
		lock.unlock();									//�ͷ���
		the_condition_variable.notify_one();			//֪ͨ���������ȴ����߳�
	}

	//�������Ƿ�Ϊ��
	bool empty() const
	{
		mutex::scoped_lock lock(the_mutex);
		return the_queue.empty();
	}

	//ȡ��
	Data wait_and_pop()
	{
		mutex::scoped_lock lock(the_mutex);

		while (the_queue.empty())						//������Ϊ��ʱ
		{
			the_condition_variable.wait(lock);			//�ȴ���������֪ͨ
		}

		Data popped_value = the_queue.front();			//��ȡ�����е����һ������
		the_queue.pop();								//ɾ��������
		return popped_value;							//���ظ�����
	}

};


//���ֵ��л�ȡĳ����ֵ��Ӧ������������ֵ������ṹ������ֵ��
void getInt(dict d, string key, int* value);


//���ֵ��л�ȡĳ����ֵ��Ӧ�ĸ�����������ֵ������ṹ������ֵ��
void getDouble(dict d, string key, double* value);


//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ�������ֵ������ṹ������ֵ��
void getChar(dict d, string key, char* value);


//���ֵ��л�ȡĳ����ֵ��Ӧ���ַ���������ֵ������ṹ������ֵ��
void getStr(dict d, string key, char* value);


///-------------------------------------------------------------------------------------
///C++ SPI�Ļص���������ʵ��
///-------------------------------------------------------------------------------------

//API�ļ̳�ʵ��
class TdApi : public CQdpFtdcTraderSpi
{
private:
	CQdpFtdcTraderApi* api;			//API����
	thread *task_thread;				//�����߳�ָ�루��python���������ݣ�
	ConcurrentQueue<Task> task_queue;	//�������

public:
	TdApi()
	{
		function0<void> f = boost::bind(&TdApi::processTask, this);
		thread t(f);
		this->task_thread = &t;
	};

	~TdApi()
	{
	};

	//-------------------------------------------------------------------------------------
	//API�ص�����
	//-------------------------------------------------------------------------------------

	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected();

	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	///@param nReason ����ԭ��
	///        0x1001 �����ʧ��
	///        0x1002 ����дʧ��
	///        0x2001 ����������ʱ
	///        0x2002 ��������ʧ��
	///        0x2003 �յ�������
	virtual void OnFrontDisconnected(int nReason);

	///������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
	///@param nTimeLapse �����ϴν��ձ��ĵ�ʱ��
	virtual void OnHeartBeatWarning(int nTimeLapse);

	///��¼������Ӧ
	virtual void OnRspUserLogin(CQdpFtdcRspUserLoginField *pRspUserLogin, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ǳ�������Ӧ
	virtual void OnRspUserLogout(CQdpFtdcRspUserLogoutField *pUserLogout, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�û��������������Ӧ
	virtual void OnRspUserPasswordUpdate(CQdpFtdcUserPasswordUpdateField *pUserPasswordUpdate, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����¼��������Ӧ
	virtual void OnRspOrderInsert(CQdpFtdcInputOrderField *pInputOrder, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///��������������Ӧ
	virtual void OnRspOrderAction(CQdpFtdcOrderActionField *pInputOrderAction, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);


	///�����ѯ������Ӧ
	virtual void OnRspQryOrder(CQdpFtdcOrderField *pOrder, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯ�ɽ���Ӧ
	virtual void OnRspQryTrade(CQdpFtdcTradeField *pTrade, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯͶ���ֲ߳���Ӧ
	virtual void OnRspQryInvestorPosition(CQdpFtdcRspInvestorPositionField *pInvestorPosition, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ�û�Ͷ���˻�
	virtual void OnRspQryUserInvestor(CQdpFtdcRspUserInvestorField *pUserInvestor, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯͶ������Ӧ
	virtual void OnRspQryInvestorAccount(CQdpFtdcRspInvestorAccountField *pInvestor, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ��������Ӧ
	virtual void OnRspQryExchange(CQdpFtdcRspExchangeField *pExchange, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ��Լ��Ӧ
	virtual void OnRspQryInstrument(CQdpFtdcRspInstrumentField *pInstrument, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ������Ӧ
	virtual void OnRspQryMarketData(CQdpFtdcMarketDataField *pDepthMarketData, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�����ѯת����ˮ��Ӧ
	virtual void OnRspQryTransferSerial(CQdpFtdcTransferSerialField *pTransferSerial, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����Ӧ��
	virtual void OnRspError(CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///����֪ͨ
	virtual void OnRtnOrder(CQdpFtdcOrderField *pOrder) ;

	///�ɽ�֪ͨ
	virtual void OnRtnTrade(CQdpFtdcTradeField *pTrade) ;

	///����¼�����ر�
	virtual void OnErrRtnOrderInsert(CQdpFtdcInputOrderField *pInputOrder, CQdpFtdcRspInfoField *pRspInfo) ;

	///������������ر�
	virtual void OnErrRtnOrderAction(CQdpFtdcOrderActionField *pOrderAction, CQdpFtdcRspInfoField *pRspInfo) ;

	///��Լ����״̬֪ͨ
	virtual void OnRtnInstrumentStatus(CQdpFtdcInstrumentStatusField *pInstrumentStatus) ;

	///�����ѯǩԼ������Ӧ
	virtual void OnRspQryContractBank(CQdpFtdcContractBankField *pContractBank, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///���з��������ʽ�ת�ڻ�֪ͨ
	virtual void OnRtnFromBankToFutureByBank(CQdpFtdcRspTransferField *pRspTransfer) ;

	///���з����ڻ��ʽ�ת����֪ͨ
	virtual void OnRtnFromFutureToBankByBank(CQdpFtdcRspTransferField *pRspTransfer) ;

	///�ڻ����������ʽ�ת�ڻ�֪ͨ
	virtual void OnRtnFromBankToFutureByFuture(CQdpFtdcRspTransferField *pRspTransfer) ;

	///�ڻ������ڻ��ʽ�ת����֪ͨ
	virtual void OnRtnFromFutureToBankByFuture(CQdpFtdcRspTransferField *pRspTransfer) ;

	///�ڻ������ѯ�������֪ͨ
	virtual void OnRtnQueryBankBalanceByFuture(CQdpFtdcNotifyQueryAccountField *pNotifyQueryAccount) ;

	///�ڻ����������ʽ�ת�ڻ�����ر�
	virtual void OnErrRtnBankToFutureByFuture(CQdpFtdcReqTransferField *pReqTransfer, CQdpFtdcRspInfoField *pRspInfo) ;

	///�ڻ������ڻ��ʽ�ת���д���ر�
	virtual void OnErrRtnFutureToBankByFuture(CQdpFtdcReqTransferField *pReqTransfer, CQdpFtdcRspInfoField *pRspInfo) ;

	///�ڻ������ѯ����������ر�
	virtual void OnErrRtnQueryBankBalanceByFuture(CQdpFtdcReqQueryAccountField *pReqQueryAccount, CQdpFtdcRspInfoField *pRspInfo) ;

	///�ڻ����������ʽ�ת�ڻ�Ӧ��
	virtual void OnRspFromBankToFutureByFuture(CQdpFtdcReqTransferField *pReqTransfer, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ڻ������ڻ��ʽ�ת����Ӧ��
	virtual void OnRspFromFutureToBankByFuture(CQdpFtdcReqTransferField *pReqTransfer, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;

	///�ڻ������ѯ�������Ӧ��
	virtual void OnRspQueryBankAccountMoneyByFuture(CQdpFtdcReqQueryAccountField *pReqQueryAccount, CQdpFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) ;


	//-------------------------------------------------------------------------------------
	//task������
	//-------------------------------------------------------------------------------------

	void processTask();

	void processFrontConnected(Task task);

	void processFrontDisconnected(Task task);

	void processHeartBeatWarning(Task task);

	void processRspUserLogin(Task task);

	void processRspUserLogout(Task task);

	void processRspQryUserInvestor(Task task);

	void processRspQryContractBank(Task task);

	void processRspQryTransferSerial(Task task);

	void processRtnFromBankToFutureByBank(Task task);

	void processRtnFromFutureToBankByBank(Task task);

	void processRspUserPasswordUpdate(Task task);

	void processRspTradingAccountPasswordUpdate(Task task);

	void processRspOrderInsert(Task task);

	void processRspOrderAction(Task task);

	void processRspQryOrder(Task task);

	void processRspQryTrade(Task task);

	void processRspQryInvestorPosition(Task task);

	void processRspQryInvestorAccount(Task task);

	void processRspQryExchange(Task task);

	void processRspQryInstrument(Task task);

	void processRspQryMarketData(Task task);

	void processRspQryExecFreeze(Task task);

	void processRspQryCombAction(Task task);

	void processRspError(Task task);

	void processRtnOrder(Task task);

	void processRtnTrade(Task task);

	void processErrRtnOrderInsert(Task task);

	void processErrRtnOrderAction(Task task);

	void processRtnInstrumentStatus(Task task);

	void processRtnFromBankToFutureByFuture(Task task);

	void processRtnFromFutureToBankByFuture(Task task);

	void processRtnQueryBankBalanceByFuture(Task task);

	void processErrRtnBankToFutureByFuture(Task task);

	void processErrRtnFutureToBankByFuture(Task task);

	void processErrRtnQueryBankBalanceByFuture(Task task);

	void processRspFromBankToFutureByFuture(Task task);

	void processRspFromFutureToBankByFuture(Task task);

	void processRspQueryBankAccountMoneyByFuture(Task task);

	//-------------------------------------------------------------------------------------
	//data���ص������������ֵ�
	//error���ص������Ĵ����ֵ�
	//id������id
	//last���Ƿ�Ϊ��󷵻�
	//i������
	//-------------------------------------------------------------------------------------

	virtual void onFrontConnected(){};

	virtual void onFrontDisconnected(int i){};

	virtual void onHeartBeatWarning(int i){};

	virtual void onRspAuthenticate(dict data, dict error, int id, bool last) {};

	virtual void onRspUserLogin(dict data, dict error, int id, bool last) {};

	virtual void onRspUserLogout(dict data, dict error, int id, bool last) {};

	virtual void onRspUserPasswordUpdate(dict data, dict error, int id, bool last) {};

	virtual void onRspTradingAccountPasswordUpdate(dict data, dict error, int id, bool last) {};

	virtual void onRspOrderInsert(dict data, dict error, int id, bool last) {};

	virtual void onRspOrderAction(dict data, dict error, int id, bool last) {};

	virtual void onRspQryUserInvestor(dict data, dict error, int id, bool last) {};

	virtual void onRspQryOrder(dict data, dict error, int id, bool last) {};

	virtual void onRspQryTrade(dict data, dict error, int id, bool last) {};

	virtual void onRspQryTransferSerial(dict data, dict error, int id, bool last){};

	virtual void onRspQryInvestorPosition(dict data, dict error, int id, bool last) {};

	virtual void onRspQryInvestorAccount(dict data, dict error, int id, bool last) {};

	virtual void onRspQryInvestor(dict data, dict error, int id, bool last) {};

	virtual void onRspQryExchange(dict data, dict error, int id, bool last) {};

	virtual void onRspQryInstrument(dict data, dict error, int id, bool last) {};

	virtual void onRspQryMarketData(dict data, dict error, int id, bool last) {};

	virtual void onRspError(dict error, int id, bool last) {};

	virtual void onRtnOrder(dict data) {};

	virtual void onRtnTrade(dict data) {};

	virtual void onErrRtnOrderInsert(dict data, dict error) {};

	virtual void onErrRtnOrderAction(dict data, dict error) {};

	virtual void onRtnInstrumentStatus(dict data) {};

	virtual void onRspQryContractBank(dict data, dict error, int id, bool last) {};

	virtual void onRtnFromBankToFutureByBank(dict data) {};

	virtual void onRtnFromFutureToBankByBank(dict data) {};

	virtual void onRtnFromBankToFutureByFuture(dict data) {};

	virtual void onRtnFromFutureToBankByFuture(dict data) {};

	virtual void onRtnQueryBankBalanceByFuture(dict data) {};

	virtual void onErrRtnBankToFutureByFuture(dict data, dict error) {};

	virtual void onErrRtnFutureToBankByFuture(dict data, dict error) {};

	virtual void onErrRtnQueryBankBalanceByFuture(dict data, dict error) {};

	virtual void onRspFromBankToFutureByFuture(dict data, dict error, int id, bool last) {};

	virtual void onRspFromFutureToBankByFuture(dict data, dict error, int id, bool last) {};

	virtual void onRspQueryBankAccountMoneyByFuture(dict data, dict error, int id, bool last) {};



	//-------------------------------------------------------------------------------------
	//req:���������������ֵ�
	//-------------------------------------------------------------------------------------

	void createFtdcTraderApi(string pszFlowPath = "");

	void release();

	void init();

	int join();

	int exit();

	string getTradingDay();

	void registerFront(string pszFrontAddress);

	void subscribePrivateTopic(int nType);

	void subscribePublicTopic(int nType);

	int reqAuthenticate(dict req, int nRequestID);

	int reqUserLogin(dict req, int nRequestID);

	int reqUserLogout(dict req, int nRequestID);

	int reqQryUserInvestor(dict req, int nRequestID);

	int reqUserPasswordUpdate(dict req, int nRequestID);

	int reqTradingAccountPasswordUpdate(dict req, int nRequestID);

	int reqOrderInsert(dict req, int nRequestID);

	int reqParkedOrderInsert(dict req, int nRequestID);

	int reqParkedOrderAction(dict req, int nRequestID);

	int reqOrderAction(dict req, int nRequestID);

	int reqExecOrderInsert(dict req, int nRequestID);

	int reqExecOrderAction(dict req, int nRequestID);

	int reqForQuoteInsert(dict req, int nRequestID);

	int reqQuoteInsert(dict req, int nRequestID);

	int reqQuoteAction(dict req, int nRequestID);

	int reqLockInsert(dict req, int nRequestID);

	int reqCombActionInsert(dict req, int nRequestID);

	int reqQryOrder(dict req, int nRequestID);

	int reqQryTrade(dict req, int nRequestID);

	int reqQryInvestorPosition(dict req, int nRequestID);

	int reqQryInvestorAccount(dict req, int nRequestID);

	int reqQryTradingCode(dict req, int nRequestID);

	int reqQryInstrumentMarginRate(dict req, int nRequestID);

	int reqQryInstrumentCommissionRate(dict req, int nRequestID);

	int reqQryExchange(dict req, int nRequestID);

	int reqQryProduct(dict req, int nRequestID);

	int reqQryInstrument(dict req, int nRequestID);

	int reqQryMarketData(dict req, int nRequestID);

	int reqQryInvestorLevel(dict req, int nRequestID);

	int reqQryExecFreeze(dict req, int nRequestID);

	int reqQryCombInstrumentGuard(dict req, int nRequestID);

	int reqQryCombAction(dict req, int nRequestID);

	int reqQryContractBank(dict req, int nRequestID);

	int reqFromBankToFutureByFuture(dict req, int nRequestID);

	int reqFromFutureToBankByFuture(dict req, int nRequestID);

	int reqQueryBankAccountMoneyByFuture(dict req, int nRequestID);
};

