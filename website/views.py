from flask import Blueprint, render_template, request, flash, jsonify,redirect,url_for
from flask_login import login_required, current_user
from .models import Chatbot
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def chatbots():
    if request.method == 'POST':
        # Handle form submission for chatbot creation
        bot_name = request.form.get('bot_name')
        bot_url = request.form.get('bot_url')

        # Validation logic
        if not bot_name or not bot_url:
            flash('Both fields are required!', 'error')
            return redirect(url_for('chatbots'))

        # Generate and save chatbot script
        # chatbot_script = generate_chatbot_script(bot_name, bot_url, current_user.id)
        chatbot_script = "<script>chatbotscript<script>"  
        # Save chatbot details to database
        new_bot = Chatbot(user_id=current_user.id, name=bot_name, url=bot_url, script=chatbot_script)
        db.session.add(new_bot)
        db.session.commit()

        flash('Chatbot created successfully!', 'success')
        return redirect(url_for('chatbots'))

    # Fetch user's existing chatbots
    user_bots = Chatbot.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', chatbots=user_bots)


