"""
Admin panel handler for bot management and broadcasting.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import ChatHistoryDB
from database.user_preferences import UserPreferencesDB
from utils.keyboards import KeyboardBuilder
from utils.states import UserStates
from config import Config
import asyncio

router = Router()

# Initialize services
db = ChatHistoryDB()
prefs_db = UserPreferencesDB()

# Admin user IDs (configure in .env)
ADMIN_IDS = [int(x) for x in Config.ADMIN_IDS.split(',')] if hasattr(Config, 'ADMIN_IDS') and Config.ADMIN_IDS else []


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in ADMIN_IDS or user_id == Config.OWNER_ID if hasattr(Config, 'OWNER_ID') else False


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel command."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bu komanda faqat adminlar uchun!")
        return
    
    await message.answer(
        "👨‍💼 <b>Admin Panel</b>\n\n"
        "Bot boshqaruvi va monitoring",
        reply_markup=KeyboardBuilder.admin_menu()
    )


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Show users list."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    
    stats = prefs_db.get_global_stats()
    user_ids = prefs_db.get_all_user_ids()
    
    text = f"""👥 <b>Foydalanuvchilar</b>

📊 Statistika:
• Jami foydalanuvchilar: {stats['total_users']}
• Jami xabarlar: {stats['total_messages']}
• Rasmlar: {stats['total_images']}
• Hujjatlar: {stats['total_documents']}
• Ovozli xabarlar: {stats['total_voice']}

👤 Faol foydalanuvchilar:
{len(user_ids)} ta"""
    
    await callback.message.edit_text(text, reply_markup=KeyboardBuilder.admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Start broadcast message."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>Broadcast Xabar</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n"
        "(Bekor qilish uchun /cancel yuboring)"
    )
    await state.set_state(UserStates.admin_waiting_broadcast_message)
    await callback.answer()


@router.message(UserStates.admin_waiting_broadcast_message)
async def admin_broadcast_send(message: Message, state: FSMContext):
    """Send broadcast message to all users."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Ruxsat yo'q!")
        await state.clear()
        return
    
    if message.text == "/cancel":
        await message.answer("❌ Broadcast bekor qilindi")
        await state.clear()
        return
    
    broadcast_text = message.text
    user_ids = prefs_db.get_all_user_ids()
    
    progress_msg = await message.answer(
        f"📤 Yuborilmoqda...\n"
        f"0 / {len(user_ids)} foydalanuvchi"
    )
    
    success_count = 0
    failed_count = 0
    
    for idx, user_id in enumerate(user_ids, 1):
        try:
            await message.bot.send_message(user_id, f"📢 <b>Admin Xabari:</b>\n\n{broadcast_text}")
            success_count += 1
            
            # Update progress every 10 users
            if idx % 10 == 0:
                await progress_msg.edit_text(
                    f"📤 Yuborilmoqda...\n"
                    f"{idx} / {len(user_ids)} foydalanuvchi\n"
                    f"✅ Yuborildi: {success_count}\n"
                    f"❌ Xato: {failed_count}"
                )
            
            await asyncio.sleep(0.05)  # Rate limiting
            
        except Exception as e:
            failed_count += 1
            print(f"Broadcast error for user {user_id}: {e}")
    
    await progress_msg.edit_text(
        f"✅ <b>Broadcast Yakunlandi!</b>\n\n"
        f"📊 Natijalar:\n"
        f"• Jami: {len(user_ids)}\n"
        f"• Yuborildi: {success_count}\n"
        f"• Xato: {failed_count}"
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Show detailed statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    
    stats = prefs_db.get_global_stats()
    total_history = db.get_message_count()
    
    text = f"""📊 <b>Bot Statistikasi</b>

👥 Foydalanuvchilar:
• Jami: {stats['total_users']} ta

💬 Xabarlar:
• Jami: {stats['total_messages']} ta
• Suhbat tarixi: {total_history} ta

🎨 Media:
• Rasmlar: {stats['total_images']} ta
• Hujjatlar: {stats['total_documents']} ta
• Ovozli: {stats['total_voice']} ta

📈 O'rtacha:
• Xabar/user: {stats['total_messages'] / max(stats['total_users'], 1):.1f} ta"""
    
    await callback.message.edit_text(text, reply_markup=KeyboardBuilder.admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_logs")
async def admin_logs(callback: CallbackQuery):
    """Show system logs."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    
    # Read last 20 lines from log file
    try:
        import subprocess
        result = subprocess.run(
            ['tail', '-n', '20', 'bot.log'],
            capture_output=True,
            text=True
        )
        logs = result.stdout or "Log fayli topilmadi"
    except:
        logs = "Loglarni o'qishda xatolik"
    
    text = f"🗂 <b>System Logs</b>\n\n<code>{logs[:4000]}</code>"
    
    await callback.message.edit_text(text, reply_markup=KeyboardBuilder.admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    """Admin settings."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    
    text = """⚙️ <b>Admin Sozlamalar</b>

Hozircha mavjud emas.
Kelajakda qo'shiladi:
• Bot sozlamalari
• Rate limiting
• Feature toggles"""
    
    await callback.message.edit_text(text, reply_markup=KeyboardBuilder.admin_menu())
    await callback.answer()
