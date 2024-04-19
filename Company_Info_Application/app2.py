from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import pandas as pd
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 加载股票代码数据
df = pd.read_csv('data/combined_ticker copy.csv')

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
    info_type = request.form['info_type']
    session['ticker'] = ticker
    session['info_type'] = info_type
    return redirect(url_for('display_options'))

@app.route('/display_options')
def display_options():
    info_type = session.get('info_type', 'company_overview')
    dict_file = {
        'company_overview': 'data/company_overview_dict.csv',
        'financial_statements': 'data/annual_financial_dict.csv',
        'key_ratios': 'data/key_ratios_dict.csv'
    }.get(info_type, 'data/company_overview_dict.csv')
    data = pd.read_csv(dict_file)
    options = data.iloc[:, 1].dropna().tolist()
    return render_template('display_options.html', options=options, info_type=info_type)

@app.route('/results', methods=['POST'])
def results():
    ticker = session['ticker']
    info_type = session['info_type']
    selected_options = request.form.getlist('selected_options')
    data = []
    fiscal_year = request.form.get('fiscalYear')
    start_month = request.form.get('startMonth', None)  # 默认为 None，除非 'key_ratios' 提供了月份
    end_month = request.form.get('endMonth', None)      # 默认为 None，除非 'key_ratios' 提供了月份

    if info_type == 'company_overview':
        data = perform_query_company_overview(ticker, selected_options)
    elif info_type == 'financial_statements':
        data = perform_query_financial_statements(ticker, selected_options, fiscal_year)
    elif info_type == 'key_ratios':
        data = perform_query_key_ratios(ticker, selected_options, fiscal_year, start_month, end_month)
    
    return render_template('results.html', 
                           ticker=ticker, 
                           info_type=info_type, 
                           data=data, 
                           variables=selected_options,
                           fiscal_year=fiscal_year,
                           start_month=start_month,
                           end_month=end_month)


# 针对 company_overview 的查询
def perform_query_company_overview(ticker, variables):
    return query_database(ticker, variables, 'company_info', 'company_overview')

# 针对 financial_statements 的查询
def perform_query_financial_statements(ticker, variables, fiscal_year):
    return query_database(ticker, variables, 'financials', 'financial_statements', extra_conditions="fyear = %s", extra_params=[fiscal_year])

# 针对 key_ratios 的查询
def perform_query_key_ratios(ticker, variables, fiscal_year, start_month, end_month):
    return query_database(ticker, variables, 'financial_ratios', 'key_ratios', extra_conditions="year = %s AND month BETWEEN %s AND %s", extra_params=[fiscal_year, start_month, end_month])


def load_variable_mapping(info_type):
    # 根据 info_type 确定映射文件路径
    dict_file = {
        'company_overview': 'data/company_overview_dict.csv',
        'financial_statements': 'data/annual_financial_dict.csv',
        'key_ratios': 'data/key_ratios_dict.csv'
    }.get(info_type, 'data/company_overview_dict.csv')

    # 加载映射字典
    mapping_df = pd.read_csv(dict_file)
    return dict(zip(mapping_df.iloc[:, 1], mapping_df.iloc[:, 0]))

def query_database(ticker, variables, table, info_type, extra_conditions=None, extra_params=[]):
    # 加载映射字典
    variable_mapping = load_variable_mapping(info_type)

    # 将用户界面变量映射到数据库列名
    db_columns = [variable_mapping.get(var, var) for var in variables]

    # 数据库连接参数
    params = {"host": "localhost", "port": '5432', "dbname": "project", "user": "postgres", "password": "123"}
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # 动态构建 SQL 字段名
    sql_fields = sql.SQL(', ').join(map(sql.Identifier, db_columns))
    sql_table = sql.Identifier(table)

    # 构建基础查询
    query = sql.SQL("SELECT {fields} FROM {table} WHERE ticker = %s").format(
        fields=sql_fields,
        table=sql_table
    )

    # 添加额外条件
    if extra_conditions:
        query = sql.SQL("{} AND {}").format(query, sql.SQL(extra_conditions))

    # 执行查询
    try:
        cur.execute(query, [ticker] + extra_params)
        rows = cur.fetchall()
        return [{var: val for var, val in zip(variables, row)} for row in rows]
    finally:
        cur.close()
        conn.close()

from datetime import datetime

def month_name_filter(month_number):
    # 将数字月份转换为月份名
    if month_number:
        month_number = int(month_number)
        return datetime(1900, month_number, 1).strftime('%B')
    return "No month provided"

app.jinja_env.filters['month_name'] = month_name_filter



if __name__ == '__main__':
    app.run(debug=True)
