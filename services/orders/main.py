from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
config_paths = [
    Path(__file__).parent.parent.parent / 'config.env',
    Path(__file__).parent.parent / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

# --- Приложение FastAPI ---
app = FastAPI(
    title="Orders Service API",
    description="API для создания и управления заказами.",
    version="1.0.0"
)

# Настройка CORS
# Для production укажите конкретные домены через переменную окружения ALLOWED_ORIGINS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]
if "*" in allowed_origins and os.getenv("ENVIRONMENT", "development") == "production":
    print("WARNING: CORS настроен на allow_origins=['*'] в production! Это небезопасно!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class OrderRequest(BaseModel):
    product_ids: List[str]
    quantities: Dict[str, int] = None  # Опциональное поле для количества

class OrderResponse(BaseModel):
    order_id: str
    message: str
    created_at: str
    product_ids: List[str]
    quantities: Dict[str, int] = None
    total_items: int = 0

# Хранилище заказов (в реальном приложении это была бы база данных)
orders_storage = []

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8000")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")
RECOMMENDER_SERVICE_URL = os.getenv("RECOMMENDER_SERVICE_URL", "http://127.0.0.1:8012")

# Конфигурация Email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)
EMAIL_COPY_TO = os.getenv("EMAIL_COPY_TO", EMAIL_FROM)  # Адрес для дубликатов писем

# Логирование конфигурации при старте
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    print(f"✅ Telegram настроен: chat_id={TELEGRAM_CHAT_ID}")
else:
    print(f"⚠️  Telegram не настроен: TOKEN={'✅' if TELEGRAM_BOT_TOKEN else '❌'}, CHAT_ID={'✅' if TELEGRAM_CHAT_ID else '❌'}")

def send_telegram_message(message: str) -> bool:
    """
    Отправляет сообщение в Telegram.
    Возвращает True если сообщение отправлено успешно, False в противном случае.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram не настроен: отсутствует TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID", flush=True)
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print(f"✅ Сообщение отправлено в Telegram (chat_id: {TELEGRAM_CHAT_ID})", flush=True)
            return True
        else:
            print(f"❌ Ошибка Telegram API: {result.get('description', 'Unknown error')}", flush=True)
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке сообщения в Telegram: {e}", flush=True)
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка при отправке в Telegram: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False

def get_product_info(product_id: str) -> Optional[Dict]:
    """
    Получает информацию о товаре из catalog service.
    """
    try:
        url = f"{CATALOG_SERVICE_URL}/api/v1/products/{product_id}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            product_data = response.json()
            print(f"✅ Получена информация о товаре {product_id}: {product_data.get('name', 'N/A')}", flush=True)
            return product_data
        else:
            print(f"⚠️  Товар {product_id} не найден (HTTP {response.status_code})", flush=True)
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Не удалось подключиться к catalog service для товара {product_id}: {e}", flush=True)
        return None
    except Exception as e:
        print(f"⚠️  Ошибка при получении информации о товаре {product_id}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def get_user_info(authorization: Optional[str] = None, required: bool = False) -> Optional[Dict]:
    """
    Получает информацию о пользователе из auth service.
    Если required=True, выбрасывает исключение при отсутствии токена или невалидном токене.
    """
    if not authorization or not authorization.startswith("Bearer "):
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Для оформления заказа необходимо войти в систему. Пожалуйста, войдите или зарегистрируйтесь, чтобы продолжить.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        url = f"{AUTH_SERVICE_URL}/users/me"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ваша сессия истекла. Для оформления заказа необходимо войти в систему снова. Мы сохранили вашу корзину, просто войдите и попробуйте еще раз.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        if required:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при проверке авторизации: {str(e)}"
            )
        print(f"⚠️  Ошибка при получении информации о пользователе: {e}")
        return None

def generate_ai_praise(products_info: List[Dict]) -> str:
    """
    Генерирует мнение музыкального эксперта о выборе пластинок через recommender service.
    Для пользователя это позиционируется как мнение эксперта, но по сути остается восхвалением.
    """
    try:
        if not products_info:
            return ""
        
        # Формируем промпт для AI
        product_names = [p.get("name", "Неизвестная пластинка") for p in products_info]
        artists = [p.get("artist", "Неизвестный исполнитель") for p in products_info]
        
        prompt = f"""Пользователь только что оформил заказ на следующие виниловые пластинки:
{', '.join([f"{name} - {artist}" for name, artist in zip(product_names, artists)])}

Напиши короткое (2-3 предложения) профессиональное мнение музыкального эксперта о выборе пользователя, подчеркивая уникальность и ценность выбранных пластинок. Будь профессиональным, но вдохновляющим."""
        
        url = f"{RECOMMENDER_SERVICE_URL}/api/v1/recommendations/generate"
        payload = {"prompt": prompt}
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Извлекаем текст из ответа (разные форматы ответа)
            if isinstance(data, dict):
                # Формат с recommendations
                if "recommendations" in data and data["recommendations"]:
                    if isinstance(data["recommendations"], list) and len(data["recommendations"]) > 0:
                        rec = data["recommendations"][0]
                        if isinstance(rec, dict):
                            return rec.get("reason", rec.get("description", ""))
                        return str(rec)
                # Формат с response
                elif "response" in data:
                    return data["response"]
                # Формат с text
                elif "text" in data:
                    return data["text"]
                # Пробуем найти любой текстовый ключ
                for key in ["message", "content", "text", "recommendation"]:
                    if key in data and data[key]:
                        return str(data[key])
            # Если это строка напрямую
            elif isinstance(data, str):
                return data
            # Пробуем преобразовать в строку
            return str(data)
        else:
            print(f"⚠️  Recommender вернул статус {response.status_code}", flush=True)
        return ""
    except Exception as e:
        print(f"⚠️  Ошибка при генерации мнения эксперта: {e}", flush=True)
        return ""

def generate_recommendations(products_info: List[Dict]) -> List[Dict]:
    """
    Генерирует рекомендации на основе покупки через recommender service.
    """
    try:
        if not products_info:
            return []
        
        # Формируем список купленных пластинок для запроса рекомендаций
        product_names = [p.get("name", "") for p in products_info]
        artists = [p.get("artist", "") for p in products_info]
        product_ids = []
        for p in products_info:
            product_id = p.get("id")
            if product_id:
                try:
                    # Пробуем преобразовать в int, если это строка с числом
                    product_ids.append(int(product_id))
                except (ValueError, TypeError):
                    pass
        
        # Формируем запрос для рекомендаций
        purchase_description = ', '.join([f"{name} - {artist}" for name, artist in zip(product_names, artists) if name])
        
        # Используем более стабильную модель (gpt-4o-mini работает лучше)
        request_data = {
            "user_preferences": f"Только что купил: {purchase_description}",
            "current_books": product_ids if product_ids else purchase_description,  # Список ID или строка с описанием
            "max_recommendations": 3,
            "model": "gpt-4o-mini"  # Используем более стабильную модель
        }
        
        url = f"{RECOMMENDER_SERVICE_URL}/api/v1/recommendations/generate"
        print(f"📡 Отправка запроса на {url}...", flush=True)
        print(f"📤 Данные запроса: {request_data}", flush=True)
        
        try:
            response = requests.post(url, json=request_data, timeout=30)
            print(f"📥 Получен ответ со статусом {response.status_code}", flush=True)
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Не удалось подключиться к recommender service: {e}", flush=True)
            return []
        except requests.exceptions.Timeout as e:
            print(f"⏱️  Таймаут при запросе к recommender service: {e}", flush=True)
            return []
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📥 Получен ответ от recommender service: {type(data)}", flush=True)
                
                # Извлекаем рекомендации из разных возможных форматов ответа
                recommendations = []
                
                if isinstance(data, dict):
                    # Формат RecommendationResponse с полем recommendations
                    if "recommendations" in data and isinstance(data["recommendations"], list):
                        recommendations = data["recommendations"]
                        print(f"✅ Найдено {len(recommendations)} рекомендаций в поле 'recommendations'", flush=True)
                    # Если это список напрямую
                    elif isinstance(data, list):
                        recommendations = data
                        print(f"✅ Найдено {len(recommendations)} рекомендаций (список)", flush=True)
                elif isinstance(data, list):
                    recommendations = data
                    print(f"✅ Найдено {len(recommendations)} рекомендаций (прямой список)", flush=True)
                
                # Нормализуем формат рекомендаций
                normalized_recommendations = []
                for rec in recommendations:
                    if isinstance(rec, dict):
                        normalized_rec = {
                            "id": rec.get("id"),
                            "name": rec.get("name", rec.get("title", "Неизвестная пластинка")),
                            "artist": rec.get("artist", rec.get("author", "Неизвестный исполнитель")),
                            "reason": rec.get("reason", rec.get("description", rec.get("match_score", ""))),
                            "match_score": rec.get("match_score", 0.7)
                        }
                        normalized_recommendations.append(normalized_rec)
                
                print(f"✅ Обработано {len(normalized_recommendations)} рекомендаций для email", flush=True)
                return normalized_recommendations
            except Exception as e:
                print(f"⚠️  Ошибка при обработке ответа от recommender: {e}", flush=True)
                import traceback
                traceback.print_exc()
                return []
        else:
            print(f"⚠️  Recommender вернул статус {response.status_code}: {response.text}", flush=True)
            # Пробуем fallback - использовать простой промпт
            try:
                print(f"🔄 Пробуем fallback с простым промптом...", flush=True)
                fallback_request = {
                    "prompt": f"Пользователь только что купил: {purchase_description}. Подбери 3 похожие виниловые пластинки с объяснением почему они подходят."
                }
                fallback_response = requests.post(url, json=fallback_request, timeout=30)
                if fallback_response.status_code == 200:
                    fallback_data = fallback_response.json()
                    if isinstance(fallback_data, dict) and "recommendations" in fallback_data:
                        recommendations = fallback_data["recommendations"]
                        print(f"✅ Fallback успешен: {len(recommendations)} рекомендаций", flush=True)
                        return recommendations
            except Exception as e:
                print(f"⚠️  Fallback тоже не сработал: {e}", flush=True)
        return []
    except Exception as e:
        print(f"⚠️  Ошибка при генерации рекомендаций: {e}", flush=True)
        return []

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Отправляет email пользователю.
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"⚠️  Email не настроен: отсутствует SMTP_USERNAME или SMTP_PASSWORD", flush=True)
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()
        
        print(f"✅ Email отправлен на {to_email}", flush=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка при отправке email на {to_email}: {e}", flush=True)
        return False

def format_order_message(order_data: Dict, products_info: List[Dict], user_info: Optional[Dict] = None) -> str:
    """
    Форматирует сообщение о заказе для отправки в Telegram.
    """
    order_id = order_data.get("order_id", "N/A")
    created_at = order_data.get("created_at", "N/A")
    total_items = order_data.get("total_items", 0)
    quantities = order_data.get("quantities", {})
    
    # Форматируем дату
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%d.%m.%Y %H:%M:%S")
    except:
        formatted_date = created_at
    
    message = f"🛒 <b>Новый заказ!</b>\n\n"
    
    # Добавляем информацию о пользователе (обязательно, так как требуется авторизация)
    if user_info:
        user_email = user_info.get("email", "Неизвестный")
        user_id = user_info.get("id", "N/A")
        message += f"👤 <b>Пользователь:</b> {user_email} (ID: {user_id})\n"
    else:
        message += f"👤 <b>Пользователь:</b> Неизвестный (ошибка получения данных)\n"
    
    message += f"📋 <b>Номер заказа:</b> {order_id}\n"
    message += f"📅 <b>Дата и время:</b> {formatted_date}\n"
    message += f"📦 <b>Всего товаров:</b> {total_items}\n\n"
    
    message += f"<b>Товары в заказе:</b>\n"
    message += "─" * 30 + "\n"
    
    total_price = 0.0
    for product_info in products_info:
        product_id = str(product_info.get("id", "N/A"))
        product_name = product_info.get("name", "Неизвестный товар")
        artist = product_info.get("artist", "Неизвестный исполнитель")
        price = float(product_info.get("price", 0.0))
        
        # Пробуем найти количество по разным форматам ID
        quantity = 1
        if quantities:
            # Пробуем найти по строковому ID
            quantity = quantities.get(product_id, quantities.get(int(product_id) if product_id.isdigit() else product_id, 1))
            # Если не найдено, пробуем найти по числовому ID
            if quantity == 1 and product_id.isdigit():
                quantity = quantities.get(int(product_id), 1)
        
        item_total = price * quantity
        total_price += item_total
        
        message += f"🎵 <b>{product_name}</b>\n"
        message += f"   Исполнитель: {artist}\n"
        message += f"   Цена: {price:.2f} ₽\n"
        message += f"   Количество: {quantity} шт.\n"
        message += f"   Итого: {item_total:.2f} ₽\n\n"
    
    message += "─" * 30 + "\n"
    message += f"💰 <b>Общая сумма:</b> {total_price:.2f} ₽\n"
    
    return message

def format_email_message(order_data: Dict, products_info: List[Dict], ai_praise: str = "", recommendations: List[Dict] = None, user_email: str = None, is_copy: bool = False) -> str:
    """
    Форматирует HTML-сообщение о заказе для отправки по email.
    """
    # Логирование для отладки
    print(f"📧 format_email_message вызвана:", flush=True)
    print(f"   - Рекомендаций получено: {len(recommendations) if recommendations else 0}", flush=True)
    if recommendations and len(recommendations) > 0:
        print(f"   - Первая рекомендация: {recommendations[0].get('name', 'N/A')}", flush=True)
    order_id = order_data.get("order_id", "N/A")
    created_at = order_data.get("created_at", "N/A")
    total_items = order_data.get("total_items", 0)
    quantities = order_data.get("quantities", {})
    
    # Форматируем дату
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%d.%m.%Y %H:%M:%S")
    except:
        formatted_date = created_at
    
    total_price = 0.0
    items_html = ""
    for product_info in products_info:
        product_id = str(product_info.get("id", "N/A"))
        product_name = product_info.get("name", "Неизвестный товар")
        artist = product_info.get("artist", "Неизвестный исполнитель")
        price = float(product_info.get("price", 0.0))
        
        quantity = 1
        if quantities:
            quantity = quantities.get(product_id, quantities.get(int(product_id) if product_id.isdigit() else product_id, 1))
            if quantity == 1 and product_id.isdigit():
                quantity = quantities.get(int(product_id), 1)
        
        item_total = price * quantity
        total_price += item_total
        
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{product_name}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{artist}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{price:.2f} ₽</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{quantity}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{item_total:.2f} ₽</td>
        </tr>
        """
    
    # Формируем HTML для мнения эксперта
    expert_opinion_html = ""
    if ai_praise:
        expert_opinion_html = f'<div class="ai-praise"><h3>🎵 Мнение музыкального эксперта:</h3><p>{ai_praise}</p></div>'
    
    # Формируем HTML для рекомендаций
    recommendations_html = ""
    print(f"🔍 Проверка рекомендаций для HTML:", flush=True)
    print(f"   - recommendations is None: {recommendations is None}", flush=True)
    print(f"   - recommendations type: {type(recommendations)}", flush=True)
    if recommendations:
        print(f"   - len(recommendations): {len(recommendations)}", flush=True)
    if recommendations and len(recommendations) > 0:
        print(f"✅ Формируем HTML для {len(recommendations)} рекомендаций", flush=True)
        rec_items = ""
        for idx, rec in enumerate(recommendations[:3], 1):  # Максимум 3 рекомендации
            rec_name = rec.get("name", rec.get("title", "Неизвестная пластинка"))
            rec_artist = rec.get("artist", rec.get("author", "Неизвестный исполнитель"))
            rec_reason = rec.get("reason", rec.get("description", ""))
            rec_id = rec.get("id", "")
            
            # Очищаем reason от лишних символов и ограничиваем длину
            if rec_reason:
                rec_reason = rec_reason.strip()
                if len(rec_reason) > 200:
                    rec_reason = rec_reason[:200] + "..."
            
            rec_items += f"""
            <div style="padding: 15px; margin: 10px 0; background: #ffffff; border-left: 4px solid #667eea; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="background: #667eea; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; margin-right: 10px;">{idx}</span>
                    <h4 style="margin: 0; color: #667eea; font-size: 16px;">{rec_name}</h4>
                </div>
                <p style="margin: 0 0 8px 34px; color: #666; font-size: 14px; font-weight: 500;">{rec_artist}</p>
                {f'<p style="margin: 8px 0 0 34px; color: #555; font-size: 13px; line-height: 1.5; font-style: italic;">{rec_reason}</p>' if rec_reason else ''}
            </div>
            """
        
        recommendations_html = f'''
        <div style="margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%); border-radius: 10px; border: 2px solid #667eea;">
            <h3 style="margin: 0 0 10px 0; color: #667eea; font-size: 20px;">💡 Рекомендации для вас:</h3>
            <p style="margin: 0 0 20px 0; color: #555; font-size: 14px;">На основе вашей покупки мы подобрали для вас персональные рекомендации:</p>
            {rec_items}
            <p style="margin: 15px 0 0 0; color: #888; font-size: 12px; font-style: italic;">Эти рекомендации подобраны специально для вас на основе вашего музыкального вкуса.</p>
        </div>
        '''
        print(f"✅ recommendations_html сформирован, длина: {len(recommendations_html)} символов", flush=True)
    else:
        print(f"⚠️  Рекомендации не добавлены в HTML (пустой список или None)", flush=True)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .order-info {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            .total {{ font-size: 20px; font-weight: bold; text-align: right; margin-top: 20px; }}
            .ai-praise {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 Спасибо за ваш заказ!</h1>
            </div>
            <div class="content">
                <div class="order-info">
                    <h2>Информация о заказе</h2>
                    <p><strong>Номер заказа:</strong> {order_id}</p>
                    <p><strong>Дата и время:</strong> {formatted_date}</p>
                    <p><strong>Всего товаров:</strong> {total_items}</p>
                    {f'<p><strong>Email заказчика:</strong> {user_email}</p>' if is_copy and user_email else ''}
                </div>
                
                {expert_opinion_html}
                {recommendations_html}
                
                <h3>Товары в заказе:</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Исполнитель</th>
                            <th style="text-align: right;">Цена</th>
                            <th style="text-align: center;">Кол-во</th>
                            <th style="text-align: right;">Итого</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div class="total">
                    <p>Общая сумма: <strong>{total_price:.2f} ₽</strong></p>
                </div>
                
                <div class="footer">
                    <p>Спасибо за покупку в Винил Шоп! 🎵</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/orders", tags=["Orders"])
def get_orders():
    """Получает список всех заказов."""
    return {"orders": orders_storage}

@app.post("/api/v1/orders", tags=["Orders"])
def create_order(
    request: OrderRequest,
    authorization: str = Header(..., alias="Authorization")
):
    """
    Создает новый заказ.
    Требуется авторизация (только для зарегистрированных пользователей).
    """
    order_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    # Вычисляем общее количество товаров
    total_items = 0
    if request.quantities:
        total_items = sum(request.quantities.values())
    else:
        total_items = len(request.product_ids)
    
    order = {
        "order_id": order_id,
        "product_ids": request.product_ids,
        "quantities": request.quantities,
        "total_items": total_items,
        "created_at": created_at,
        "status": "created"
    }
    
    orders_storage.append(order)
    
    # Получаем информацию о пользователе (обязательно, так как требуется авторизация)
    user_info = get_user_info(authorization, required=True)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить вашу авторизацию. Для оформления заказа необходимо войти в систему. Мы сохранили вашу корзину - просто войдите и попробуйте еще раз."
        )
    
    user_email = user_info.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email пользователя не найден в профиле."
        )
    
    # Получаем информацию о товарах для Telegram-уведомления
    products_info = []
    print(f"📦 Получение информации о {len(request.product_ids)} товарах из catalog service...", flush=True)
    
    # Пробуем получить все товары сразу для оптимизации
    all_products = None
    catalog_available = False
    try:
        # Сначала проверяем доступность catalog service
        health_url = f"{CATALOG_SERVICE_URL}/health"
        health_response = requests.get(health_url, timeout=2)
        if health_response.status_code == 200:
            catalog_available = True
            print(f"✅ Catalog service доступен на {CATALOG_SERVICE_URL}", flush=True)
        
        if catalog_available:
            all_products_url = f"{CATALOG_SERVICE_URL}/api/v1/products"
            all_products_response = requests.get(all_products_url, timeout=5)
            if all_products_response.status_code == 200:
                all_products_data = all_products_response.json()
                all_products = {str(p.get("id")): p for p in all_products_data.get("products", [])}
                print(f"✅ Загружено {len(all_products)} товаров из catalog", flush=True)
    except requests.exceptions.ConnectionError:
        print(f"❌ Catalog service недоступен на {CATALOG_SERVICE_URL}", flush=True)
        print(f"   Убедитесь, что catalog service запущен на порту 8000", flush=True)
        catalog_available = False
    except Exception as e:
        print(f"⚠️  Не удалось загрузить все товары сразу: {e}", flush=True)
        catalog_available = False
    
    # Получаем информацию о каждом товаре
    for product_id in request.product_ids:
        product_info = None
        
        # Сначала пробуем найти в уже загруженных товарах
        if all_products and str(product_id) in all_products:
            product_info = all_products[str(product_id)]
            print(f"✅ Товар {product_id} найден в кэше: {product_info.get('name', 'N/A')}", flush=True)
        else:
            # Если не найдено, делаем отдельный запрос
            product_info = get_product_info(product_id)
        
        if product_info:
            # Преобразуем ID в строку для совместимости
            product_info["id"] = str(product_info.get("id", product_id))
            products_info.append(product_info)
        else:
            # Если не удалось получить информацию, создаем минимальную запись
            if not catalog_available:
                print(f"❌ Catalog service недоступен - не удалось получить информацию о товаре {product_id}", flush=True)
            else:
                print(f"⚠️  Товар {product_id} не найден в catalog, используем заглушку", flush=True)
            products_info.append({
                "id": str(product_id),
                "name": f"Товар #{product_id}",
                "artist": "Неизвестный исполнитель",
                "price": 0.0
            })
    
    # Генерируем мнение музыкального эксперта о выборе пластинок
    ai_praise = ""
    try:
        print(f"🎵 Генерация мнения музыкального эксперта...", flush=True)
        ai_praise = generate_ai_praise(products_info)
        if ai_praise:
            print(f"✅ Мнение эксперта сгенерировано", flush=True)
    except Exception as e:
        print(f"⚠️  Ошибка при генерации мнения эксперта: {e}", flush=True)
    
    # Генерируем рекомендации на основе покупки
    recommendations = []
    try:
        print(f"💡 Генерация рекомендаций на основе покупки...", flush=True)
        recommendations = generate_recommendations(products_info)
        if recommendations and len(recommendations) > 0:
            print(f"✅ Сгенерировано {len(recommendations)} рекомендаций", flush=True)
        else:
            print(f"⚠️  Рекомендации не были сгенерированы (пустой список)", flush=True)
    except Exception as e:
        print(f"⚠️  Ошибка при генерации рекомендаций: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    # Отправляем email пользователю и дубликат на наш адрес
    try:
        print(f"📧 Подготовка отправки email на {user_email}...", flush=True)
        print(f"📊 Статистика перед отправкой email:", flush=True)
        print(f"   - Мнение эксперта: {'✅' if ai_praise else '❌'}", flush=True)
        print(f"   - Рекомендаций: {len(recommendations) if recommendations else 0}", flush=True)
        if recommendations:
            print(f"   - Первая рекомендация: {recommendations[0].get('name', 'N/A') if len(recommendations) > 0 else 'N/A'}", flush=True)
        email_subject = f"Ваш заказ №{order_id} - Винил Шоп"
        email_body = format_email_message(order, products_info, ai_praise, recommendations)
        print(f"📧 Email body сгенерирован, длина: {len(email_body)} символов", flush=True)
        
        # Отправляем письмо пользователю
        send_email(user_email, email_subject, email_body)
        
        # Отправляем дубликат на наш адрес (если указан и отличается от адреса пользователя)
        if EMAIL_COPY_TO:
            if EMAIL_COPY_TO != user_email:
                copy_subject = f"[ДУБЛИКАТ] Заказ №{order_id} от {user_email} - Винил Шоп"
                print(f"📧 Отправка дубликата письма на {EMAIL_COPY_TO}...", flush=True)
                # Генерируем отдельное письмо для дубликата с информацией о заказчике
                copy_email_body = format_email_message(order, products_info, ai_praise, recommendations, user_email=user_email, is_copy=True)
                send_email(EMAIL_COPY_TO, copy_subject, copy_email_body)
            else:
                print(f"ℹ️  EMAIL_COPY_TO совпадает с адресом пользователя, дубликат не отправляется", flush=True)
    except Exception as e:
        print(f"⚠️  Ошибка при отправке email: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    # Отправляем уведомление в Telegram
    try:
        print(f"📤 Подготовка отправки уведомления в Telegram для заказа {order_id}...", flush=True)
        # Добавляем предупреждение, если catalog service недоступен
        if not catalog_available:
            print(f"⚠️  ВНИМАНИЕ: Catalog service недоступен! Информация о товарах может быть неполной.", flush=True)
        telegram_message = format_order_message(order, products_info, user_info)
        send_telegram_message(telegram_message)
    except Exception as e:
        print(f"⚠️  Ошибка при подготовке/отправке Telegram-уведомления: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    return OrderResponse(
        order_id=order_id,
        message="Order created successfully",
        created_at=created_at,
        product_ids=request.product_ids,
        quantities=request.quantities,
        total_items=total_items
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010)  # Изменено на 8010 согласно config.env