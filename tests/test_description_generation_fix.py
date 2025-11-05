"""
Тестовый скрипт для проверки генерации описаний виниловых пластинок
Проверяет, что описания генерируются для правильных пластинок
"""
import asyncio
import httpx
import json

async def test_description_generation():
    """Тестирует генерацию описаний для разных виниловых пластинок"""
    
    base_url = "http://127.0.0.1:8004"
    catalog_url = "http://127.0.0.1:8000"
    
    # Тестовые виниловые пластинки
    test_records = [
        {"id": 1, "name": "Abbey Road", "artist": "The Beatles"},
        {"id": 2, "name": "The Dark Side of the Moon", "artist": "Pink Floyd"},
        {"id": 3, "name": "Led Zeppelin IV", "artist": "Led Zeppelin"},
    ]
    
    print("=" * 80)
    print("ТЕСТ ГЕНЕРАЦИИ ОПИСАНИЙ ВИНИЛОВЫХ ПЛАСТИНОК")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for record in test_records:
            record_id = record["id"]
            expected_name = record["name"]
            expected_artist = record["artist"]
            
            print(f"\n{'=' * 80}")
            print(f"ТЕСТ {record_id}: {expected_name} от {expected_artist}")
            print(f"{'=' * 80}")
            
            try:
                # Шаг 1: Проверяем, что пластинка существует в каталоге
                print(f"\n[Шаг 1] Проверяем пластинку в каталоге...")
                catalog_response = await client.get(f"{catalog_url}/api/v1/products/{record_id}")
                
                if catalog_response.status_code == 404:
                    print(f"❌ Виниловая пластинка с ID {record_id} не найдена в каталоге!")
                    continue
                
                catalog_response.raise_for_status()
                record_data = catalog_response.json()
                actual_name = record_data.get('name', '')
                actual_artist = record_data.get('artist', '')
                if isinstance(actual_artist, dict):
                    actual_artist = actual_artist.get('name', '')
                
                print(f"✅ Пластинка найдена: '{actual_name}' от '{actual_artist}'")
                
                if actual_name != expected_name:
                    print(f"⚠️  ВНИМАНИЕ: Название не совпадает! Ожидалось: '{expected_name}', получено: '{actual_name}'")
                
                # Шаг 2: Генерируем описание
                print(f"\n[Шаг 2] Генерируем описание...")
                gen_response = await client.post(
                    f"{base_url}/api/v1/recommendations/generate-description/{record_id}",
                    headers={"Content-Type": "application/json"}
                )
                
                if gen_response.status_code != 200:
                    error_text = await gen_response.aread()
                    print(f"❌ Ошибка генерации: {gen_response.status_code}")
                    print(f"   Ответ: {error_text.decode()}")
                    continue
                
                gen_data = gen_response.json()
                generated_description = gen_data.get('generated_description', '')
                
                print(f"✅ Описание сгенерировано ({len(generated_description)} символов)")
                print(f"\n📝 Описание:")
                print(f"   {generated_description}")
                
                # Шаг 3: Проверяем качество описания
                print(f"\n[Шаг 3] Проверка качества описания...")
                
                desc_lower = generated_description.lower()
                record_name_lower = actual_name.lower()
                
                # Проверки для пластинок классического рока
                if "beatles" not in record_name_lower and "the beatles" not in record_name_lower:
                    forbidden_terms = [
                        "поп-музыка", "электронная музыка", "хип-хоп"
                    ]
                    
                    found_forbidden = []
                    for term in forbidden_terms:
                        if term in desc_lower:
                            found_forbidden.append(term)
                    
                    if found_forbidden:
                        print(f"⚠️  Найдены нежелательные термины: {', '.join(found_forbidden)}")
                    else:
                        print(f"✅ Нежелательные термины не найдены")
                    
                    # Проверяем, упоминается ли правильное название пластинки
                    if record_name_lower.split()[0] in desc_lower or record_name_lower[:20] in desc_lower:
                        print(f"✅ Описание содержит правильное название пластинки")
                    else:
                        print(f"⚠️  ВНИМАНИЕ: Описание может не содержать правильное название пластинки")
                else:
                    print(f"✅ Это пластинка The Beatles - проверка пропущена")
                
                # Проверяем длину
                if 150 <= len(generated_description) <= 400:
                    print(f"✅ Длина описания в норме")
                else:
                    print(f"⚠️  Длина описания необычная: {len(generated_description)} символов")
                
                # Проверяем, что описание не пустое
                if generated_description.strip():
                    print(f"✅ Описание не пустое")
                else:
                    print(f"❌ ОШИБКА: Описание пустое!")
                
            except Exception as e:
                print(f"❌ ОШИБКА: {type(e).__name__}: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(test_description_generation())

