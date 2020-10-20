# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 18:08:55 2020

@author: MarcelloCavalcanti
"""

    def fromApp(self, message, sessionID):
        #global _report
        Oda_Type = {'1':'Market', '2':'Limit', '3':'Stop'}
        Oda_Status = {'0':'New', '1':'Partially Filled', '2':'Filled', '4':'Cancelled', '8':'Rejected'}
        self.logger.info('Received app message = %s.', Read_FIX_Message(message))
        
        # Get incoming message Type
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        msgType = msgType.getValue()
        
        # Get timestamp (tag 52)
        _Timestamp = fix.SendingTime()
        message.getHeader().getField(_Timestamp)
        _Timestamp = _Timestamp.getString()
        
        print('[fromApptoTrader] {}'.format(Read_FIX_Message(message)))
        
        if msgType == fix.MsgType_ExecutionReport:
            # Extract fields from the message here and pass to an upper layer
            print("[fromApptoTrader] Execution Report Received!")
            
            if extract_message_field_value(fix.ExecType(), message) == 'I': # Order Status Req or System Restart/Re-send Req, need to skip as fields replied are different and kill the kernel
                pass #print('Order_Status = %s'% (Oda_Status[extract_message_field_value(fix.OrdStatus(), message)])) #Order_Status = 0 (New) or =8 (Rejected)
            else: 
                _report = {'Time': _Timestamp, \
                           'Order_Type': Oda_Type[extract_message_field_value(fix.OrdType(), message)], \
                           'Side': str(np.where(extract_message_field_value(fix.Side(), message) == '1', 'BUY','SELL')), \
                           'ccy': extract_message_field_value(fix.Symbol(), message), \
                           'Avg_Px': extract_message_field_value(fix.AvgPx(), message), \
                           'Cum_Qty': extract_message_field_value(fix.CumQty(), message), \
                           'Order_Px': extract_message_field_value(fix.Price(), message), \
                           'Order_Qty': extract_message_field_value(fix.OrderQty(), message), \
                           'Order_Status': Oda_Status[extract_message_field_value(fix.OrdStatus(), message)], \
                           'Clnt_Order_ID': extract_message_field_value(fix.ClOrdID(), message), \
                           'Exec_Order_ID': extract_message_field_value(fix.ExecID(), message)}
                print('')
                print(_report)
                print('')
                ###ADD CONTROL CHECK THAT EXECUTION MATCHES curr_pos###
                
                ###Logging Server Response###
                srv_resp = pd.Series({'TimeStamp':_report['Time'],'ClOrdId':_report['Clnt_Order_ID'],'Serv_Id':'',\
                                      'symbol':_report['ccy'],'side':_report['Side'],'quantity':_report['Cum_Qty'],'type':_report['Order_Type'],\
                                      'price':_report['Avg_Px'],'TIF':'1', 'Order_Status':_report['Order_Status']})
                
                self._Trade_Logger = self._Trade_Logger.append(srv_resp, ignore_index=True)
        
        elif msgType == fix.MsgType_OrderCancelReject:
            # Extract fields from the message here and pass to an upper layer
            print("[fromApptoTrader] Order Cancel REJECT Received!")
