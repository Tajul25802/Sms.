import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# API Keys (Replace with yours)
NUMVERIFY_API = "YOUR_NUMVERIFY_API"
HIBP_API = "YOUR_HAVEIBEENPWNED_API"

# Start Command
def start(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton("📱 Phone Lookup", callback_data="phone")],
        [InlineKeyboardButton("📧 Email Check", callback_data="email")],
        [InlineKeyboardButton("👤 Username Search", callback_data="username")],
        [InlineKeyboardButton("🌐 IP Lookup", callback_data="ip")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(
        "🔍 *OSINT Bot - Choose an option:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Phone Lookup (Using NumVerify API)
def phone_lookup(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text("📱 *Enter a phone number (with country code):*", parse_mode="Markdown")
    
    # Store next step handler
    context.user_data['next_step'] = 'process_phone'

def process_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API}&number={phone}"
    response = requests.get(url).json()
    
    if response.get("valid"):
        info = f"""
📱 *Phone Lookup Results:*
- **Number:** `{response['number']}`
- **Country:** {response['country_name']} ({response['country_code']})
- **Carrier:** {response['carrier']}
- **Line Type:** {response['line_type']}
        """
        update.message.reply_text(info, parse_mode="Markdown")
    else:
        update.message.reply_text("❌ Invalid phone number or API error.")

# Email Breach Check (HaveIBeenPwned)
def email_check(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text("📧 *Enter an email to check for breaches:*", parse_mode="Markdown")
    context.user_data['next_step'] = 'process_email'

def process_email(update: Update, context: CallbackContext):
    email = update.message.text
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"hibp-api-key": HIBP_API}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        breaches = response.json()
        breach_list = "\n".join([f"- {b['Name']} ({b['BreachDate']})" for b in breaches])
        update.message.reply_text(f"🔓 *Breaches found for {email}:*\n{breach_list}", parse_mode="Markdown")
    else:
        update.message.reply_text("✅ No breaches found for this email.")

# Main Bot Setup
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(phone_lookup, pattern="^phone$"))
    dp.add_handler(CallbackQueryHandler(email_check, pattern="^email$"))
    
    # Message Handlers (For phone/email input)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
