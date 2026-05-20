"""
Lumberbud Telegram Bot - Railway Ready
Reads all sensitive config from environment variables.
"""

import logging
import asyncio
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Config from environment variables ─────────────────────────────────────
BOT_TOKEN     = os.environ.get("BOT_TOKEN",     "8651898978:AAF9DG6LgBy3jtn5v7okrs7L0SkvPGH7-rQ")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "7542646148")
MOMO_NAME     = os.environ.get("MOMO_NAME",     "Papa Poku Boakye Yiadom")
MOMO_NUMBER   = os.environ.get("MOMO_NUMBER",   "0544884827")
MOMO_NETWORK  = os.environ.get("MOMO_NETWORK",  "MTN")
PRICE         = int(os.environ.get("PRICE",     "150"))

# ── States ─────────────────────────────────────────────────────────────────
GET_QUANTITY, GET_NAME, GET_PHONE, GET_LOCATION, CONFIRM, AWAIT_PAY = range(6)
order_num = [2000]

def new_id():
    order_num[0] += 1
    return f"LMB-{order_num[0]}"

def order_summary(data, order_id):
    total = data["quantity"] * PRICE
    return (
        f"🌲 *Order #{order_id}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Packs:     *{data['quantity']}*\n"
        f"💰 Total:     *GH₵ {total:,}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name:      {data['name']}\n"
        f"📞 Phone:     {data['phone']}\n"
        f"📍 Location:  {data['location']}\n"
        f"🕐 Time:      {data['timestamp']}\n"
    )

def momo_text(total, order_id):
    return (
        f"💳 *Payment Instructions*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Send *GH₵ {total:,}* via Mobile Money:\n\n"
        f"📱 Network:   *{MOMO_NETWORK}*\n"
        f"📲 Number:    *{MOMO_NUMBER}*\n"
        f"👤 Name:      *{MOMO_NAME}*\n\n"
        f"📝 Reference: *{order_id}*\n"
        f"_Use the order ID as your reference_\n\n"
        f"Once paid, tap ✅ below and we'll confirm your delivery."
    )

# ── Handlers ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = [
        [InlineKeyboardButton("🛒  Place an Order",  callback_data="order")],
        [InlineKeyboardButton("ℹ️  About Lumberbud",  callback_data="about")],
        [InlineKeyboardButton("📞  Contact Us",        callback_data="contact")],
    ]
    await update.message.reply_text(
        "👋 *Welcome to Lumberbud!*\n\n"
        "Premium quality, delivered to your door.\n"
        "Fast. Discreet. Reliable.\n\n"
        "What would you like to do today?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return GET_QUANTITY

async def menu_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "about":
        kb = [[InlineKeyboardButton("🛒 Order Now", callback_data="go_order")]]
        await q.edit_message_text(
            f"🌲 *About Lumberbud*\n\n"
            f"Top-grade product in 1g packs.\n\n"
            f"✅ Premium quality\n"
            f"✅ Fast delivery\n"
            f"✅ Discreet packaging\n"
            f"✅ Friendly service\n\n"
            f"*Price: GH₵ {PRICE} per pack*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return GET_QUANTITY
    elif q.data == "contact":
        kb = [[InlineKeyboardButton("🛒 Order Now", callback_data="go_order")]]
        await q.edit_message_text(
            "📞 *Contact Lumberbud*\n\n"
            "⏰ Available: Daily, 8am – 10pm\n\n"
            "Place your order below and we'll reach out! 🌲",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return GET_QUANTITY
    else:
        await q.edit_message_text(
            f"🛒 *Place Your Order*\n\n"
            f"Each pack is *GH₵ {PRICE}*.\n\n"
            f"How many packs would you like?\n"
            f"_(Type a number, e.g. 3)_",
            parse_mode="Markdown"
        )
        return GET_QUANTITY

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text(
            "⚠️ Please enter a valid number of packs.\n_(e.g. type *3* for 3 packs)_",
            parse_mode="Markdown"
        )
        return GET_QUANTITY
    qty = int(text)
    if qty > 50:
        await update.message.reply_text(
            "⚠️ Maximum order is 50 packs.\nFor bulk orders contact us directly.\n\nHow many packs? _(1–50)_",
            parse_mode="Markdown"
        )
        return GET_QUANTITY
    context.user_data["quantity"] = qty
    total = qty * PRICE
    await update.message.reply_text(
        f"✅ *{qty} pack{'s' if qty > 1 else ''}* — *GH₵ {total:,}*\n\n"
        f"Now I need a few details for delivery.\n\n"
        f"👤 What is your *full name*?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Please enter your full name.")
        return GET_NAME
    context.user_data["name"] = name
    await update.message.reply_text(
        f"👋 Nice to meet you, *{name}*!\n\n"
        f"📞 What is your *phone number*?\n"
        f"_So we can reach you when we arrive_",
        parse_mode="Markdown"
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+233"):
        phone = "0" + phone[4:]
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text(
            "⚠️ Please enter a valid Ghana phone number.\n_(e.g. 0244 123 456)_",
            parse_mode="Markdown"
        )
        return GET_PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text(
        "📍 What is your *delivery location / address*?\n\n"
        "_Be as specific as possible so we can find you._\n"
        "_(e.g. Tema, Community 5, opposite the clinic, white gate)_",
        parse_mode="Markdown"
    )
    return GET_LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text.strip()
    if len(location) < 5:
        await update.message.reply_text(
            "Please give a more detailed location so we can find you. 📍"
        )
        return GET_LOCATION
    context.user_data["location"]  = location
    context.user_data["timestamp"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
    context.user_data["order_id"]  = new_id()
    qty   = context.user_data["quantity"]
    total = qty * PRICE
    oid   = context.user_data["order_id"]
    summary = order_summary(context.user_data, oid)
    kb = [[
        InlineKeyboardButton("✅ Confirm Order", callback_data="confirm"),
        InlineKeyboardButton("✏️ Edit Order",    callback_data="edit"),
    ]]
    await update.message.reply_text(
        f"📋 *Please review your order:*\n\n{summary}\n💰 *Total: GH₵ {total:,}*\n\nIs everything correct?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return CONFIRM

async def confirm_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "edit":
        context.user_data.clear()
        await q.edit_message_text(
            f"No problem! Let's start over.\n\nHow many packs? _(GH₵ {PRICE} each)_",
            parse_mode="Markdown"
        )
        return GET_QUANTITY
    oid   = context.user_data["order_id"]
    total = context.user_data["quantity"] * PRICE
    kb = [[
        InlineKeyboardButton("✅ I've Sent Payment", callback_data="paid"),
        InlineKeyboardButton("❓ I Need Help",        callback_data="help"),
    ]]
    await q.edit_message_text(
        f"🎉 *Order #{oid} confirmed!*\n\n{momo_text(total, oid)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    d = context.user_data
    try:
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=(
                f"🔔 *NEW ORDER — Lumberbud*\n\n"
                f"Order:    *#{oid}*\n"
                f"Packs:    *{d['quantity']}*\n"
                f"Total:    *GH₵ {total:,}*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Name:     {d['name']}\n"
                f"Phone:    {d['phone']}\n"
                f"Location: {d['location']}\n"
                f"Time:     {d['timestamp']}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Owner notify error: {e}")
    return AWAIT_PAY

async def pay_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    oid   = context.user_data.get("order_id", "N/A")
    name  = context.user_data.get("name", "Customer")
    phone = context.user_data.get("phone", "N/A")
    total = context.user_data.get("quantity", 0) * PRICE
    if q.data == "paid":
        await q.edit_message_text(
            f"🙏 *Thank you, {name}!*\n\n"
            f"Payment notification received for *Order #{oid}*.\n\n"
            f"We'll verify and call you on {phone} shortly. 📞\n\n"
            f"Thank you for choosing *Lumberbud* 🌲",
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=(
                    f"💸 *PAYMENT CLAIMED*\n\n"
                    f"Order:  *#{oid}*\n"
                    f"Name:   {name}\n"
                    f"Phone:  {phone}\n"
                    f"Amount: GH₵ {total:,}\n\n"
                    f"⚠️ Check your {MOMO_NETWORK} MoMo and confirm."
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Pay notify error: {e}")
    elif q.data == "help":
        await q.edit_message_text(
            f"📞 *Need help with Order #{oid}?*\n\n"
            f"Contact us:\n📲 *{MOMO_NUMBER}* (WhatsApp / Call)\n\n"
            f"We're here to help. 🌲",
            parse_mode="Markdown"
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Order cancelled. Type /start to begin again. 🌲")
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type /start to place an order. 🌲")

# ── Main ───────────────────────────────────────────────────────────────────
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(menu_btn, pattern="^(order|about|contact|go_order)$"),
        ],
        states={
            GET_QUANTITY: [
                CallbackQueryHandler(menu_btn, pattern="^(order|about|contact|go_order)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity),
            ],
            GET_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            CONFIRM:      [CallbackQueryHandler(confirm_btn, pattern="^(confirm|edit)$")],
            AWAIT_PAY:    [CallbackQueryHandler(pay_btn, pattern="^(paid|help)$")],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start",  start),
        ],
        allow_reentry=True,
        per_message=False,
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    logger.info("Lumberbud bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
