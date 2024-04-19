from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'very_secret_key'  # 设置一个强密钥

df = pd.read_csv('data/combined_ticker.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_ticker', methods=['GET'])
def search_ticker():
    query = request.args.get('q', '').upper()
    if query:
        matched = df[df['Symbol'].str.startswith(query)]['Symbol'].tolist()
        return jsonify(matched)
    return jsonify([])

@app.route('/search', methods=['POST'])
def search():
    ticker = request.form['ticker']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    info_type = request.form['info_type']

    if info_type == 'stock_price':
        query_result = perform_stock_price_query(ticker, start_date, end_date)
    elif info_type == 'financial_info':
        query_result = perform_financial_info_query(ticker, start_date, end_date)
    else:
        query_result = [{'symbol': ticker, 'data_field': 'No valid information type selected'}]

    session['query_result'] = json.dumps(query_result, default=str)
    session['ticker'] = ticker  # 保存ticker到session
    return redirect(url_for('show_results'))

def perform_stock_price_query(ticker, start_date, end_date):
    # 数据库连接和查询逻辑
    client = MongoClient('localhost', 27017)
    db = client['apan5400']
    collection = db['project']
    # 查询逻辑和错误处理
    pipeline = [
        {
            "$match": {
                "ticker": ticker,
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "date": 1,
                "adjclose": 1,
                "volume": 1,
                "high_low_diff": 1,
                "close_open_diff": 1
            }
        },
        {"$sort": {"date": 1}}
    ]
    try:
        return list(collection.aggregate(pipeline))
    except Exception as e:
        app.logger.error("Query failed: %s", e)
        return []

@app.route('/results')
def show_results():
    data = json.loads(session.get('query_result', '[]'))
    ticker = session.get('ticker', 'Unknown Ticker')  # 从session获取ticker
    return render_template('results.html', data=data, ticker=ticker)

if __name__ == '__main__':
    app.run(debug=True)

