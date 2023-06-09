from flask import Flask, session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request
from sqlalchemy import text
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Connection credentials
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "1a8a8a7415157aaaBbb"
DATABASE = "flask"

# configuring our database uri

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

db = SQLAlchemy(app)

# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))

def generate_number():
   choices = ["3", "4", "5"]
   probabilities = [0.95, 0.036, 0.014]
   return random.choices(choices, probabilities)[0]


def takeSecond(elem):
   return elem[1]

@app.route('/gacha', methods=['GET', 'POST'])
def gacha():
   if request.method == 'GET':
      print("get gacha")
      return render_template("gacha.html")
   else:
      data = request.get_json()  # 获取前端发送的JSON数据
      received_string = data['data']  # 获取字符串数据
      return_string = ""
      username = session.get('username')
      print("后端gacha收到：" + received_string)
      print("username:"+session.get('username'))
      # 这里根据当前用户的username，去用户表查询其user_id，然后再去卡池执行抽卡逻辑，拼接获得新的记录，最后插入gacha_result中
      # 同时，这里需要把插入的card_name全部记录，以便于输出和显示
      with app.app_context():
          with db.engine.connect() as conn:
              stmt = text("SELECT user_id AS result FROM user WHERE user_name = :username")
              rs = conn.execute(stmt, {"username": username})
              userid= rs.fetchone()[0] # 这里获取到了当前用户的id
              for i in range(0,10):
                  gacha_result_once = generate_number()
                  if gacha_result_once == "3":
                     stmt = text("SELECT * FROM gacha_list WHERE card_status = 3 ORDER BY RAND() LIMIT 1;")
                     rs = conn.execute(stmt, {"username": username})
                     row = rs.fetchone()
                     cardid = row[0]  # 获取第一列 card_id
                     cardname = row[1]  # 获取第二列 card_name
                     print(cardid)
                     print(cardname)
                     return_string = return_string + cardname + " "
                  elif gacha_result_once == "4":
                     stmt = text("SELECT * FROM gacha_list WHERE card_status = 4 ORDER BY RAND() LIMIT 1;")
                     rs = conn.execute(stmt, {"username": username})
                     row = rs.fetchone()
                     cardid = row[0]  # 获取第一列 card_id
                     cardname = row[1]  # 获取第二列 card_name
                     print(cardid)
                     print(cardname)
                     return_string = return_string + cardname + " "
                  elif gacha_result_once == "5":
                     stmt = text("SELECT * FROM gacha_list WHERE card_status = 5 ORDER BY RAND() LIMIT 1;")
                     rs = conn.execute(stmt, {"username": username})
                     row = rs.fetchone()
                     cardid = row[0]  # 获取第一列 card_id
                     cardname = row[1]  # 获取第二列 card_name
                     print(cardid)
                     print(cardname)
                     return_string = return_string + cardname + " "
                  stmt = text("INSERT INTO gacha_history VALUES(:userid,:cardid,CURRENT_TIMESTAMP)")
                  rs = conn.execute(stmt, {"userid": userid, "cardid": cardid})
                  print("抽到了："+str(cardid))
              conn.commit()
              conn.closed
              print("userid："+str(userid))
      return session.get('username')+"上次十连的结果："+return_string

@app.route('/', methods=['GET', 'POST'])
def index():
   print("????")
   if request.method == 'GET':
      return render_template("index.html",data="default")
   else:
      print("<<<")
      login_result = 0 # 0->没有用户，进行注册, 1->有用户，登录成功, 2->有用户，登录失败
      login_result = login_request()
      print("<!<")
      if login_result == 0:
         msg = "新用户注册成功"
      elif login_result == 1:
         msg = "登录成功"
      else:
         msg = "登录失败，请检查密码重新输入"
      return render_template("index.html",data=msg)

def login_request():
   # 接收post请求的form表单参数
   username = request.form.get('username')
   userpass = request.form.get('password')
   print(str(username))
   print(str(userpass))
   with app.app_context():
      with db.engine.connect() as conn:
         stmt = text("SELECT IF(COUNT(*) > 0, 1, 0) AS result FROM user WHERE user_name = :username")
         rs = conn.execute(stmt, {"username": username})
         whether_registed = rs.fetchone()[0]
         conn.commit()
         conn.closed
   if whether_registed > 0: # 这是用户已经注册过的情况，数据库内存储了用户的信息（主要是用户名，用户注册也就看这个，然后用户id好像没啥用了）接下来一步应该是检验密码
      with app.app_context():
         with db.engine.connect() as conn:
            stmt = text("SELECT COUNT(*) AS count FROM user WHERE user_name = :username AND user_pass = :userpass;")
            rs = conn.execute(stmt, {"username": username,"userpass":userpass})
            pass_correct = rs.fetchone()[0]
            if pass_correct > 0: # 用户登录成功
               login_result = 1
               session['username'] = username
               session['userpass'] = userpass
               print("登录成功")
            else:
               login_result = 2
               print("输入密码错误，登录失败")
            conn.commit()
            conn.closed
   else: # 用户没有注册过的情况
      print("没注册过，帮他注册一个")
      login_result = 0
      print("账户名："+username+" "+"密码："+userpass)
      with app.app_context():
         with db.engine.connect() as conn:
            stmt = text("INSERT INTO user (user_name, user_pass) VALUES (:username, :userpass);")
            rs = conn.execute(stmt, {"username": username,"userpass":userpass})
            conn.commit()
            conn.closed
      session['username'] = username
      session['userpass'] = userpass
   return login_result

@app.route('/my_gacha_result', methods=['GET', 'POST'])
def my_gacha_result():
   # 这里首先把gacha_history里面所有属于userid的记录获取出来，然后用表格展示（数据全部传到前端）
   # 但是在这之前需要先把userid设置为session的全局变量()难蚌，感觉可以在前面登录和注册的功能那里加一个获取id的模块
   username = session.get('username')
   with app.app_context():
      with db.engine.connect() as conn:
         stmt = text("SELECT user_id FROM user WHERE user_name = :username;")
         rs = conn.execute(stmt, {"username": username})
         userid = rs.fetchone()[0]
         session['userid'] = userid # 此处获取了userid，去表格查询其所有的抽卡记录
         stmt = text("SELECT * FROM gacha_history WHERE user_id = :userid;")
         rs = conn.execute(stmt, {"userid": userid})
         history_list = rs.fetchall() # 此处获取一个list，其中每个元素都是一个元组，组成形式：(userid, cardid, obtain_time)，但是这个obtain_time比较特殊
         return_list = []
         # 接下来，通过对元组重新赋值，将list中每一个元组转化为(card_name, card_status, obtain_time),然后把list传给前端
         for record in history_list:
            cardid = record[1]
            obtain_time = record[2]
            stmt = text("SELECT card_name, card_status FROM gacha_list WHERE card_id =:cardid;")
            rs = conn.execute(stmt, {"cardid": cardid})
            card = rs.fetchone()
            cardname = card[0]
            cardstatus = card[1]
            return_list.append((cardname, cardstatus, obtain_time))
         stmt = text("SHOW FIELDS FROM gacha_history")
         rs = conn.execute(stmt)
         labels = rs.fetchall()
         labels = [l[0] for l in labels]
         # 这段代码获取表头，但是吧，应该可以在前端写一下，把表头单独展示，而不是在表格展示
         # 因为现在的滚动表格展示，只要一滚动，表头就看不见了，最好的方法其实是让表头固定，然后表格内容滑动
         # 有空再做
         conn.commit()
         conn.closed
   labels[0] = "灵基/礼装名称"
   labels[1] = "稀有度"
   labels[2] = "获取时间"
   return_list.sort(key=takeSecond,reverse=True)
   return render_template("my_gacha_result.html",labels=labels,content=return_list)

@app.route('/helpless1', methods=['GET', 'POST'])
def helpless1():
   if request.method == 'GET':
      gacha_times = 0
      userid = session['userid']
      user_five = 0
      user_four = 0
      user_three = 0
      user_total_score = 0
      with app.app_context():
         with db.engine.connect() as conn:
            stmt = text("SELECT COUNT(*) AS count FROM gacha_history WHERE user_id = :userid;")
            rs = conn.execute(stmt, {"userid": userid})
            gacha_times = rs.fetchone()[0]  # 获取该用户总的抽卡次数
            stmt = text("SELECT * FROM gacha_history WHERE user_id = :userid;")
            rs = conn.execute(stmt, {"userid": userid})
            user_gacha_history = rs.fetchall()  # 获取该用户所有的抽卡记录，做分析和展示
            for item in user_gacha_history:
               cardid = item[1]
               stmt = text("SELECT card_status FROM gacha_list WHERE card_id =:cardid;")
               rs = conn.execute(stmt, {"cardid": cardid})
               card = rs.fetchone()
               cardstatus = card[0]
               if cardstatus == 5:
                  user_five = user_five + 1
               elif cardstatus == 4:
                  user_four = user_four + 1
               elif cardstatus == 3:
                  user_three = user_three + 1
      user_total_score = user_three * 1 + user_four * 5 + user_five * 10
      user_average_score = gacha_times * 1 * 0.95 + gacha_times * 5 * 0.036 + gacha_times * 10 * 0.014
      user_average_score = int(user_average_score)
      if user_average_score < user_total_score:
         result = "欧"
      else:
         result = "非"
      conn.commit()
      conn.closed
      return render_template("helpless1.html", result=result, gacha_times=gacha_times, user_five=user_five,
                             user_four=user_four, user_three=user_three, user_average_score=user_average_score,
                             user_total_score=user_total_score)
   else: # 查询数据库，把该用户的所有抽卡记录删除
      userid = session['userid']
      with app.app_context():
         with db.engine.connect() as conn:
            stmt = text("DELETE FROM gacha_history WHERE user_id=:userid")
            rs = conn.execute(stmt, {"userid": userid})
            conn.commit()
            conn.closed
   return render_template("helpless1.html")

@app.route('/helpless2', methods=['GET', 'POST'])
def helpless2():
   return render_template("helpless2.html")

if __name__ == '__main__':
   app.run()
