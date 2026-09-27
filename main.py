import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import google.generativeai as genai

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Lấy Token từ Environment Variables (Cấu hình trên Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Cấu hình Gemini AI với Prompt Định hình Kiến thức Ma Sói
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    SYSTEM_INSTRUCTION = """
    Bạn là một BẬC THẦY QUẢN TRÒ MA SÓI (Werewolf / Mafia Master) có kiến thức sâu rộng nhất về trò chơi Ma Sói.
    Nhiệm vụ của bạn:
    1. Am hiểu tường tận luật chơi Ma Sói cơ bản, Ma Sói Ultimate, Ma Sói Onenight, các biến thể Việt Nam và thế giới.
    2. Giải thích chi tiết, chính xác kĩ năng của mọi chức năng: Tiên Tri, Phù Thủy, Bảo Vệ, Thợ Săn, Sói Trùm, Sói Băng, Thần Tình Yêu, Già Làng, Thằng Hề, Bán Sói, Kẻ Chết Chóc...
    3. Hướng dẫn chiến thuật chơi Ma Sói cho từng phe (Phe Dân, Phe Sói, Phe Thứ 3).
    4. Giọng văn kịch tính, hấp dẫn, đậm chất không khí u tối của làng Ma Sói, vừa chuyên nghiệp vừa hài hước khi cần.
    5. Trả lời bằng Tiếng Việt ngắn gọn, rõ ràng, dễ hiểu.
    """
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
else:
    model = None

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🐺 **CHÀO MƯỜNG BẠN ĐẾN VỚI QUẢN TRÒ MA SÓI AI!** 🐺\n\n"
        "Tôi là Bậc Thầy Ma Sói - người nắm giữ kiến thức sâu rộng nhất về Làng Ma Sói!\n\n"
        "📌 **Các lệnh hỗ trợ:**\n"
        "• `/luat [tên_vai_trò]` : Hỏi luật chơi hoặc kĩ năng vai trò bất kỳ (VD: `/luat Phù thủy`)\n"
        "• `/chienthuat [phe/vai_tro]` : Gợi ý mẹo và chiến thuật chơi (VD: `/chienthuat Phe Sói`)\n"
        "• `/hoidap [câu_hỏi]` : Hỏi bất kỳ thắc mắc nào về Ma Sói!"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

# Lệnh hỏi luật chơi & chức năng
async def luat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập tên vai trò hoặc luật cần hỏi. Ví dụ: `/luat Phù Thủy`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    prompt = f"Hãy giải thích chi tiết luật chơi, kĩ năng và lưu ý của vai trò/chủ đề Ma Sói này: '{query}'"
    
    if model:
        try:
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi khi tra cứu AI: {e}")
    else:
        await update.message.reply_text("⚠️ Chưa cấu hình GEMINI_API_KEY nên chưa dùng được tính năng AI!")

# Lệnh hỏi chiến thuật
async def chienthuat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập phe/vai trò bạn muốn xin chiến thuật. Ví dụ: `/chienthuat Tiên Tri`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    prompt = f"Phân tích chiến thuật chơi đỉnh cao, cách bluff và mẹo sống sót/chiến thắng cho: '{query}' trong game Ma Sói."
    
    if model:
        try:
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi khi tra cứu AI: {e}")
    else:
        await update.message.reply_text("⚠️ Chưa cấu hình GEMINI_API_KEY!")

# Lệnh hỏi đáp chung về Ma Sói
async def hoidap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập câu hỏi. Ví dụ: `/hoidap Phù thủy có thể tự cứu mình không?`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    if model:
        try:
            response = model.generate_content(query)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi khi xử lý câu hỏi: {e}")
    else:
        await update.message.reply_text("⚠️ Chưa cấu hình GEMINI_API_KEY!")

def main():
    if not TELEGRAM_TOKEN:
        print("Lỗi: Thiếu TELEGRAM_TOKEN!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("luat", luat))
    app.add_handler(CommandHandler("chienthuat", chienthuat))
    app.add_handler(CommandHandler("hoidap", hoidap))

    print("🤖 Bot Ma Sói AI Am Hiểu Nhất đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
