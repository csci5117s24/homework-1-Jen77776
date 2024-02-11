from flask import Flask, render_template, request, redirect, url_for,jsonify
import os
import psycopg2
from dotenv import load_dotenv



#psql "sslmode=require host=dpg-cmvv3hacn0vc73ar98g0-a.oregon-postgres.render.com port=5432 dbname=database_ovi5 user=database_ovi5_user"
#password:Tuz1Y0VJ9SmoewUHphoh8vtPWM396PY4
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


# 定义一个函数来建立数据库连接
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# 定义创建表格的函数
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses1 (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL CHECK (length(name) >= 3),
            age TEXT,
            country TEXT,
            subscribe BOOLEAN,
            comments TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # 这里处理表单提交
        name = request.form.get('name')
        age = request.form.get('age')
        country = request.form.get('country')
        subscribe = 'subscribe' in request.form
        comments = request.form.get('comments', '')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO survey_responses1 (name, age, country, subscribe, comments) VALUES (%s, %s, %s, %s, %s)",(name, age, country, subscribe, comments))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/thanks')
    return render_template('survey.html')


@app.route('/decline')
def decline():
    return render_template('decline.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/api/results')
def api_results():
    reverse = request.args.get('reverse', 'false') == 'true'
    conn = get_db_connection()
    cur = conn.cursor()
    if reverse:
        cur.execute('SELECT * FROM survey_responses1 ORDER BY id DESC')
    else:
        cur.execute('SELECT * FROM survey_responses1 ORDER BY id ASC')
    responses = cur.fetchall()
    cur.close()
    conn.close()
    # 将查询结果转换为JSON格式
    data = [dict(zip([key[0] for key in cur.description], row)) for row in responses]
    return jsonify(data)

@app.route('/admin/summary')
def admin_summary():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 提取文本回答
    cur.execute('SELECT id, name, comments FROM survey_responses1')
    text_answers = cur.fetchall()
    
    # 提取选择/复选框问题的汇总数据
    cur.execute('SELECT age, COUNT(*) FROM survey_responses1 GROUP BY age')
    age_data = cur.fetchall()

    cur.execute('SELECT country, COUNT(*) FROM survey_responses1 GROUP BY country')
    country_data = cur.fetchall()

    cur.execute('SELECT subscribe, COUNT(*) FROM survey_responses1 GROUP BY subscribe')
    subscribe_data = cur.fetchall()
    
    # 提取每日调查响应数量的时间序列数据
    cur.execute('SELECT DATE(timestamp) as survey_date, COUNT(*) FROM survey_responses1 GROUP BY survey_date ORDER BY survey_date')
    time_series_data = cur.fetchall()
    
    cur.close()
    conn.close()

    # 将查询结果转换为适合Chart.js的格式
    age_labels = [row[0] for row in age_data]
    age_counts = [row[1] for row in age_data]

    country_labels = [row[0] for row in country_data]
    country_counts = [row[1] for row in country_data]

    subscribe_labels = ['Subscribed' if row[0] else 'Not Subscribed' for row in subscribe_data]
    subscribe_counts = [row[1] for row in subscribe_data]

    time_series_labels = [row[0].isoformat() for row in time_series_data]
    time_series_counts = [row[1] for row in time_series_data]

    # 准备传递给模板的数据
    #text_answers = [dict(row) for row in cur.fetchall()]
    data = {
        'text_answers': text_answers,
        'age_labels': age_labels,
        'age_counts': age_counts,
        'country_labels': country_labels,
        'country_counts': country_counts,
        'subscribe_labels': subscribe_labels,
        'subscribe_counts': subscribe_counts,
        'time_series_labels': time_series_labels,
        'time_series_counts': time_series_counts,
    }
    #print(text_answers)  # 在将数据发送到模板之前打印


    return render_template('admin_summary.html', data=data)

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'development':
        create_table()  # 创建表
    app.run(debug=True)
