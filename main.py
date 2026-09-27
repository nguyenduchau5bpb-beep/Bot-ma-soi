import logging
import os
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# 1. TẠO WEB SERVER FLASK ĐỂ MỞ CỔNG TRÊN RENDER
# ==========================================
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot Ma Soi AI is running and alive!"


def run_web():
  # Lấy cổng do Render cung cấp (mặc định là 10000)
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# ==========================================
# 2. CÁC TÍNH NĂNG VÀ HANDLER CỦA BOT MA SÓI AI
# ==========================================

# Lấy biến môi trường cho Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình Google Gemini AI
if GEMINI_API_KEY:
  genai.configure(api_key=GEMINI_API_KEY)
  gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
  logger.warning(
      "CẢNH BÁO: Chưa cấu hình GEMINI_API_KEY trong Environment Variables!"
  )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Lệnh /start"""
  user_name = update.effective_user.first_name
  welcome_message = (
      f"🐺 Chào mừng {user_name} đến với **Bot Ma Sói AI Am Hiểu Nhất**!\n\n"
      "Tôi ở đây để giúp bạn nắm vững luật chơi, chiến thuật đỉnh cao và giải"
      " đáp mọi thắc mắc về game Ma Sói.\n\n"
      "📜 **Các lệnh có sẵn:**\n"
      "• /luat - Hướng dẫn luật chơi Ma Sói cơ bản và nâng cao\n"
      "• /chienthuat - Chia sẻ chiến thuật, mẹo chơi ẩn thân, lật kèo\n"
      "• /hoidap - Hỏi đáp nhanh mọi thắc mắc về game\n\n"
      "💬 *Hoặc bạn có thể nhắn tin trực tiếp cho tôi bất cứ lúc nào để trò"
      " chuyện nhé!*"
  )
  await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def luat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Lệnh /luat"""
  luat_text = (
      "📜 **TÓM TẮT LUẬT CHƠI MA SÓI (WEREWOLF)**\n\n"
      "1. **Phe Dân Làng:** Tìm ra toàn bộ Ma Sói và treo cổ chúng trước khi quá"
      " muộn.\n"
      "2. **Phe Ma Sói:** Giấu mình ban ngày, ăn thịt Dân Làng vào ban đêm.\n"
      "3. **Phe Thứ Ba (Độc lập):** Có mục tiêu riêng (Kẻ Thổi Sáo, Cặp đôi tình"
      " nhân, Kẻ sát nhân...).\n\n"
      "⏱ **Vòng chơi:** Ban đêm (Chức năng dậy hành động) ➔ Ban ngày (Thảo"
      " luận & Treo cổ).\n"
      "💡 *Nhập câu hỏi chi tiết nếu bạn muốn tìm hiểu về chức năng của Tiên"
      " Tri, Thợ Săn, Bảo Vệ,...*"
  )
  await update.message.reply_text(luat_text, parse_mode="Markdown")


async def chienthuat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Lệnh /chienthuat"""
  chien_thuat_text = (
      "🎯 **CHIẾN THUẬT MA SÓI ĐỈNH CAO**\n\n"
      "• **Dân Làng:** Đừng nói quá nhiều gây nghi ngờ, hãy chú ý quan sát sự"
      " mâu thuẫn trong lời nói của người khác.\n"
      "• **Ma Sói:** Đừng 'bè phái' bảo vệ nhau lộ liễu ban ngày. Hãy biết 'bán"
      " đồng đội' đúng lúc để tạo lòng tin.\n"
      "• **Tiên Tri:** Cân nhắc thời điểm 'lật bài ngửa' (claim) hợp lý, tránh bị"
      " Sói cắn ngay đêm hôm sau.\n\n"
      "🧠 *Muốn bàn về chiến thuật cho phe nào cụ thể? Hãy nhắn cho tôi nhé!*"
  )
  await update.message.reply_text(chien_thuat_text, parse_mode="Markdown")


async def hoidap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Lệnh /hoidap"""
  await update.message.reply_text(
      "❓ Bạn muốn hỏi gì về game Ma Sói? Hãy gõ câu hỏi trực tiếp hoặc nhắn nội"
      " dung bạn thắc mắc, tôi sẽ giải đáp chi tiết cho bạn!"
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Nhận tin nhắn của người dùng và gọi Gemini AI trả lời"""
  user_message = update.message.text

  if not GEMINI_API_KEY:
    await update.message.reply_text(
        "Bot chưa được cấu hình API Key của AI. Vui lòng liên hệ Admin."
    )
    return

  # Gửi trạng thái đang soạn tin nhắn cho sinh động
  await context.bot.send_chat_action(
      chat_id=update.effective_chat.id, action="typing"
  )

  try:
    prompt_context = (
        "Bạn là một chuyên gia am hiểu sâu sắc về tựa game Board Game Ma Sói"
        " (Werewolf). Hãy trả lời câu hỏi của người chơi một cách thông minh,"
        " lôi cuốn, mang phong cách huyền bí, hỗ trợ chiến thuật đỉnh cao và"
        " giải đáp luật chơi chính xác bằng tiếng Việt.\n\n"
        f"Câu hỏi của người chơi: {user_message}"
    )

    response = gemini_model.generate_content(prompt_context)
    reply_text = response.text

    await update.message.reply_text(reply_text)

  except Exception as e:
    logger.error(f"Lỗi khi gọi Gemini API: {e}")
    await update.message.reply_text(
        "Đã xảy ra lỗi nhỏ khi kết nối với AI. Bạn thử nhắn lại sau ít phút"
        " nhé!"
    )


# ==========================================
# 3. HÀM KHỞI CHẠY BOT TELEGRAM
# ==========================================
def run_telegram_bot():
  TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

  if not TELEGRAM_TOKEN:
    logger.error("Lỗi: Thiếu TELEGRAM_TOKEN trong biến môi trường!")
    return

  # Khởi tạo Bot Telegram
  app_bot = Application.builder().token(TELEGRAM_TOKEN).build()

  # Đăng ký các lệnh
  app_bot.add_handler(CommandHandler("start", start))
  app_bot.add_handler(CommandHandler("luat", luat))
  app_bot.add_handler(CommandHandler("chienthuat", chienthuat))
  app_bot.add_handler(CommandHandler("hoidap", hoidap))

  # Đăng ký nhận tin nhắn văn bản thông thường để chat với AI
  app_bot.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  logger.info("🤖 Bot Ma Sói AI đang chạy (polling)...")
  app_bot.run_polling(drop_pending_updates=True)


# ==========================================
# 4. HÀM CHÍNH (MAIN) KHỞI CHẠY SONG SONG
# ==========================================
if __name__ == "__main__":
  # Khởi chạy Flask server ở một luồng riêng để mở cổng cho Render
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  # Khởi chạy Bot Telegram ở luồng chính
  run_telegram_bot()
