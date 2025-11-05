"""
Комплексный тест качества генерации описаний
Проверяет, что описания генерируются корректно для разных виниловых пластинок
"""
import asyncio
import httpx
import json
import time
import re

# Тестовые виниловые пластинки - классический рок
TEST_RECORDS_ROCK = [
    {
        "id": 1,  # Abbey Road
        "name": "Abbey Road",
        "artist": "The Beatles",
        "forbidden_words": ["поп", "электроника", "хип-хоп"]
    },
    {
        "id": 2,  # The Dark Side of the Moon
        "name": "The Dark Side of the Moon",
        "artist": "Pink Floyd",
        "forbidden_words": ["поп", "электроника", "хип-хоп"]
    },
    {
        "id": 3,  # Led Zeppelin IV
        "name": "Led Zeppelin IV",
        "artist": "Led Zeppelin",
        "forbidden_words": ["поп", "электроника", "хип-хоп"]
    }
]

# Виниловая пластинка The Beatles (для проверки, что описания корректны)
TEST_RECORDS_BEATLES = [
    {
        "id": 1,  # Abbey Road
        "name": "Abbey Road",
        "artist": "The Beatles",
        "required_words": ["beatles", "битлз"]  # Должны упоминаться
    }
]

async def test_single_record_description(product_id, expected_name, expected_artist, forbidden_words=None, required_words=None):
    """Тестирует генерацию описания для одной виниловой пластинки"""
    base_url = "http://127.0.0.1:8004"
    catalog_url = "http://127.0.0.1:8000"
    
    print(f"\n{'='*60}")
    print(f"Тест виниловой пластинки: {expected_name} (ID={product_id})")
    print(f"Исполнитель: {expected_artist}")
    print(f"{'='*60}")
    
    # Шаг 1: Проверяем данные виниловой пластинки в каталоге
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            catalog_response = await client.get(f"{catalog_url}/api/v1/products/{product_id}")
            
            if catalog_response.status_code != 200:
                print(f"❌ Виниловая пластинка с ID {product_id} не найдена в каталоге!")
                return False
            
            catalog_data = catalog_response.json()
            actual_name = catalog_data.get('name', '')
            actual_artist = catalog_data.get('artist', '')
            
            print(f"✅ Данные из каталога:")
            print(f"   Название: {actual_name}")
            print(f"   Исполнитель: {actual_artist}")
            print(f"   Текущее описание: {catalog_data.get('description', 'отсутствует')[:100]}")
            
            # Проверяем соответствие
            if expected_name.lower() not in actual_name.lower():
                print(f"⚠️  Предупреждение: название в каталоге '{actual_name}' не совпадает с ожидаемым '{expected_name}'")
            
    except Exception as e:
        print(f"❌ Ошибка получения данных из каталога: {e}")
        return False
    
    # Шаг 2: Генерируем описание
    print(f"\n[Шаг 2] Генерируем описание...")
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/recommendations/generate-description/{product_id}"
            )
            
            elapsed = time.time() - start_time
            print(f"   Время генерации: {elapsed:.2f} секунд")
            
            if response.status_code != 200:
                print(f"❌ Ошибка HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Детали: {error_data.get('detail', error_data)}")
                except:
                    print(f"   Ответ: {response.text[:200]}")
                return False
            
            data = response.json()
            generated_description = data.get('generated_description', '')
            
            if not generated_description:
                print("❌ Описание пустое!")
                return False
            
            print(f"✅ Описание сгенерировано ({len(generated_description)} символов):")
            print(f"   {generated_description[:200]}...")
            
            # Шаг 3: Проверяем качество описания
            print(f"\n[Шаг 3] Проверка качества описания...")
            issues = []
            warnings = []
            
            # Проверка на запрещенные слова (для виниловых пластинок классического рока)
            if forbidden_words:
                description_lower = generated_description.lower()
                found_forbidden = []
                for word in forbidden_words:
                    if word.lower() in description_lower:
                        found_forbidden.append(word)
                
                if found_forbidden:
                    issues.append(f"❌ Найдены запрещенные слова: {', '.join(found_forbidden)}")
                else:
                    print(f"✅ Запрещенные слова не найдены")
            
            # Проверка на требуемые слова (для виниловых пластинок The Beatles)
            if required_words:
                description_lower = generated_description.lower()
                found_required = []
                missing_required = []
                for word in required_words:
                    if word.lower() in description_lower:
                        found_required.append(word)
                    else:
                        missing_required.append(word)
                
                if missing_required:
                    warnings.append(f"⚠️  Не найдены ожидаемые слова: {', '.join(missing_required)}")
                else:
                    print(f"✅ Все требуемые слова найдены: {', '.join(found_required)}")
            
            # Проверка длины
            if len(generated_description) < 50:
                warnings.append(f"⚠️  Описание слишком короткое ({len(generated_description)} символов)")
            elif len(generated_description) > 500:
                warnings.append(f"⚠️  Описание слишком длинное ({len(generated_description)} символов)")
            else:
                print(f"✅ Длина описания в норме ({len(generated_description)} символов)")
            
            # Проверка на общие фразы (клише)
            cliche_phrases = [
                "погрузитесь в магический мир музыки",
                "невероятный музыкальный опыт"
            ]
            description_lower = generated_description.lower()
            for phrase in cliche_phrases:
                if phrase in description_lower:
                    warnings.append(f"⚠️  Найдена общая фраза: '{phrase}'")
            
            # Выводим результаты
            if issues:
                print("\n❌ ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
                for issue in issues:
                    print(f"   {issue}")
            
            if warnings:
                print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
                for warning in warnings:
                    print(f"   {warning}")
            
            if not issues and not warnings:
                print("\n✅ Все проверки пройдены!")
                return True
            elif issues:
                return False
            else:
                return True  # Есть предупреждения, но не критично
                
    except httpx.TimeoutException:
        print(f"❌ Таймаут при генерации описания")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        import traceback
        print(f"   Детали: {traceback.format_exc()[:300]}")
        return False

async def test_all_records():
    """Тестирует генерацию описаний для всех тестовых виниловых пластинок"""
    print("=" * 60)
    print("КОМПЛЕКСНЫЙ ТЕСТ КАЧЕСТВА ГЕНЕРАЦИИ ОПИСАНИЙ")
    print("=" * 60)
    
    # Проверка доступности сервисов
    print("\n[Шаг 0] Проверка доступности сервисов...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            recommender_resp = await client.get("http://127.0.0.1:8004/health")
            catalog_resp = await client.get("http://127.0.0.1:8000/health")
            
            if recommender_resp.status_code == 200 and catalog_resp.status_code == 200:
                print("✅ Все сервисы доступны")
            else:
                print("❌ Некоторые сервисы недоступны")
                print(f"   Recommender: {recommender_resp.status_code}")
                print(f"   Catalog: {catalog_resp.status_code}")
                return
    except Exception as e:
        print(f"❌ Ошибка проверки сервисов: {e}")
        print("   Запустите сервисы: python start_services_final.py")
        return
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Тестируем виниловые пластинки классического рока
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Виниловые пластинки классического рока (проверка корректности)")
    print("=" * 60)
    
    for record in TEST_RECORDS_ROCK:
        results["total"] += 1
        passed = await test_single_record_description(
            product_id=record["id"],
            expected_name=record["name"],
            expected_artist=record["artist"],
            forbidden_words=record["forbidden_words"]
        )
        
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Небольшая пауза между запросами
        await asyncio.sleep(2)
    
    # Тестируем виниловую пластинку The Beatles
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Виниловая пластинка The Beatles (проверка корректности)")
    print("=" * 60)
    
    for record in TEST_RECORDS_BEATLES:
        results["total"] += 1
        passed = await test_single_record_description(
            product_id=record["id"],
            expected_name=record["name"],
            expected_artist=record["artist"],
            required_words=record["required_words"]
        )
        
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        await asyncio.sleep(2)
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    print(f"Всего тестов: {results['total']}")
    print(f"✅ Пройдено: {results['passed']}")
    print(f"❌ Провалено: {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"📊 Успешность: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print("\n🎉 Все тесты пройдены!")
    else:
        print(f"\n⚠️  {results['failed']} тест(ов) провалено. Проверьте логи выше.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_records())

