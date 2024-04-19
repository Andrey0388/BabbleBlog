from flask import Flask, render_template, redirect, abort, request, jsonify
from sqlalchemy import create_engine

from app.data.db_session import create_session
from app.forms.news import NewsForm
from data import db_session
from data.users import User
from data.news import News, Like
from forms.user import RegisterForm
from forms.loginform import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_login import login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    order = request.args.get('order', 'newest')
    if order == 'newest':
        news = sorted(news, key=lambda x: x.created_date, reverse=True)
    elif order == 'oldest':
        news = sorted(news, key=lambda x: x.created_date)
    else:
        pass

    likes_order = request.args.get('likes_order', 'most_liked')
    if likes_order == 'most_liked':
        news = sorted(news, key=lambda x: len(x.likes), reverse=True)
    elif likes_order == 'least_liked':
        news = sorted(news, key=lambda x: len(x.likes))
    else:
        pass

    filterBy = request.args.get('filterBy', 'all')
    if filterBy == 'my_posts':
        news = list(filter(lambda x: x.user.name == current_user.name, news))
    elif filterBy == 'all':
        pass
    else:
        pass

    likes_count = {}
    for item in news:
        likes_count[item.id] = db_sess.query(Like).filter(Like.news_id == item.id).count()

    like_user_ids = {}
    for item in news:
        like_user_ids[item] = [like.user_id for like in item.likes]
    return render_template('index.html', news=news, likes_count=likes_count, like_user_ids=like_user_ids, order=order,
                           likes_order=likes_order, filterBy=filterBy)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким никнеймом уже существует")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.category = form.category.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.category.data = news.category
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.category = form.category.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/toggle_like', methods=['POST'])
@login_required
def toggle_like():
    data = request.json
    news_id = data.get('news_id')
    user_id = current_user.id

    if not news_id:
        return jsonify({'error': 'News ID is required'}), 400

    db_sess = db_session.create_session()
    news_item = db_sess.query(News).get(news_id)

    if not news_item:
        return jsonify({'error': 'News not found'}), 404

    if user_id in [like.user_id for like in news_item.likes]:
        # Удаляем лайк
        like_to_remove = next((like for like in news_item.likes if like.user_id == user_id), None)
        if like_to_remove:
            db_sess.delete(like_to_remove)
            db_sess.commit()
            return jsonify({'action': 'unliked'}), 200
    else:
        # Добавляем лайк
        like = Like(user_id=user_id, news_id=news_id)
        db_sess.add(like)
        db_sess.commit()
        return jsonify({'action': 'liked'}), 200

    return jsonify({'error': 'An error occurred'}), 500


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
