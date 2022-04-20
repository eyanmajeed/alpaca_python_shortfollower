import json
import boto3
import email
import os
import re
import alpaca_trade_api as tradeapi

BASE_URL = "https://api.alpaca.markets"
API_KEY = ""
SECRET_KEY = ""

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    data = s3.get_object(Bucket=event['Records'][0]['s3']['bucket']['name'], Key=event['Records'][0]['s3']['object']['key'])
    emailbody = data['Body'].read().decode("utf-8")
    
    msg = email.message_from_string(emailbody)
    fromAddress = msg['from']
    mailSubject = msg['subject']
    regex = "\\<(.*?)\\>"
    fromAddress = re.findall(regex, fromAddress)[0]
    
    print('Short Follower Triggered')
    mailSubject = str(mailSubject)
    fromAddress = str(fromAddress)
    print("Email Subject: ",mailSubject)
    print("Email From: ",fromAddress)
    
    para = '(' in mailSubject
    if fromAddress == "info@hindenburgresearch.com":
        if para == True:
            index = mailSubject.rfind(':')
            mailSubject = mailSubject[index+1:-1]
            print("Ticker: ",mailSubject)
            ticker = str(mailSubject)

            api = tradeapi.REST(API_KEY,SECRET_KEY,BASE_URL)
            account = api.get_account()
            accstatus = account.status
            acccash = account.cash
            print("Alpaca Account Status: ",accstatus)
            print("Alpaca Account Cash: $",acccash)
            shortcapital = float(acccash) * 0.8
            print("Commitment for Short: $",shortcapital)
            ucurrentprice = api.get_latest_trade(ticker)
            currentprice = float(ucurrentprice.p)
            print("Current Price: $",currentprice)
            uquantity = shortcapital / currentprice
            quantity = str(round(uquantity))
            print("Quantity :",quantity)
            
            order = api.submit_order(
                symbol= ticker,
                qty=quantity,
                side='sell',
                type='market',
                time_in_force='gtc',
                )
            print(order)
             
        
        else :
            print('Aborted')
            return None
            
    else :
        print('Aborted')
        return None
